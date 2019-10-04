# map2loop Package

A package to extract information from geological maps to feed 3D modelling packages

#### What it does:
  
-  Combines information extracted from geology map in various forms to supoprt 3D geological modelling. Outputs are simple csv files that should be readble by any 3D mdoelling system (I think).

#### Inputs: (example data supplied) 
   
- Geology Polygons  
- Fault and fold axial trace PolyLines  
- Structure measurements (bed dips)
- Graph from Vitaliy's map2model cpp code 
  
#### map2loop outputs:
  
| content | filename | created by | example notebook |
| ----- | ----- | ----- | ----- |
| dtm in lat long wgs83 | \*/dtm/\*_dtm.tif | m2l_utils.get_dtm |   2 |
| georeferenced dtm | \*/dtm/\*_dtm_rp.tif| m2l_utils.reproject_dtm |  2 |
| Bed dip dd data with z and formation | \*/output/\*_orientations.csv | m2l_geometry. save_orientations |  2 |
| Extra orientations for empty series | \*/output/\*_empty_series_orientations.csv | m2l_geometry. create_orientations |  2 |
| Contact info with z and formation | \*/output/\*_contacts4.csv | m2l_geometry. save_basal_contacts |  2 |
| Fault trace with z | \*/output/\*_faults.csv | m2l_geometry. save_faults |  2 |
| Fault orientation with z | \*/output/\*_fault_orientations.csv | m2l_geometry. save_faults |  2 |
| Pluton contacts with z and formation | \*/output/ign_contacts.csv | Notebook 8 |  8 |
| Pluton contact orientations | \*/output/ign_orientations_\*.csv | Notebook 8 |  8 |
| Interpolated dip dip direction grid | \*/tmp/interpolation_scipy_rbf.csv | m2l_interpolation. interpolate_orientations |  4 |
| Interpolated contact vector grid | \*/tmp/interpolation_contacts_scipy_rbf.csv | m2l_interpolation. interpolate_contacts |  5 |
| Combined interpolation grid | \*/tmp/combo_full.csv | m2l_interpolation. join_contacts_and_orientations |  6 |
| Fault-fault relationship table | \*/output/fault-fault-relationships.csv | Notebook 7 |  7 |
| Fault-unit relationship table | \*/output/unit-fault-relationships.csv | Notebook 7 |  7 |
| Fault-group relationship table | \*/output/group-fault-relationships.csv | Notebook 7 |  7 |
| Local formation thickness estimates | \*/output/formation_thicknesses.csv | Notebook 9 |  9 |
| Group-level stratigraphic relationships | \*/tmp/\*_Group.csv | m2l_topology. save_group |  2 |
| Formation-level stratigraphic relationships | \*/tmp/*_groups.csv | m2l_topology. save_units |  2 |
| Summary strat relationships | \*/tmp/*_all_sorts.csv| m2l_topology. save_units |  2 |
| Basal contacts shapefile | \*/tmp/\*_basal_contacts2.shp | m2l_geometry. save_basal_no_faults |  2 |
| Clipped geology map shapefile | \*/tmp/geol_clip.shp | Notebook 2 |  2 |
| Clipped fault & fold axial traces shapefile  | \*/tmp/faults_clip.shp | Notebook 2 |  2 |
| Clipped orientations shapefile  | \*/tmp/structure_clip.shp | Notebook 2 |  2 |
| Various topology graphs  | \*/graph/\*.gml | map2model cpp code in Notebook 1 |  1 |
| Basic vtk model thanks to gempy  | \*/vtk/\*.vtp | gempy |  3 |

  
Does not deal with sills yet.  
Sample code to feed to gempy, but second sample code that does it better broken!  
<br>
Standalone map2model cpp code from Vitaliy provides fault/fault and fault/strat relationships   

#### Installation
For the moment installation uses:<br>

pip install --index-url https://test.pypi.org/simple/ --no-deps map2loop  
or   
setup.py install
  
#### Requirements
rasterio
matplotlib
networkx
numpy
pandas
geopandas
os
urllib
sys
math
shapely
gempy
