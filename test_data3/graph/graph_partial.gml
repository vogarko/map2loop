# --- COLUMN NAMES IN CSV DATA FILES: -------------------------------------------------------------
# OBJECT COORDINATES              =WKT
# FAULT: ID                       =OBJECTID
# FAULT: FEATURE                  =FEATURE
# POINT: ID                       =GEOPNT_ID
# POINT: DIP                      =DIP
# POINT: DIP DIR                  =DIP_DIR
# POLYGON: ID                     =OBJECTID
# POLYGON: LEVEL1 NAME            =UNITNAME
# POLYGON: LEVEL2 NAME            =GROUP_
# POLYGON: MIN AGE                =MIN_AGE_MA
# POLYGON: MAX AGE                =MAX_AGE_MA
# POLYGON: CODE                   =CODE
# POLYGON: DESCRIPTION            =DESCRIPTN
# POLYGON: ROCKTYPE1              =ROCKTYPE1
# POLYGON: ROCKTYPE2              =ROCKTYPE2
# --- SOME CONSTANTS: ----------------------------------------------------------------------------
# FAULT AXIAL FEATURE NAME        =Fold axial trace
# SILL UNIT DESCRIPTION CONTAINS  =sill
# IGNEOUS ROCKTYPE CONTAINS                           =intrusive
# VOLCANIC ROCKTYPE CONTAINS                          =volcanic
# Intersect Contact With Fault: angle epsilon (deg)   =1.0
# Intersect Contact With Fault: distance epsilon (m)  =15.0
# ------------------------------------------------------------------------------------------------
# Path to the output data folder                      =../test_data3/graph/
# Path to geology data file                           =../test_data3/tmp/hams2_geol.csv
# Path to faults data file                            =../test_data3/tmp/GEOS_GEOLOGY_LINEARSTRUCTURE_500K_GSD.csv
# Path to points data file                            =../test_data3/tmp/hams2_structure.csv
# ------------------------------------------------------------------------------------------------
# Clipping window X1 Y1 X2 Y2 (zeros for infinite)    =500057 7455348 603028 7567953
# Min length fraction for strat/fault graphs          =0.0
# Graph edge width categories (three doubles)         =2000. 20000. 200000.
# Graph edge direction (0-min age, 1-max age, 2-avg)  =2
# Partial graph polygon ID                            =32
# Partial graph depth                                 =4
# Map subregion size dx, dy [m] (zeros for full map)  =0. 0.
# ------------------------------------------------------------------------------------------------
Creator "map2model-cpp"
graph [
  hierarchic 1
  directed 1
  node [
    id -8
    LabelGraphics [ text "A-b-PRK" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -9
    LabelGraphics [ text "A-mgn-PRK" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -10
    LabelGraphics [ text "A-s-PRK" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -1
    LabelGraphics [ text "Fortescue Group" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id 8
    LabelGraphics [ text "A-FO-od" fontSize 14 ]
    gid -1
    graphics [ fill "#ff4c4c" w 150 ]
  ]
  node [
    id 14
    LabelGraphics [ text "A-FO-xo-a" fontSize 14 ]
    gid -1
    graphics [ fill "#4cb694" w 150 ]
  ]
  node [
    id 6
    LabelGraphics [ text "A-FOh-xs-f" fontSize 14 ]
    gid -1
    graphics [ fill "#4cc882" w 150 ]
  ]
  node [
    id 7
    LabelGraphics [ text "A-FOo-bbo" fontSize 14 ]
    gid -1
    graphics [ fill "#4cc387" w 150 ]
  ]
  node [
    id 1
    LabelGraphics [ text "A-FOp-bs" fontSize 14 ]
    gid -1
    graphics [ fill "#4cdf6b" w 150 ]
  ]
  node [
    id 16
    LabelGraphics [ text "A-FOr-b" fontSize 14 ]
    gid -1
    graphics [ fill "#4c4cff" w 150 ]
  ]
  node [
    id 17
    LabelGraphics [ text "A-FOu-bbo" fontSize 14 ]
    gid -1
    graphics [ fill "#cd7d4c" w 150 ]
  ]
  node [
    id 15
    LabelGraphics [ text "A-b-PRK" fontSize 14 ]
    gid -8
    graphics [ fill "#4c5af0" w 150 ]
  ]
  node [
    id 5
    LabelGraphics [ text "A-mgn-PRK" fontSize 14 ]
    gid -9
    graphics [ fill "#4c65e5" w 150 ]
  ]
  node [
    id 21
    LabelGraphics [ text "A-s-PRK" fontSize 14 ]
    gid -10
    graphics [ fill "#4c52f8" w 150 ]
  ]
  edge [
    source 14
    target 1
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 8
    target 1
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 6
    target 5
    graphics [ style "line" arrow "last" width 5 fill "#0000ff" ]
  ]
  edge [
    source 5
    target 15
    graphics [ style "line" arrow "last" width 5 fill "#0000ff" ]
  ]
  edge [
    source 16
    target 5
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 6
    target 15
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 6
    target 16
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 14
    target 6
    graphics [ style "line" arrow "last" width 5 fill "#0000ff" ]
  ]
  edge [
    source 6
    target 21
    graphics [ style "line" arrow "last" width 5 fill "#0000ff" ]
  ]
  edge [
    source 16
    target 15
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 1
    target 7
    graphics [ style "line" arrow "last" width 5 fill "#007589" ]
  ]
  edge [
    source 17
    target 1
    graphics [ style "line" arrow "last" width 5 fill "#0039c5" ]
  ]
  edge [
    source 5
    target 21
    graphics [ style "line" arrow "last" width 5 fill "#fe0000" ]
  ]
  edge [
    source 7
    target 6
    graphics [ style "line" arrow "last" width 5 fill "#0008f6" ]
  ]
]