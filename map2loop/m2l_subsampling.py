import geopandas as gpd
import shapely
import matplotlib.pyplot as plt
import sys
import copy
import fiona
import shapely
from shapely.geometry import shape, mapping, LineString, Polygon, MultiLineString, MultiPolygon, MultiPoint
from shapely.geometry.polygon import LinearRing
import heapq

def plot (dataframe, column):
	plot=dataframe.plot(column=column,figsize=(5,5), edgecolor='#000000',linewidth=0.2, cmap='Set2')
	plot = plot.figure; plot.tight_layout()
	#plot.savefig('ygsbplot.png')
	
def upscale_by (dataframe, column):
	group = dataframe.groupby(column)
	group.head()
	plot=dataframe.plot(column=column,figsize=(5,5), edgecolor='#000000',linewidth=0.2, legend=True, cmap='Set2')

def vector_aggregate (dataframe, column, geometry_column, output_file):
	group = dataframe.dissolve(by=column)
	group.head()
	group.plot(figsize=(5,5), edgecolor='#000000', linewidth=0.2, legend=True, cmap='Set2')
	
	# create a dictionary
	group = {}

	for i in range(len(dataframe)):
		unit_name_id = dataframe.at[i, column]
		ygsb_geometry = dataframe.at[i, geometry_column]
		# if the feature's state doesn't yet exist, create it and assign a list
		if unit_name_id not in unit_name:
			unit_name[unit_name_id] = []
		# append the feature to the list of features
		unit_name[unit_name_id].append(ygsb_geometry)

	# create a geopandas geodataframe, with columns for state and geometry
	group_dissolved = gpd.GeoDataFrame(columns=[column, geometry_column], crs=dataframe.crs)

	#iterate your dictionary
	for group, dataframe_list in group.items():
		#create a geoseries from the list of features
		geom = gpd.GeoSeries(dataframe_list)
		#use unary_union to join them, thus returning polygon or multi-polygon
		geom = geom.unary_union
    
		#set your state and geometry values
		group_dissolved.set_value(group, column, group)
		group_dissolved.set_value(group, geometry_column, geom)

	group_dissolved.head()
	group_dissolved.plot(cmap='Set2', edgecolor='#000000', linewidth=0.2, figsize=(5, 5), legend=True)
	group_dissolved.area
	group_dissolved.to_file(output_file)
	
debug = True
self_intersections_fixed = 0

def vector_simplify (inFile, outFile, threshold):
	threshold = float(threshold)
	with fiona.open(inFile, 'r') as input:
		meta = input.meta
		dictJunctions = {}
		simplifyObj = GeomSimplify()
		simplifyObj.find_all_junctions(inFile, dictJunctions) 
		simplify = GeomSimplify(dictJunctions)
		invalid_geoms_count = 0

		with fiona.open(outFile, 'w', **meta) as output:
			for myGeom in input:
				myShape = shape(myGeom['geometry'])
				simplifiedShapes =[]
				if isinstance(myShape, LineString):
					line = myShape
					simplifiedShapes = [simplify.simplify_line_topology(line, threshold)]
				elif isinstance(myShape, MultiLineString):
					mline = myShape
					simplifiedShapes = [simplify.simplify_multiline_topology(mline, threshold)]
				elif isinstance(myShape, Polygon):
					polygon = myShape
					simplifiedShapes = [simplify.simplify_polygon_topology(polygon, threshold)]
				elif isinstance(myShape, MultiPolygon):
					mpolygon = myShape
					simplifiedShapes = [simplify.simplify_multipolygon_topology(mpolygon, threshold)]
				else:
					raise ValueError('Unhandled geometry type: ' + repr(myShape.type))
				check_invalid_geometry(simplifiedShapes)
				for simpleShape in simplifiedShapes:
					if simpleShape is not None:
						output.write({'geometry':mapping(simpleShape), 'properties': myGeom['properties']})

	if debug:
		with open('debug_junctions.txt', 'w') as output:
			for key in dictJunctions:
				output.write(str(key))
	test=gpd.read_file(outFile)
	plot=test.plot(figsize=(5,5), edgecolor='#000000',linewidth=0.2, cmap='Set2')
	plot = plot.figure; plot.tight_layout()
	
def check_invalid_geometry(shapeList):
	checkedShapeList = []
	for shape in shapeList:
		if isinstance(shape, Polygon):
			shape = fix_self_intersections_polygon(shape)
		elif isinstance(shape, MultiPolygon):
			shape = fix_self_intersections_mpolygon(shape)
		checkedShapeList.append(shape)
	return checkedShapeList

def fix_self_intersections_polygon(polygon):
	global self_intersections_fixed
	if validate:
		if not isinstance(polygon, Polygon):
			raise ValueError('Non-Polygon passed to fix_self_intersections_polygon: ' + repr(polygon.type))
	shape = polygon
	if not polygon.is_valid:
		shape = polygon.buffer(0)
		self_intersections_fixed += 1
	return shape

def fix_self_intersections_mpolygon(mpolygon):
	if validate:
		if not isinstance(mpolygon, MultiPolygon):
			raise ValueError('Non-MultiPolygon passed to fix_self_intersections_mpolygon: ' + repr(mpolygon.type))
	checked_polygons = []
	for polygon in mpolygon.geoms:
		if not polygon.is_valid:
			cleaned_shape = fix_self_intersections_polygon(polygon)
			for p in cleaned_shape.geoms:
				checked_polygons.append(p)
		else:
			checked_polygons.append(polygon)
	return MultiPolygon(checked_polygons)

validate = False
if validate:
	dictArcThresholdCounts = {}

class GeomSimplify(object):
	# default quantization factor is 1
	quantitizationFactor = (1,1)
	def __init__(self, dictJunctions = None):
		self.dictJunctions = dictJunctions
		self.dictSimpleArcs = {}	# Stores simplified arcs from bordering polygons
	def create_ring_from_arcs(self, arcList):
		ringPoints = []
		for arc in arcList:
			arcPoints = arc.coords;
			if len(ringPoints) == 0:
				ringPoints.extend(arcPoints)
			else:
				if validate:

					last = self.quantitize(ringPoints[-1])
					first = self.quantitize(arcPoints[0])
					if last[0] != first[0] or last[1] != first[1]:
						raise ValueError('arcList does not form a ring.')
				ringPoints.extend(arcPoints[1:])
		if len(ringPoints) < 3:
			return None
		return LinearRing(ringPoints)

	def simplify_line_topology(self, line, threshold):
		if not self.dictJunctions:
			return self.simplify_line(line, threshold)
		lineList = self.cut_line_by_junctions(line, self.dictJunctions)
		simplifiedLines = []
		for line in lineList:
			simplifiedLines.append(self.simplify_line(line, threshold))
		if len(simplifiedLines) == 1:
			return simplifiedLines[0]
		else:
			return MultiLineString(simplifiedLines)

	def simplify_line(self, line, threshold):
		triangleArray = []
		for index, point in enumerate(line.coords[1:-1]):
			triangleArray.append(TriangleCalculator(point, index))
		startIndex = 0
		endIndex = len(line.coords)-1
		startTriangle = TriangleCalculator(line.coords[startIndex], startIndex)
		endTriangle = TriangleCalculator(line.coords[endIndex], endIndex)

		for index, triangle in enumerate(triangleArray):
			prevIndex = index - 1
			nextIndex = index + 1

			if prevIndex >= 0:
				triangle.prevTriangle = triangleArray[prevIndex]
			else:
				triangle.prevTriangle = startTriangle

			if nextIndex < len(triangleArray):
				triangle.nextTriangle = triangleArray[nextIndex]
			else:
				triangle.nextTriangle = endTriangle
		heapq.heapify(triangleArray)
		while len(triangleArray) > 0:
			if triangleArray[0].calcArea() >= threshold:
				break
			else:
				prev = triangleArray[0].prevTriangle
				next = triangleArray[0].nextTriangle
				prev.nextTriangle = next
				next.prevTriangle = prev
				heapq.heappop(triangleArray)
				heapq.heapify(triangleArray)
		indexList = []
		for triangle in triangleArray:
			indexList.append(triangle.ringIndex + 1)
		indexList.append(startTriangle.ringIndex)
		indexList.append(endTriangle.ringIndex)
		indexList.sort()
		simpleLine = []
		for index in indexList:
			simpleLine.append(line.coords[index])
		simpleLine = LineString(simpleLine)
		return simpleLine
	
	def simplify_multiline_topology(self, mline, threshold):
		if not self.dictJunctions:
			return self.simplify_multiline(mline, threshold)
		mlineArray = self.cut_mline_by_junctions(mline, self.dictJunctions)
		simplifiedShapes = []
		for mline in mlineArray:
			simplifiedShapes.append(self.simplify_multiline(mline, threshold))
		linesList = []
		for mline in simplifiedShapes:
			for line in mline.geoms:
				linesList.append(line)
		return MultiLineString(linesList)
	
	def simplify_multiline(self, mline, threshold):
		lineList = mline.geoms
		simpleLineList = []
		for line in lineList:
			simpleLine = self.simplify_line(line, threshold)
		  
			if simpleLine:
				simpleLineList.append(simpleLine)
		if not simpleLineList:
			return None
		return MultiLineString(simpleLineList)
		
	def simplify_polygon_topology(self, poly, threshold):
		if self.dictJunctions:
			cutPolygonTuple = self.cut_polygon_by_junctions(poly, self.dictJunctions)
			arcList = cutPolygonTuple[0]
			originalPolygon = cutPolygonTuple[1]

			if arcList is None: # No junctions on polygon exterior ring
				simpleExtRing = self.simplify_ring(poly.exterior, threshold, self.dictJunctions)
			else:
				simpleArcList = []
				num_junctions = len(arcList)
				for arc in arcList:
					simpleArc = None
					myThreshold = threshold
					simpleArc = self.simplify_line(arc, myThreshold)
					simpleArcList.append(simpleArc)

				# Stitch the arcs back together into a ring
				simpleExtRing = self.create_ring_from_arcs(simpleArcList)
		else:
			# Get exterior ring
			simpleExtRing = self.simplify_ring(poly.exterior, threshold, self.dictJunctions)

		# If the exterior ring was removed by simplification, return None
		if simpleExtRing is None:
			return None

		simpleIntRings = []
		for ring in poly.interiors:
			simpleRing = self.simplify_ring(ring, threshold, self.dictJunctions)
			if simpleRing is not None:
				simpleIntRings.append(simpleRing)
		return shapely.geometry.Polygon(simpleExtRing, simpleIntRings)

	def simplify_multipolygon_topology(self, mpoly, threshold):
		# break multipolygon into polys
		polyList = mpoly.geoms
		simplePolyList = []

		# call simplify_polygon() on each
		for poly in polyList:
			simplePoly = self.simplify_polygon_topology(poly, threshold)
			#if not none append to list
			if simplePoly:
				simplePolyList.append(simplePoly)

		# check that polygon count > 0, otherwise return None
		if not simplePolyList:
			return None

		# put back into multipolygon
		return MultiPolygon(simplePolyList)

	def simplify_ring(self, ring, threshold, dictJunctions = None, minimumPoints = 2):
		# A ring must not have any junctions on it!
		if validate and dictJunctions:
			for point in ring.coords:
				quant_point = self.quantitize(point)
				if quant_point in dictJunctions:
					raise ValueError('Ring has junctions on it')

		# Build list of TriangleCalculators
		triangleRing = []
		## each triangle contains an index and a point (x,y)
		## because rings have a point on top of a point
		## we are skipping the last point by using slice notation[:-1]
		## *i.e. 'a[:-1]' # everything except the last item*
		for index, point in enumerate(ring.coords[:-1]):
			triangleRing.append(TriangleCalculator(point, index))

		# Hook up triangles with next and prev references (doubly-linked list)
		for index, triangle in enumerate(triangleRing):
			# set prevIndex to be the adjacent point to index
			# these steps are necessary for dealing with
			# closed rings
			prevIndex = index - 1
			if prevIndex < 0:
				# if prevIndex is less than 0, then it means index = 0, and
				# the prevIndex is set to last value in the index
				# (i.e. adjacent to index[0])
				prevIndex = len(triangleRing) - 1
			# set nextIndex adjacent to index
			nextIndex = index + 1
			if nextIndex == len(triangleRing):
				# if nextIndex is equivalent to the length of the array
				# set nextIndex to 0
				nextIndex = 0
			triangle.prevTriangle = triangleRing[prevIndex]
			triangle.nextTriangle = triangleRing[nextIndex]

		# Build a min-heap from the TriangleCalculator list
		heapq.heapify(triangleRing)

		# Simplify
		while len(triangleRing) > minimumPoints:
			# if the smallest triangle is greater than the threshold, we can stop
			# i.e. loop to point where the heap head is >= threshold

			if triangleRing[0].calcArea() >= threshold:
				break
			else:
				prev = triangleRing[0].prevTriangle
				next = triangleRing[0].nextTriangle
				prev.nextTriangle = next
				next.prevTriangle = prev
				heapq.heappop(triangleRing)

		# Handle case where we've removed too many points for the ring to be a polygon
		if len(triangleRing) < 3:
			return None

		# Create an list of indices from the triangleRing heap
		indexList = []
		for triangle in triangleRing:
			indexList.append(triangle.ringIndex)

		# Sort the index list
		indexList.sort()

		# Create a new simplified ring
		simpleRing = []
		for index in indexList:
			simpleRing.append(ring.coords[index])

		# Convert list into LinearRing
		simpleRing = LinearRing(simpleRing)
		return simpleRing

	def rotate_ring(ring, index):
		# Validate index
		if index < 0 or index > len(ring.coords) - 2:
			raise ValueError('Invalid index in rotate_ring: ' + repr(index))

		points = []
		for point in ring.coords[index:-1]:
			points.append(point)
		for point in ring.coords[:index]:
			points.append(point)

		newRing = LinearRing(points)

		#Validate
		if len(newRing.coords) != len(ring.coords):
			raise ValueError('Failed to rotate ring.')
		return newRing

	def set_quantitization_factor(self, quantValue):
		self.quantitizationFactor = (quantValue, quantValue)

	def quantitize(self, point):
		# the default quantization factor is 1
		# Divide by quantitiztion factor, round(int), multiply by quantitization factor
		x_quantitized = int(round(point[0]/self.quantitizationFactor[0])) * self.quantitizationFactor[0]
		y_quantitized = int(round(point[1]/self.quantitizationFactor[1])) * self.quantitizationFactor[1]

		return (x_quantitized,y_quantitized)

	def __append_junctions(self, dictJunctions, dictNeighbors, pointsList):
		if validate:
			dictCheck = {}

		# updates dictJunctions & dictNeighbors
		for index, point in enumerate(pointsList):
			quant_point = self.quantitize(point)

			# Check that no points on the points list are quantitized to the same value. If they are, you may need to fix the
			# data or lower the quantitization factor
			if validate:
				if quant_point in dictCheck:
					raise ValueError('Two points in the same shape quantitized to the same value - you may need to lower the quantitization factor: ' + repr(quant_point) + '.  Points: ' + repr(point) + ', ' + repr(dictCheck[quant_point]))
				dictCheck[quant_point] = point

			quant_neighbors = []
			# append the previous neighbor
			if index - 1 > 0:
				quant_neighbors.append(self.quantitize(pointsList[index - 1]))
			# append the next neighbor
			if index + 1 < len(pointsList):
				quant_neighbors.append(self.quantitize(pointsList[index + 1]))

			# check if point is in dictNeighbors, if it is
			# check if the neighbors are equivalent to what
			# is already in there, if not equiv. append to
			# dictJunctions

			if quant_point in dictNeighbors:
				# check if neighbors are equivalent
				if set(dictNeighbors[quant_point]) != set(quant_neighbors):
					dictJunctions[quant_point] = 1
			else:
				# Otherwise, add to neighbors
				dictNeighbors[quant_point] = quant_neighbors

	def find_all_junctions(self, inFile, dictJunctions):
		dictNeighbors = {}

		# loop over each
		with fiona.open(inFile, 'r') as input:

			# read shapely geometries from file
			for myGeom in input:
				myShape = shape(myGeom['geometry'])
				if isinstance(myShape, LineString):
					self.append_junctions_line(myShape, dictJunctions, dictNeighbors)
				elif isinstance(myShape, MultiLineString):
					self.append_junctions_mline(myShape, dictJunctions, dictNeighbors)
				elif isinstance(myShape, Polygon):
					self.append_junctions_polygon(myShape, dictJunctions, dictNeighbors)
				elif isinstance(myShape, MultiPolygon):
					self.append_junctions_mpolygon(myShape, dictJunctions, dictNeighbors)
				else:
					raise ValueError('Unhandled geometry type: ' + repr(myShape.type))

	def append_junctions_line(self, myShape, dictJunctions, dictNeighbors):
		pointsLineList = list(myShape.coords)
		self.__append_junctions(dictJunctions, dictNeighbors, pointsLineList)

	def append_junctions_mline(self, myShape, dictJunctions, dictNeighbors):
		for line in myShape.geoms:
			self.append_junctions_line(line, dictJunctions, dictNeighbors)
	def append_junctions_polygon(self, myShape, dictJunctions, dictNeighbors):
		if validate:
			if not isinstance(myShape, Polygon):
				raise ValueError('Non-Polygon passed to append_junctions_polygon: ' + repr(myShape.type))
		pointsList = list(myShape.exterior.coords[:-1])
		self.__append_junctions(dictJunctions, dictNeighbors, pointsList)

		# Validate that interior rings have no junctions
		if validate:
			countJunctions = len(dictJunctions)
			for ring in myShape.interiors:
				self.__append_junctions(dictJunctions, dictNeighbors, list(ring.coords[:-1]))
				if len(dictJunctions) != countJunctions:
					raise ValueError('Junction found on interior ring')

	def append_junctions_mpolygon(self, myShape, dictJunctions, dictNeighbors):
		for polygon in myShape.geoms:
			self.append_junctions_polygon(polygon, dictJunctions, dictNeighbors)

	def cut_line_by_junctions(self, myShape, dictJunctions):
		arcs = []
		arc = []
		pointsLineList = list(myShape.coords)

		# split lines into arcs by junctions
		for point in pointsLineList:
			quant_pt = self.quantitize(point)
			arc.append(point)
			length_of_arc = len(arc)
			if quant_pt in dictJunctions and length_of_arc >= 2:

				arcs.append(arc)
				arc = [point]
		if len(arc) > 1:
			arcs.append(arc)
		arcsLine = [LineString(ar) for ar in arcs]
		return arcsLine

	def cut_mline_by_junctions(self, myShape, dictJunctions):
		lineList = myShape.geoms
		junctionedLines = []
		multiJunctionedLines = []
		for line in lineList:
			junctionedLines.append(self.cut_line_by_junctions(line, dictJunctions))
			
		for cut_mline in junctionedLines:
			multiJunctionedLines.append(MultiLineString(cut_mline))
		return multiJunctionedLines

	def cut_ring_by_junctions(self, ring, dictJunctions):
		#Verify a ring was passed to function
		if validate:
			if ring.coords[0] != ring.coords[-1]:
				raise ValueError('Invalid ring passed to cut_ring_by_junctions: ' + repr(ring.coords))
		# Identify junction points
		junctionPointIndices = []
		for index, point in enumerate(ring.coords[:-1]):
			quant_pt = self.quantitize(point)
			if quant_pt in dictJunctions:
				junctionPointIndices.append(index)
		# If there are no junctions on ring just return None
		if len(junctionPointIndices) == 0:
			return None
		arcsList = self.cut_line_by_junctions(ring, dictJunctions)
		return arcsList

	def cut_polygon_by_junctions(self, myShape, dictJunctions):
		if validate:
			if not isinstance(myShape, Polygon):
				raise ValueError('Non-Polygon passed to cut_polygon_by_junctions: ' + repr(myShape.type))
		exteriorRing = myShape.exterior
		interiorRings = myShape.interiors
		# Count junctions on exterior ring
		junctionCountExtRing = self.count_junctions_in_points_list(exteriorRing.coords, dictJunctions)
		# If there are no junctions, just return None as the cutExterior ring
		if junctionCountExtRing == 0:
			return (None, myShape)
		# If there are at least 1, but fewer than 3 junctions on the exterior ring
		# we need to add new 'junctions' to make sure we don't simplify below 3 points
		# New junctions are necessary so we don't simplify that point for any bordering polygons
		if junctionCountExtRing > 0 and junctionCountExtRing < 3:
			junctionsToAdd = 3 - junctionCountExtRing
			self.add_junctions_to_ring(exteriorRing, junctionsToAdd, dictJunctions)
		# InteriorRings should have no junctions, so only cut the exterior ring
		cutExteriorRing = self.cut_ring_by_junctions(exteriorRing, dictJunctions)
		# Validate that there are no junctions on the interior rings
		if validate:
			for ring in interiorRings:
				for point in ring.coords:
					if self.quantitize(point) in dictJunctions:
						raise ValueError('Interior ring has a junction point: ' + repr(point))
		# Return a tuple containing the cut exterior ring, and the original shape
		return (cutExteriorRing, myShape)

	def cut_mpolygon_by_junctions(self, myShape, dictJunctions):
		if validate:
			if not isinstance(myShape, MultiPolygon):
				raise ValueError('Non-MultiPolygon passed to cut_mpolygon_by_junctions: ' + repr(myShape.type))
		cutMpolyList = []
		for polygon in myShape.geoms:
			cutMpolyList.append(self.cut_polygon_by_junctions(myShape, dictJunctions))
		return cutMpolyList

	def count_junctions_in_points_list(self, pointsList, dictJunctions):
		junctionPoints = []
		for point in pointsList:
			qp = self.quantitize(point)
			if qp in dictJunctions and qp not in junctionPoints:
				junctionPoints.append(qp)
		return len(junctionPoints)

	# Add artificial junctions to a ring that prevent it from being simplified at the artificial junctions
	def add_junctions_to_ring(self, ring, junctionsToAdd, dictJunctions):
		# Copy ring to temporary
		tempRing = copy.copy(ring)

		# For now just add the first non-junction points on the ring to the list of junctions:
		simpleRing = []
		for index, point in enumerate(ring.coords):
			quant_point = self.quantitize(point)
			if quant_point in dictJunctions: # if the point is a junction, add it to simplified ring
				simpleRing.append(ring.coords[index])
			elif junctionsToAdd > 0:	# even it the point is not a junction, if we still need new to add new juctions add the current point
				simpleRing.append(ring.coords[index])
				junctionsToAdd -= 1
		# Convert list into LinearRing
		simpleRing = LinearRing(simpleRing)

		# Add the ring points to dictJunctions
		for index, point in enumerate(simpleRing.coords):
			quant_point = self.quantitize(point)
			if quant_point not in dictJunctions:
				dictJunctions[quant_point] = 0
				# Using a 0 instead of a 1 to distinguish this type of of junction from
				# the ones calculated by append_junctions

class ArcThreshold(object):
	# Should return the same value even if start and end are switched
	def get_string(start, end):
		if str(start) < str(end):
			return str(start) + "_" + str(end)
		else:
			return str(end) + "_" + str(start)

class TriangleCalculator(object):
	def __init__(self, point, index):
		# Save instance variables
		self.point = point
		self.ringIndex = index
		self.prevTriangle = None
		self.nextTriangle = None
		
	def __eq__(self, other):
		return (self.calcArea() == other.calcArea())
				
	def __ne__(self, other):
		return not (self == other)

	def __lt__(self, other):
		return (self.calcArea() < other.calcArea())

	def calcArea(self):
		# Add validation
		#if not self.prevTriangle or not self.nextTriangle:
			#print "ERROR:"
		p1 = self.point
		p2 = self.prevTriangle.point
		p3 = self.nextTriangle.point
		area = abs(p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1])) / 2.0
		#print "area = " + str(area) + ", point = " + str(self.point)
		return area
#modified from rmapshaper( Visvalignam-Whyatt + Topology preservation)