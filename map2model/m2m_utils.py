import geopandas as gpd
import pandas as pd
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry import Point
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.transform import from_origin
from rasterio import features
import re
from urllib.request import urlopen
from PIL import Image


#first test
def hw():
	print("Hello world")

#calculate mod with 0 meaning no mod
def mod_safe(a,b):
    
    if(b==0):
        return(0)
    else:
        return(a%b)
        
# get value froma rasterio raster at location x,y (real world coords)
def value_from_raster(dataset,locations):

    for val in dataset.sample(locations):
        value=str(val).replace("[","").replace("]","")
    return(value)

#get dtm data from Hawaiian SRTM server and save as geotiff
def get_dtm(path_out, minlong,maxlong,minlat,maxlat):

    minxll=int((minlong+180)*120)
    maxxll=int((maxlong+180)*120)
    minyll=int((minlat+90)*120)
    maxyll=int((maxlat+90)*120)
    
    sizex=round(maxxll-minxll+1)
    sizey=round(maxyll-minyll+1)
    
    minxll=str(minxll)
    maxxll=str(maxxll)
    minyll=str(minyll)
    maxyll=str(maxyll)
    bbox="["+minyll+":1:"+maxyll+"]["+minxll+":1:"+maxxll+"]"

    link = "http://oos.soest.hawaii.edu/thredds/dodsC/srtm30plus_v11_land.ascii?elev"+bbox

    f = urlopen(link)
    myfile = f.read()
    myfile2=myfile.decode("utf-8") 
    data=myfile2.split("---------------------------------------------")
    #import re

    grid=re.sub('\[.*\]','',data[1]).replace(",","").replace("elev.elev","").replace("\n"," ").replace("  "," ")
    #print(grid)
    grid=grid.split(" ")
    grid=grid[2:(sizex*sizey)+2]
    OPeNDAP = np.ones((sizey,sizex), dtype='int16')
    k=0
    for j in range (0, sizey, 1):
        for i in range (0, sizex, 1):
            OPeNDAP[sizey-1-j][i]=int(float(grid[k]))
            k+=1

    #maxtopo=np.amax(OPeNDAP)
    #print("max height =",maxtopo)
    #maxtopo=np.around(maxtopo,-2)+100
    #print("rounded up max height =",maxtopo)


    transform = from_origin(minlong, maxlat,0.008333333,0.008333333)

    new_dataset = rasterio.open(path_out, 'w', driver='GTiff',
                                height = OPeNDAP.shape[0], width = OPeNDAP.shape[1],
                                count=1, dtype=str(OPeNDAP.dtype),
                                crs='+proj=longlat',
                                transform=transform)

    new_dataset.write(OPeNDAP, 1)
    new_dataset.close()

#reproject a dtm 
def reproject_dtm(path_in,path_out,src_crs,dst_crs):
    with rasterio.open(path_in) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })


        with rasterio.open(path_out, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)

#get bounds of a dtm
def get_dtm_bounds(path_in,dst_crs):            
    with rasterio.open(path_in) as dataset:

        # Read the dataset's valid data mask as a ndarray.
        mask = dataset.dataset_mask()
        for geom, val in rasterio.features.shapes(
                    mask, transform=dataset.transform):

                # Transform shapes from the dataset's own coordinate
                # reference system to 28350.
                geom_rp = rasterio.warp.transform_geom(
                    dataset.crs, dst_crs, geom, precision=6)

                # Print GeoJSON shapes to stdout.
                #print(geom_rp)
                return(geom_rp)

#https://gist.github.com/mhweber/cf36bb4e09df9deee5eb54dc6be74d26
#code to explode a MultiPolygon to Polygons    

def explode(indf):
#    indf = gpd.GeoDataFrame.from_file(indata)
    outdf = gpd.GeoDataFrame(columns=indf.columns)
    for idx, row in indf.iterrows():
        if type(row.geometry) == Polygon:
            outdf = outdf.append(row,ignore_index=True)
        if type(row.geometry) == MultiPolygon:
            multdf = gpd.GeoDataFrame(columns=indf.columns)
            recs = len(row.geometry)
            multdf = multdf.append([row]*recs,ignore_index=True)
            for geom in range(recs):
                multdf.loc[geom,'geometry'] = row.geometry[geom]
            outdf = outdf.append(multdf,ignore_index=True)
    return outdf

###https://github.com/earthlab/earthpy/blob/master/earthpy/clip.py
###
### earthpy.clip
### ============
### A module to clip vector data using GeoPandas.
###

def _clip_points(shp, clip_obj):
    """Clip point geometry to the clip_obj GeoDataFrame extent.
    Clip an input point GeoDataFrame to the polygon extent of the clip_obj
    parameter. Points that intersect the clip_obj geometry are extracted with
    associated attributes and returned.
    Parameters
    ----------
    shp : GeoDataFrame
        Composed of point geometry that is clipped to clip_obj.
    clip_obj : GeoDataFrame
        Reference polygon for clipping.
    Returns
    -------
    GeoDataFrame
        The returned GeoDataFrame is a subset of shp that intersects
        with clip_obj.
    """
    poly = clip_obj.geometry.unary_union
    return shp[shp.geometry.intersects(poly)]


def _clip_multi_point(shp, clip_obj):
    """Clip multi point features to the clip_obj GeoDataFrame extent.
    Clip an input multi point to the polygon extent of the clip_obj
    parameter. Points that intersect the clip_obj geometry are
    extracted with associated attributes returned.
    Parameters
    ----------
    shp : GeoDataFrame
        multipoint geometry that is clipped to clip_obj.
    clip_obj : GeoDataFrame
        Reference polygon for clipping.
    Returns
    -------
    GeoDataFrame
        The returned GeoDataFrame is a clipped subset of shp
        containing multi-point and point features.
    """

    # Explode multi-point features when clipping then recreate geom
    clipped = _clip_points(shp.explode().reset_index(level=[1]), clip_obj)
    clipped = clipped.dissolve(by=[clipped.index]).drop(columns="level_1")[
        shp.columns.tolist()
    ]

    return clipped


def _clip_line_poly(shp, clip_obj):
    """Clip line and polygon geometry to the clip_obj GeoDataFrame extent.
    Clip an input line or polygon to the polygon extent of the clip_obj
    parameter. Lines or Polygons that intersect the clip_obj geometry are
    extracted with associated attributes and returned.
    Parameters
    ----------
    shp : GeoDataFrame
        Line or polygon geometry that is clipped to clip_obj.
    clip_obj : GeoDataFrame
        Reference polygon for clipping.
    Returns
    -------
    GeoDataFrame
        The returned GeoDataFrame is a clipped subset of shp
        that intersects with clip_obj.
    """
    # Create a single polygon object for clipping
    poly = clip_obj.geometry.unary_union
    spatial_index = shp.sindex

    # Create a box for the initial intersection
    bbox = poly.bounds
    # Get a list of id's for each object that overlaps the bounding box and
    # subset the data to just those lines
    sidx = list(spatial_index.intersection(bbox))
    shp_sub = shp.iloc[sidx]

    # Clip the data - with these data
    clipped = shp_sub.copy()
    clipped["geometry"] = shp_sub.intersection(poly)

    # Return the clipped layer with no null geometry values
    return clipped[clipped.geometry.notnull()]


def _clip_multi_poly_line(shp, clip_obj):
    """Clip multi lines and polygons to the clip_obj GeoDataFrame extent.
    Clip an input multi line or polygon to the polygon extent of the clip_obj
    parameter. Lines or Polygons that intersect the clip_obj geometry are
    extracted with associated attributes and returned.
    Parameters
    ----------
    shp : GeoDataFrame
        multiLine or multipolygon geometry that is clipped to clip_obj.
    clip_obj : GeoDataFrame
        Reference polygon for clipping.
    Returns
    -------
    GeoDataFrame
        The returned GeoDataFrame is a clipped subset of shp
        that intersects with clip_obj.
    """

    # Clip multi polygons
    clipped = _clip_line_poly(shp.explode().reset_index(level=[1]), clip_obj)

    lines = clipped[
        (clipped.geometry.type == "MultiLineString")
        | (clipped.geometry.type == "LineString")
    ]
    line_diss = lines.dissolve(by=[lines.index]).drop(columns="level_1")

    polys = clipped[clipped.geometry.type == "Polygon"]
    poly_diss = polys.dissolve(by=[polys.index]).drop(columns="level_1")

    return gpd.GeoDataFrame(
        pd.concat([poly_diss, line_diss], ignore_index=True)
    )

def clip_shp(shp, clip_obj):
    """Clip points, lines, or polygon geometries to the clip_obj extent.
    Both layers must be in the same Coordinate Reference System (CRS) and will
    be clipped to the full extent of the clip object.
    If there are multiple polygons in clip_obj,
    data from shp will be clipped to the total boundary of
    all polygons in clip_obj.
    Parameters
    ----------
    shp : GeoDataFrame
          Vector layer (point, line, polygon) to be clipped to clip_obj.
    clip_obj : GeoDataFrame
          Polygon vector layer used to clip shp.
          The clip_obj's geometry is dissolved into one geometric feature
          and intersected with shp.
    Returns
    -------
    GeoDataFrame
         Vector data (points, lines, polygons) from shp clipped to
         polygon boundary from clip_obj.
    Examples
    --------
    Clipping points (glacier locations in the state of Colorado) with
    a polygon (the boundary of Rocky Mountain National Park):
        >>> import geopandas as gpd
        >>> import earthpy.clip as cl
        >>> from earthpy.io import path_to_example
        >>> rmnp = gpd.read_file(path_to_example('rmnp.shp'))
        >>> glaciers = gpd.read_file(path_to_example('colorado-glaciers.geojson'))
        >>> glaciers.shape
        (134, 2)
        >>> rmnp_glaciers = cl.clip_shp(glaciers, rmnp)
        >>> rmnp_glaciers.shape
        (36, 2)
    Clipping a line (the Continental Divide Trail) with a
    polygon (the boundary of Rocky Mountain National Park):
        >>> cdt = gpd.read_file(path_to_example('continental-div-trail.geojson'))
        >>> rmnp_cdt_section = cl.clip_shp(cdt, rmnp)
        >>> cdt['geometry'].length > rmnp_cdt_section['geometry'].length
        0    True
        dtype: bool
    Clipping a polygon (Colorado counties) with another polygon
    (the boundary of Rocky Mountain National Park):
        >>> counties = gpd.read_file(path_to_example('colorado-counties.geojson'))
        >>> counties.shape
        (64, 13)
        >>> rmnp_counties = cl.clip_shp(counties, rmnp)
        >>> rmnp_counties.shape
        (4, 13)
    """
    try:
        shp.geometry
        clip_obj.geometry
    except AttributeError:
        raise AttributeError(
            "Please make sure that your input and clip GeoDataFrames have a"
            " valid geometry column"
        )

    if not any(shp.intersects(clip_obj.unary_union)):
        raise ValueError("Shape and crop extent do not overlap.")

    if any(shp.geometry.type == "MultiPoint"):
        return _clip_multi_point(shp, clip_obj)
    elif any(shp.geometry.type == "Point"):
        return _clip_points(shp, clip_obj)
    elif any(shp.geometry.type == "MultiPolygon") or any(
        shp.geometry.type == "MultiLineString"
    ):
        return _clip_multi_poly_line(shp, clip_obj)
    else:
        return _clip_line_poly(shp, clip_obj)

def save_clip_to_bbox(path,geom,minx,maxx,miny,maxy,dst_crs):
    y_point_list = [miny, miny, maxy, maxy, miny]
    x_point_list = [minx, maxx, maxx, minx, minx]

    bbox_geom = Polygon(zip(x_point_list, y_point_list))

    polygo = gpd.GeoDataFrame(index=[0], crs=dst_crs, geometry=[bbox_geom]) 
    
    clipped=clip_shp(geom,polygo)
    clipped.to_file(path)

try:
    import httplib
except:
    import http.client as httplib

def have_access(url):
    conn = httplib.HTTPConnection(url, timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        display(Image.open("./graphics/yes.png"))
        print("available: "+url)
    except:
        conn.close()
        display(Image.open("./graphics/no.png"))
        print("NOT available: "+url)
    