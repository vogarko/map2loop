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
    id -12
    LabelGraphics [ text "A-b-PRK" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -13
    LabelGraphics [ text "A-mgn-PMI" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -14
    LabelGraphics [ text "A-mgn-PRK" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -15
    LabelGraphics [ text "A-s-PMI" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -16
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
    id -21
    LabelGraphics [ text "Shingle Creek Group" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -23
    LabelGraphics [ text "Turee Creek Group" anchor "n" fontStyle "bold" fontSize 14 ]
    isGroup 1
    graphics [ fill "#FAFAFA" ]
  ]
  node [
    id -27
    LabelGraphics [ text "Wyloo Group" anchor "n" fontStyle "bold" fontSize 14 ]
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
    id 2
    LabelGraphics [ text "A-HAS-xsl-ci[2]" fontSize 14 ]
    gid -9
    graphics [ fill "#f5fff5" w 150 ]
  ]
  node [
    id 9
    LabelGraphics [ text "A-HAd-kd[6]" fontSize 14 ]
    gid -9
    graphics [ fill "#e1ffe1" w 150 ]
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
    gid -12
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 19
    LabelGraphics [ text "A-mgn-PMI" fontSize 14 ]
    gid -13
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 5
    LabelGraphics [ text "A-mgn-PRK[1]" fontSize 14 ]
    gid -14
    graphics [ fill "#fafffa" w 150 ]
  ]
  node [
    id 20
    LabelGraphics [ text "A-s-PMI" fontSize 14 ]
    gid -15
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 21
    LabelGraphics [ text "A-s-PRK" fontSize 14 ]
    gid -16
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
    id 12
    LabelGraphics [ text "P_-HAo-ci" fontSize 14 ]
    gid -9
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 13
    LabelGraphics [ text "P_-HAw-fr" fontSize 14 ]
    gid -9
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 28
    LabelGraphics [ text "P_-SKb-bb" fontSize 14 ]
    gid -21
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 22
    LabelGraphics [ text "P_-SKq-stq" fontSize 14 ]
    gid -21
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 18
    LabelGraphics [ text "P_-TK-s" fontSize 14 ]
    gid -23
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 11
    LabelGraphics [ text "P_-TKa-xs-k" fontSize 14 ]
    gid -23
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 27
    LabelGraphics [ text "P_-TKk-sf" fontSize 14 ]
    gid -23
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 26
    LabelGraphics [ text "P_-TKo-stq" fontSize 14 ]
    gid -23
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 24
    LabelGraphics [ text "P_-WYa-st" fontSize 14 ]
    gid -27
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 25
    LabelGraphics [ text "P_-WYd-kd" fontSize 14 ]
    gid -27
    graphics [ fill "#ffffff" w 150 ]
  ]
  node [
    id 23
    LabelGraphics [ text "P_-WYm-sp" fontSize 14 ]
    gid -27
    graphics [ fill "#ffffff" w 150 ]
  ]
  edge [
    source 0
    target 10
    graphics [ style "line" arrow "last" width 7 fill "#002cd2" ]
    LabelGraphics [ text "9" fill "#d2ffd2" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
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
    source 3
    target 2
    graphics [ style "line" arrow "last" width 7 fill "#0013eb" ]
    LabelGraphics [ text "41" fill "#2eff2e" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
  ]
  edge [
    source 2
    target 9
    graphics [ style "line" arrow "last" width 7 fill "#0010ee" ]
    LabelGraphics [ text "18" fill "#a4ffa4" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
  ]
  edge [
    source 3
    target 9
    graphics [ style "line" arrow "last" width 3 fill "#4bb300" ]
    LabelGraphics [ text "1" fill "#fafffa" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
  ]
  edge [
    source 3
    target 10
    graphics [ style "line" arrow "last" width 5 fill "#fe0000" ]
    LabelGraphics [ text "1" fill "#fafffa" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
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
    source 10
    target 8
    graphics [ style "line" arrow "last" width 7 fill "#0014ea" ]
    LabelGraphics [ text "1" fill "#fafffa" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
  ]
  edge [
    source 17
    target 1
    graphics [ style "line" arrow "last" width 7 fill "#002bd3" ]
  ]
  edge [
    source 10
    target 17
    graphics [ style "line" arrow "last" width 7 fill "#002fcf" ]
    LabelGraphics [ text "1" fill "#fafffa" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
  ]
  edge [
    source 2
    target 10
    graphics [ style "line" arrow "last" width 1 fill "#b24c00" ]
  ]
  edge [
    source 11
    target 26
    graphics [ style "line" arrow "last" width 3 fill "#001ae4" ]
  ]
  edge [
    source 7
    target 6
    graphics [ style "line" arrow "last" width 5 fill "#000df1" ]
    LabelGraphics [ text "1" fill "#fafffa" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
  ]
  edge [
    source 9
    target 10
    graphics [ style "line" arrow "last" width 3 fill "#f90500" ]
  ]
  edge [
    source 12
    target 13
    graphics [ style "line" arrow "last" width 5 fill "#000df1" ]
  ]
  edge [
    source 12
    target 18
    graphics [ style "line" arrow "last" width 5 fill "#0012ec" ]
  ]
  edge [
    source 13
    target 4
    graphics [ style "line" arrow "last" width 7 fill "#0021dd" ]
    LabelGraphics [ text "1" fill "#fafffa" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
  ]
  edge [
    source 18
    target 13
    graphics [ style "line" arrow "last" width 1 fill "#f20c00" ]
  ]
  edge [
    source 9
    target 0
    graphics [ style "line" arrow "last" width 7 fill "#001be3" ]
    LabelGraphics [ text "24" fill "#85ff85" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
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
    source 2
    target 0
    graphics [ style "line" arrow "last" width 5 fill "#9b6300" ]
    LabelGraphics [ text "2" fill "#f5fff5" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
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
    source 16
    target 15
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 8
    target 7
    graphics [ style "line" arrow "last" width 5 fill "#000bf3" ]
  ]
  edge [
    source 22
    target 27
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 22
    target 28
    graphics [ style "line" arrow "both" width 3 fill "#0000ff" ]
  ]
  edge [
    source 23
    target 22
    graphics [ style "line" arrow "last" width 1 fill "#0000ff" ]
  ]
  edge [
    source 22
    target 18
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 25
    target 23
    graphics [ style "line" arrow "last" width 5 fill "#0000ff" ]
  ]
  edge [
    source 26
    target 27
    graphics [ style "line" arrow "last" width 3 fill "#004cb2" ]
  ]
  edge [
    source 28
    target 27
    graphics [ style "line" arrow "last" width 1 fill "#0000ff" ]
  ]
  edge [
    source 23
    target 27
    graphics [ style "line" arrow "last" width 1 fill "#0000ff" ]
  ]
  edge [
    source 23
    target 28
    graphics [ style "line" arrow "last" width 3 fill "#0000ff" ]
  ]
  edge [
    source 1
    target 7
    graphics [ style "line" arrow "last" width 5 fill "#0054aa" ]
    LabelGraphics [ text "1" fill "#fafffa" fontSize 14 fontStyle "bold" model "centered" position "center" outline "#000000"]
  ]
  edge [
    source 5
    target 21
    graphics [ style "line" arrow "last" width 5 fill "#fe0000" ]
  ]
  edge [
    source 22
    target 11
    graphics [ style "line" arrow "last" width 3 fill "#0015e9" ]
  ]
  edge [
    source 11
    target 27
    graphics [ style "line" arrow "last" width 3 fill "#0029d5" ]
  ]
  edge [
    source 6
    target 20
    graphics [ style "line" arrow "last" width 5 fill "#0012ec" ]
  ]
  edge [
    source 12
    target 27
    graphics [ style "line" arrow "last" width 5 fill "#005aa4" ]
  ]
  edge [
    source 25
    target 18
    graphics [ style "line" arrow "last" width 3 fill "#a45a00" ]
  ]
  edge [
    source 24
    target 25
    graphics [ style "line" arrow "last" width 3 fill "#04fa00" ]
  ]
]