#ROI

step_out=0.1   #padding arounf dtm to ensure reprojected dtm covers target area (in degrees)
inset=0      #unused??

minx=500057  #region of interest coordinates in metre-based system (or non-degree system)
maxx=603028
miny=7455348
maxy=7567953
model_top=1200
model_base=-8200

#PATHS

test_data_path='../test_data3/'
m2m_cpp_path='../m2m_cpp/'

mindep_file='mindeps_2018.shp' #input mineral deposit file (if local)

structure_file='http://geo.loop-gis.org/geoserver/loop/wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=warox_points_f5011&bbox='+bbox2+'&srs=EPSG:28350'
fault_file='http://geo.loop-gis.org/geoserver/loop/wfs?service=WFS&version=1.1.0&request=GetFeature&typeName=linear_500k&bbox='+bbox2+'&srs=EPSG:28350'
geology_file='http://geo.loop-gis.org/geoserver/loop/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=loop:geol_500k&bbox='+bbox2+'&srs=EPSG:28350'


#CRS

src_crs = {'init': 'EPSG:4326'}  # coordinate reference system for imported dtms (geodetic lat/long WGS84)
dst_crs = {'init': 'EPSG:28350'} # coordinate system for data

#codes and labels these refer to specific fields (codes) in GIS layer or database that contain the info needed for these calcs and text substrings (labels) in the contents of these fields
c_l= {
#Orientations
  "d": "dip",                  #field that contains dip information
  "dd": "dip_dir",             #field that contains dip direction information
  "sf": 'feature',             #field that contains information on type of structure
  "bedding": 'Bed',            #text to search for in field defined by sfcode to show that this is a bedding measurement
#Stratigraphy
  "g": 'group_',               #field that contains coarser stratigraphic coding
  "c": 'code',                 #field that contains finer stratigraphic coding
  "ds": 'descriptn',           #field that contains information about lithology
  "u": 'unitname',             #field that contains alternate stratigraphic coding (not used??)
  "r1": 'rocktype1',           #field that contains  extra lithology information
  "r2": 'rocktype2',           #field that contains even more lithology information
  "sill": 'sill',              #text to search for in field defined by dscode to show that this is a sill
  "intrusive": 'intrusive',    #text to search for in field defined by dscode to show that this is an intrusion
  "volcanic": 'volcanic',      #text to search for in field defined by dscode to show that this is an intrusion
#Timing
  "min": 'min_age_ma',         #field that contains minimum age of unit defined by ccode
  "max": 'max_age_ma',         #field that contains maximum age of unit defined by ccode
#faults and folds
  "f": 'feature',              #field that contains information on type of structure
  "fault": 'Fault',            #text to search for in field defined by fcode to show that this is a fault
  "fold": 'Fold axial trace',  #text to search for in field defined by fcode to show that this is a fold axial trace
  "n": 'name',                 #field that contains information on name of fault (not used??)
  "t": 'type',                 #field that contains information on type of fold
  "syn": 'syncline',           #text to search for in field defined by t to show that this is a syncline
#ids
  "o": 'objectid',             #field that contains unique id of geometry object
  "gi": 'geopnt_id'            #field that contains unique id of structure point
}

#DECIMATION

orientation_decimate=0  #store every nth orientation (in object order) 0 = save all
contact_decimate=10     #store every nth contact point (in object order) 0 = save all
fault_decimate=5        #store every nth fault point (in object order) 0 = save all
fold_decimate=5         #store every nth fold axial trace point (in object order) 0 = save all


#INTERPOLATION

gridx=50                #x grid dimensions (no of points, not distance) for interpolations
gridy=50                #x grid dimensions (no of points, not distance) for interpolations
scheme='scipy_rbf'      #interpolation scheme
dist_buffer=5           #buffer distance for clipping points by faults (in metres or same units as dst_crs)
intrusion_mode=0        # 1 all intrusions exluded from basal contacts, 0 only sills
use_interpolations=False    # flag to sue interpolated orientations or not.

#ASSUMPTIONS

pluton_dip=45           #surface dip of pluton contacts
pluton_form='domes'     #saucers: \__+_+__/  batholith: +/       \+   domes: /  +  + \  pendant: +\_____/+
fault_dip=90            #surface dip of faults

#DERIVED PATHS

local_paths=False       #flag to use local or WFS source for data inputs (True = local)

graph_path=test_data_path+'graph/'
tmp_path=test_data_path+'tmp/'
data_path=test_data_path+'data/'
dtm_path=test_data_path+'dtm/'
output_path=test_data_path+'output/'
vtk_path=test_data_path+'vtk/'

fault_file=data_path+fault_file
structure_file=data_path+structure_file
geology_file=data_path+geology_file
mindep_file=data_path+mindep_file

fault_file_csv=fault_file.replace(".shp",".csv").replace("/data/","/tmp/")
structure_file_csv=structure_file.replace(".shp",".csv").replace("/data/","/tmp/")
geology_file_csv=geology_file.replace(".shp",".csv").replace("/data/","/tmp/")
mindep_file_csv=mindep_file.replace(".shp",".csv").replace("/data/","/tmp/")

strat_graph_file=test_data_path+'graph/graph_strat.gml'

dtm_file=dtm_path+'dtm.tif'
dtm_reproj_file=dtm_path+'dtm_rp.tif'

if(not os.path.isdir(test_data_path)):
   os.mkdir(test_data_path)
if(not os.path.isdir(tmp_path)):
   os.mkdir(tmp_path)
if(not os.path.isdir(output_path)):
   os.mkdir(output_path)
if(not os.path.isdir(dtm_path)):
   os.mkdir(dtm_path)
if(not os.path.isdir(vtk_path)):
   os.mkdir(vtk_path)
if(not os.path.isdir(graph_path)):
   os.mkdir(graph_path)

print('Default parameters loaded from '+test_data_path+'m2l_config_remote.py:')
with open(test_data_path+'m2l_config_remote.py', 'r') as myfile:
  data = myfile.read()
  print(data)
  myfile.close()

print('\nModify these parameters in the cell below')