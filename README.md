# map2loop Package

A package to extract information from geological maps to feed 3D modelling packages

#### What it does:
  
- Inputs: (example data supplied)  
- Graph from Vitaliy's map2model ArcPlugin (and soon via standalone code)  
- Geology Polygons  
- Fault PolyLines  
- Structure measurements (bed dips)
- Fold axial traces
- Interoplated structural data  
  
#### map2loop outputs:
  
| content | filename | created by | Example Notebook |
| dtm in lat long wgs83 | */dtm/*_dtm.tif | m2l_utils.get_dtm |  Notebook 2 |
| georeferenced dtm | */dtm/*_dtm_rp.tif| m2l_utils.reproject_dtm | Notebook 2 |
| Bed dip dd data with z and formation | */output/*_orientations.csv | m2l_geometry.save_orientations | Notebook 2 |
| Extra orientations for empty series | */output/*_empty_series_orientations.csv | m2l_geometry.create_orientations | Notebook 2 |
| Contact info with z and formation | */output/*_contacts4.csv | m2l_geometry.save_basal_contacts | Notebook 2 |
| Fault trace with z | */output/*_faults.csv | m2l_geometry.save_faults | Notebook 2 |
| Fault orientation with z | */output/*_fault_orientations.csv | m2l_geometry.save_faults | Notebook 2 |
| Pluton contacts with z and formation | */output/ign_contacts.csv | Notebook 8 | Notebook 8 |
| Pluton contact orientations | */output/ign_orientations_*.csv | Notebook 8 | Notebook 8 |
| Interpolated d dd grid | */tmp/interpolation_scipy_rbf.csv | m2l_interpolation.interpolate_orientations | Notebook 4 |
| Interpolated contact vector grid | */tmp/interpolation_contacts_scipy_rbf.csv | m2l_interpolation.interpolate_contacts | Notebook 5 |
| Combined interpolation grid | */tmp/combo_full.csv | m2l_interpolation.join_contacts_and_orientations | Notebook 6 |
| Fault-fault relationship table | */output/fault-fault-relationships.csv | Notebook 7 | Notebook 7 |
| Fault-unit relationship table | */output/unit-fault-relationships.csv | Notebook 7 | Notebook 7 |
| Fault-group relationship table | */output/group-fault-relationships.csv | Notebook 7 | Notebook 7 |
| Local formation thickness estimates | */output/formation_thicknesses.csv | Notebook 9 | Notebook 9 |
| Group-level stratigraphic relationships | */tmp/*_Group.csv | m2l_topology.save_group | Notebook 2 |
| Formation-level stratigraphic relationships | */tmp/*_groups.csv | m2l_topology.save_units | Notebook 2 |
| Summary strat relationships | */tmp/*_all_sorts.csv| m2l_topology.save_units | Notebook 2 |
| Basal contacts shapefile | */tmp/*_basal_contacts2.shp | m2l_geometry.save_basal_no_faults | Notebook 2 |
| Clipped geology map shapefile | */tmp/geol_clip.shp | Notebook 2 | Notebook 2 |
| Clipped fault & fold axial traces shapefile  | */tmp/faults_clip.shp | Notebook 2 | Notebook 2 |
| Clipped orientations shapefile  | */tmp/structure_clip.shp | Notebook 2 | Notebook 2 |
| Various topology graphs  | */graph/*.gml | map2model cpp code in Notebook 1 | Notebook 1 |

  
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
