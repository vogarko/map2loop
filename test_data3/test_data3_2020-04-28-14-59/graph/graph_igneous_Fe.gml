# --- COLUMN NAMES IN CSV DATA FILES: -------------------------------------------------------------
# OBJECT COORDINATES              =WKT
# FAULT: ID                       =OBJECTID
# FAULT: FEATURE                  =FEATURE
# POLYGON: ID                     =OBJECTID
# POLYGON: LEVEL1 NAME            =UNITNAME
# POLYGON: LEVEL2 NAME            =GROUP_
# POLYGON: MIN AGE                =MIN_AGE_MA
# POLYGON: MAX AGE                =MAX_AGE_MA
# POLYGON: CODE                   =CODE
# POLYGON: DESCRIPTION            =DESCRIPTN
# POLYGON: ROCKTYPE1              =ROCKTYPE1
# POLYGON: ROCKTYPE2              =ROCKTYPE2
# DEPOSIT: SITE CODE                                  =SITE_CODE
# DEPOSIT: SITE TYPE                                  =SITE_TYPE_
# DEPOSIT: SITE COMMODITY                             =SITE_COMMO
# --- SOME CONSTANTS: ----------------------------------------------------------------------------
# FAULT AXIAL FEATURE NAME        =Fold axial trace
# SILL UNIT DESCRIPTION CONTAINS  =sill
# IGNEOUS ROCKTYPE CONTAINS                           =intrusive
# VOLCANIC ROCKTYPE CONTAINS                          =volcanic
# IGNORE DEPOSITS WITH SITE TYPE                      =Infrastructure
# Intersect Contact With Fault: angle epsilon (deg)   =1.0
# Intersect Contact With Fault: distance epsilon (m)  =15.0
# Distance buffer (fault stops on another fault) (m)  =20.0
# Distance buffer (point on contact) (m)              =500.0
# ------------------------------------------------------------------------------------------------
# Path to the output data folder                      =../test_data3/graph/
# Path to geology data file                           =../test_data3/tmp/hams2_geol.csv
# Path to faults data file                            =../test_data3/tmp/GEOS_GEOLOGY_LINEARSTRUCTURE_500K_GSD.csv
# Path to mineral deposits data file                  =../test_data3/tmp/mindeps_2018.csv
# ------------------------------------------------------------------------------------------------
# Clipping window X1 Y1 X2 Y2 (zeros for infinite)    =500057 7455348 603028 7567953
# Min length fraction for strat/fault graphs          =0.0
# Graph edge width categories (three doubles)         =2000. 20000. 200000.
# Graph edge direction (0-min age, 1-max age, 2-avg)  =2
# Deposit names for adding info on the graph          =Fe,Cu,Au,NONE
# Partial graph polygon ID                            =32
# Partial graph depth                                 =4
# Map subregion size dx, dy [m] (zeros for full map)  =0. 0.
# ------------------------------------------------------------------------------------------------
Creator "map2model-cpp"
graph [
  hierarchic 1
  directed 1
  node [
    id -10
    LabelGraphics [ text "A-b-PRK" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -11
    LabelGraphics [ text "A-mgn-PMI" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -12
    LabelGraphics [ text "A-mgn-PRK" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -13
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
    id -9
    LabelGraphics [ text "Hamersley Group" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id 8
    LabelGraphics [ text "A-FO-od" fontSize 14 ]
    gid -1
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 14
    LabelGraphics [ text "A-FO-xo-a" fontSize 14 ]
    gid -1
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 6
    LabelGraphics [ text "A-FOh-xs-f[3]" fontSize 14 ]
    gid -1
    graphics [ fill "#f0fff0" w 150 ]
  ]
  node [
    id 10
    LabelGraphics [ text "A-FOj-xs-b" fontSize 14 ]
    gid -1
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 7
    LabelGraphics [ text "A-FOo-bbo" fontSize 14 ]
    gid -1
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 1
    LabelGraphics [ text "A-FOp-bs[1]" fontSize 14 ]
    gid -1
    graphics [ fill "#fafffa" w 150 ]
  ]
  node [
    id 16
    LabelGraphics [ text "A-FOr-b" fontSize 14 ]
    gid -1
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 17
    LabelGraphics [ text "A-FOu-bbo[1]" fontSize 14 ]
    gid -1
    graphics [ fill "#fafffa" w 150 ]
  ]
  node [
    id 0
    LabelGraphics [ text "A-HAm-cib[10]" fontSize 14 ]
    gid -9
    graphics [ fill "#ccffcc" w 150 ]
  ]
  node [
    id 15
    LabelGraphics [ text "A-b-PRK" fontSize 14 ]
    gid -10
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 19
    LabelGraphics [ text "A-mgn-PMI" fontSize 14 ]
    gid -11
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 5
    LabelGraphics [ text "A-mgn-PRK[1]" fontSize 14 ]
    gid -12
    graphics [ fill "#fafffa" w 150 ]
  ]
  node [
    id 21
    LabelGraphics [ text "A-s-PRK" fontSize 14 ]
    gid -13
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 3
    LabelGraphics [ text "P_-HAb-cib[50]" fontSize 14 ]
    gid -9
    graphics [ fill "#00ff00" w 150 ]
  ]
  node [
    id 4
    LabelGraphics [ text "P_-HAj-xci-od[1]" fontSize 14 ]
    gid -9
    graphics [ fill "#fafffa" w 150 ]
  ]
  node [
    id 13
    LabelGraphics [ text "P_-HAw-fr" fontSize 14 ]
    gid -9
    graphics [ fill "#ffffff" w 150 ]
  ]
  edge [
    source 14
    target 1
    graphics [ style "line" arrow "last" width 5 fill "#0003fb" ]
  ]
  edge [
    source 8
    target 1
    graphics [ style "line" arrow "last" width 5 fill "#0006f8" ]
  ]
  edge [
    source 4
    target 3
    graphics [ style "line" arrow "last" width 7 fill "#001fdf" ]
    LabelGraphics [ text "7" fill "#dcffdc" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
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
    source 14
    target 6
    graphics [ style "line" arrow "last" width 5 fill "#0000ff" ]
  ]
  edge [
    source 10
    target 8
    graphics [ style "line" arrow "last" width 7 fill "#0014ea" ]
    LabelGraphics [ text "1" fill "#fafffa" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
  ]
  edge [
    source 13
    target 4
    graphics [ style "line" arrow "last" width 7 fill "#0021dd" ]
    LabelGraphics [ text "1" fill "#fafffa" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
  ]
  edge [
    source 14
    target 8
    graphics [ style "line" arrow "last" width 5 fill "#0003fb" ]
  ]
  edge [
    source 14
    target 17
    graphics [ style "line" arrow "last" width 5 fill "#0008f6" ]
  ]
  edge [
    source 8
    target 6
    graphics [ style "line" arrow "last" width 5 fill "#0012ec" ]
  ]
  edge [
    source 6
    target 19
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 8
    target 17
    graphics [ style "line" arrow "last" width 5 fill "#002bd3" ]
  ]
  edge [
    source 0
    target 8
    graphics [ style "line" arrow "last" width 3 fill "#9d6100" ]
  ]
  edge [
    source 14
    target 7
    graphics [ style "line" arrow "last" width 5 fill "#0002fc" ]
  ]
  edge [
    source 8
    target 7
    graphics [ style "line" arrow "last" width 5 fill "#000bf3" ]
  ]
  edge [
    source 5
    target 21
    graphics [ style "line" arrow "last" width 5 fill "#fe0000" ]
  ]
]