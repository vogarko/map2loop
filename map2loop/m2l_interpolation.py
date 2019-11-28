import numpy as np
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
from matplotlib import cm
from math import sin, cos, atan, atan2, asin, radians, degrees, sqrt, pow, acos
import numpy as np
import geopandas as gpd
from geopandas import GeoDataFrame
import pandas as pd
import os
from shapely.geometry import Polygon
from shapely.geometry import Point
from map2loop import m2l_utils
import rasterio

######################################
# inspired by https://stackoverflow.com/questions/3104781/inverse-distance-weighted-idw-interpolation-with-python
# 
# Simple Inverse Distance Weighting interpolation of observations z at x,y locations returned at locations defined by xi,yi arrays. From...
# scipy_idw(x, y, z, xi, yi)
# Args:
# x,y coordinates of points to be interpolated
# z value to be interpolated
# xi,yi grid of points where interpolation of z will be calculated - sci_py version of Simple Inverse Distance Weighting interpolation of observations z at x,y locations returned at locations defined by xi,yi arrays
# 
# simple Inverse Distance Weighting calculation
######################################
def simple_idw(x, y, z, xi, yi):
    dist = distance_matrix(x,y, xi,yi)

    # In IDW, weights are 1 / distance
    weights = 1.0 / (dist)

    # Make weights sum to one
    weights /= weights.sum(axis=0)

    # Multiply the weights for each interpolated point by all observed Z-values
    zi = np.dot(weights.T, z)
    return zi

######################################
# call scipy inverse distance weighting
# 
# Simple Inverse Distance Weighting interpolation of observations z at x,y locations returned at locations defined by xi,yi arrays. From...
# scipy_idw(x, y, z, xi, yi)
# Args:
# x,y coordinates of points to be interpolated
# z value to be interpolated
# xi,yi grid of points where interpolation of z will be calculated - sci_py version of Simple Inverse Distance Weighting interpolation of observations z at x,y locations returned at locations defined by xi,yi arrays
# 
######################################
def scipy_idw(x, y, z, xi, yi):
    interp = Rbf(x, y, z, function='linear')
    return interp(xi, yi)

######################################
# call scipy Radial basis function interpolation
# 
# scipy_rbf(x, y, z, xi, yi)
# Args:
# x,y coordinates of points to be interpolated
# z value to be interpolated
# xi,yi grid of points where interpolation of z will be calculated
# 
# sci_py version of Radial Basis Function interpolation of observations z at x,y locations returned at locations defined by xi,yi arraysplot(x,y,z,grid)
######################################
def scipy_rbf(x, y, z, xi, yi):
    interp = Rbf(x, y, z, epsilon=1)
    return interp(xi, yi)

######################################
# calculate all distances between to arrays of points
# Make a distance matrix between pairwise observations
# Note: from <http://stackoverflow.com/questions/1871536>
# (Yay for ufuncs!)
# distance_matrix(x0, y0, x1, y1)
# Args:
# x0,y0 array of point locations
# x1,y1 second array of point locations
# 
# Returns array of distances between all points defined by arrays by x0,y0 and all points defined by arrays x1,y1 from http://stackoverflow.com/questions/1871536
######################################
def distance_matrix(x0, y0, x1, y1):
    obs = np.vstack((x0, y0)).T
    interp = np.vstack((x1, y1)).T

    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])

    return np.hypot(d0, d1)

######################################
# plot an array of data
######################################
def plot(x,y,z,grid):
    plt.figure()
    plt.imshow(grid, extent=(0,100,0,100))
    #plt.hold(True)
    #plt.scatter(x,100-y,c=z)
    plt.colorbar()

######################################
# interpolate three data arrays using various schemes
#
# call_interpolator(calc,x,y,l,m,n,xi,yi,nx,ny)
# Args:
# calc calculation mode, one of 'simple_idw', 'scipy_idw', 'scipy_rbf'
# l,m,n arrays of direction cosines of pole to plane
# xi,yi arrays of locations of interpolated locations (assumes a grid for plotting, otherwise doesn't matter)
# nx,ny number of x,y elemnts in grid
# 
# Call interpolator defined by calc for arrays of arbitrary location x,y located observations as triple or double arrays of 3D or 2D direction cosine arrays (l,m,n) and returns grid of nx ,ny interpolated values for points defined by xi,yi locations. Inspired by https://stackoverflow.com/questions/3104781/inverse-distance-weighted-idw-interpolation-with-python
######################################
def call_interpolator(calc,x,y,l,m,n,xi,yi,nx,ny):
    # Calculate IDW or other interpolators

    #display(x)
    #display(y)
    #display(l)
    #display(m)
    #display(xi)
    #display(yi)
    #display(nx)
    #display(ny)
        
    if(calc=='simple_idw'):
        ZIl = simple_idw(x,y,l,xi,yi)
    if(calc=='scipy_rbf'):
        ZIl = scipy_rbf(x,y,l,xi,yi)
    if(calc=='scipy_idw'):
        ZIl = scipy_idw(x,y,l,xi,yi)
    ZIl = ZIl.reshape((ny, nx))
    
    if(calc=='simple_idw'):
        ZIm = simple_idw(x,y,m,xi,yi)
    if(calc=='scipy_rbf'):
        ZIm = scipy_rbf(x,y,m,xi,yi)
    if(calc=='scipy_idw'):
        ZIm = scipy_idw(x,y,m,xi,yi)
    ZIm = ZIm.reshape((ny, nx))
    
    if(type(n) is not int):
        if(calc=='simple_idw'):
            ZIn = simple_idw(x,y,n,xi,yi)
        if(calc=='scipy_rbf'):
            ZIn = scipy_rbf(x,y,n,xi,yi)
        if(calc=='scipy_idw'):
            ZIn = scipy_idw(x,y,n,xi,yi)
        ZIn = ZIn.reshape((ny, nx))   
    else:
        ZIn=0
        
    return(ZIl,ZIm,ZIn)
    
######################################
# Interpolate dipd,dipdirection data from shapefile     
#
# interpolate_orientations(structure_file,tmp_path,bbox,c_l,use_gcode,scheme,gridx,gridy)
# structure_file path to orientation layer
# tmp_path directory of temporary outputs from m2l
# bbox bounding box of region of interest
# c_l dictionary of codes and labels specific to input geo information layers
# use_gcode list of groups whose orientation data will be interpolated scheme interpolation scheme one of 'simple_idw', 'scipy_idw', 'scipy_rbf'
# gridx,gridy number of cols & rows in interpolation grid
# 
# Interpolate orientation layer to produce regular grid of l,m,n direction cosines
# Can choose between various RBF and IDW options
# The purpose of these interpolations and associated code is to help in three cases:
# -- Providing estimated dips and contacts in fault-bounded domains where no structural data are available
# -- Needed to estimate true thickness of formations
# -- Useful for poulating parts of maps where little structural data is available
######################################
def interpolate_orientations(structure_file,output_path,bbox,c_l,this_gcode,calc,gridx,gridy):
    structure = gpd.read_file(structure_file,bbox=bbox)
    
    if(len(this_gcode)==1):       
        is_gp=structure[c_l['g']] == thisgcode # subset orientations to just those with this group
        gp_structure = structure[is_gp]
        #print('single group')
        #display(gp_structure)
    else:
        #print('first code',this_gcode[0])
        is_gp=structure[c_l['g']] == this_gcode[0] # subset orientations to just those with this group
        gp_structure = structure[is_gp]
        gp_structure_all = gp_structure.copy()
        #print('first group')
        #display(gp_structure)

        for i in range (1,len(this_gcode)):
            #print('next code',this_gcode[i])
            is_gp=structure[c_l['g']] == this_gcode[i] # subset orientations to just those with this group
            temp_gp_structure = structure[is_gp]
            gp_structure_all = pd.concat([gp_structure_all, temp_gp_structure], ignore_index=True)
            #print('next group')
            #display(gp_structure)

    npts = len(gp_structure_all)
    
    nx, ny = gridx,gridy

    xi = np.linspace(bbox[0],bbox[2], nx)
    yi = np.linspace(bbox[1],bbox[3], ny)
    xi, yi = np.meshgrid(xi, yi)
    xi, yi = xi.flatten(), yi.flatten()
    x = np.zeros(npts)
    y = np.zeros(npts)
    dip = np.zeros(npts)
    dipdir = np.zeros(npts)
    
    i=0
    for a_pt in gp_structure_all.iterrows():
        x[i]=a_pt[1]['geometry'].x
        y[i]=a_pt[1]['geometry'].y
        dip[i] = a_pt[1][c_l['d']]
        dipdir[i] = a_pt[1][c_l['dd']]
        i=i+1
    
    l=np.zeros(npts)
    m=np.zeros(npts)
    n=np.zeros(npts)
    
    for i in range(0,npts):
        l[i],m[i],n[i]=m2l_utils.ddd2dircos(dip[i],dipdir[i])

    ZIl,ZIm,ZIn=call_interpolator(calc,x,y,l,m,n,xi,yi,nx,ny)
    
    # Comparisons...
    plot(x,-y,l,ZIl)
    plt.title('l')
    plot(x,-y,m,ZIm)
    plt.title('m')
    plot(x,-y,n,ZIn)
    plt.title('n')
    
    plt.show()
    
    f=open(output_path+'input.csv','w')
    fi=open(output_path+'interpolation_'+calc+'.csv','w')
    fl=open(output_path+'interpolation_l.csv','w')
    fm=open(output_path+'interpolation_m.csv','w')
    fn=open(output_path+'interpolation_n.csv','w')
    
    f.write("x,y,dip,dipdirection\n")
    fi.write("x,y,dip,dipdirection\n")
    fl.write("x,y,l\n")
    fm.write("x,y,m\n")
    fn.write("x,y,n\n")
    
    for i in range (0,npts):
        ostr=str(x[i])+","+str(y[i])+","+str(int(dip[i]))+","+str(int(dipdir[i]))+'\n'
        f.write(ostr)
    
    for xx in range (0,gridx):
        for yy in range (0,gridy):
            yyy=xx
            xxx=gridy-2-yy
            L=ZIl[xxx,yyy]/(sqrt((pow(ZIl[xxx,yyy],2.0))+(pow(ZIm[xxx,yyy],2.0))+(pow(ZIn[xxx,yyy],2.0))))
            M=ZIm[xxx,yyy]/(sqrt((pow(ZIl[xxx,yyy],2.0))+(pow(ZIm[xxx,yyy],2.0))+(pow(ZIn[xxx,yyy],2.0))))
            N=ZIn[xxx,yyy]/(sqrt((pow(ZIl[xxx,yyy],2.0))+(pow(ZIm[xxx,yyy],2.0))+(pow(ZIn[xxx,yyy],2.0))))
            
            dip,dipdir=m2l_utils.dircos2ddd(L,M,N)

            ostr=str(bbox[0]+(xx*((bbox[2]-bbox[0])/gridx)))+","+str(bbox[1]+((gridy-1-yy)*((bbox[3]-bbox[1])/gridy)))+","+str(int(dip))+","+str(int(dipdir))+'\n'
            fi.write(ostr)
            
            ostr=str(xx)+","+str(yy)+","+str(L)+'\n'
            fl.write(ostr)
            ostr=str(xx)+","+str(yy)+","+str(M)+'\n'
            fm.write(ostr)
            ostr=str(xx)+","+str(yy)+","+str(N)+'\n'
            fn.write(ostr)
    
    f.close()
    fi.close()
    fl.close()
    fm.close()
    fn.close()
    
    fig, ax = plt.subplots(figsize=(10, 10),)
    q = ax.quiver(xi, yi, -ZIm, ZIl,headwidth=0)
    plt.show()
    print("orientations interpolated as dip dip direction",output_path+'interpolation_'+calc+'.csv')
    print("orientations interpolated as l,m,n dir cos",output_path+'interpolation_l.csv etc.')

######################################
# Interpolate 2D contact data from shapefile
# 
# interpolate_contacts(geology_file,tmp_path,dtm,bbox,c_l,use_gcode,scheme,gridx,gridy)
# geology_file path to basal contacts layer
# tmp_path directory of temporary outputs from m2l
# dtm rasterio format elevation grid
# bbox bounding box of region of interest
# c_l dictionary of codes and labels specific to input geo information layers
# use_gcode list of groups whose contact data will be interpolated scheme interpolation scheme one of 'simple_idw', 'scipy_idw', 'scipy_rbf'
# gridx,gridy number of cols & rows in interpolation grid
# 
# Interpolate basal contacts layer to produce regular grid of l,m direction cosines
######################################
def interpolate_contacts(geology_file,output_path,dtm,bbox,c_l,use_gcode,calc,gridx,gridy):
    geol_file = gpd.read_file(geology_file,bbox=bbox)
    #print(len(geol_file))
    geol_file.plot( color='black',edgecolor='black') 
    
    # Setup: Generate data...
    npts = 0
    decimate=1
    nx, ny = gridx,gridy

    xi = np.linspace(bbox[0],bbox[2], nx)
    yi = np.linspace(bbox[1],bbox[3], ny)
    xi, yi = np.meshgrid(xi, yi)
    xi, yi = xi.flatten(), yi.flatten()
    x = np.zeros(20000)   ############## FUDGE ################
    y = np.zeros(20000)
    l = np.zeros(20000)
    m = np.zeros(20000)
    f=open(output_path+'raw_contacts.csv','w')
    f.write("X,Y,Z,angle,lsx,lsy,formation,group\n")
    j=0
    i=0
    for acontact in geol_file.iterrows():   #loop through distinct linestrings in MultiLineString
        if(acontact[1].geometry.type=='MultiLineString'):
            #print(i)
            for line in acontact[1].geometry: # loop through line segments
                #print(i,len(acontact[1].geometry))
                if(m2l_utils.mod_safe(i,decimate)  ==0 and acontact[1][c_l['g']] in use_gcode):
                    #if(acontact[1]['id']==170): 
                        #display(npts,line.coords[0][0],line.coords[1][0]) 
                    dlsx=line.coords[0][0]-line.coords[1][0]
                    dlsy=line.coords[0][1]-line.coords[1][1]
                    if(not line.coords[0][0]==line.coords[1][0] or not line.coords[0][1]==line.coords[1][1]):               
                        lsx=dlsx/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                        lsy=dlsy/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                        x[i]=line.coords[1][0]+(dlsx/2)
                        y[i]=line.coords[1][1]+(dlsy/2)
                        angle=degrees(atan2(lsx,lsy))
                        l[i]=lsx
                        m[i]=lsy
                        locations=[(x[i],y[i])] #doesn't like point right on edge?
                        height=m2l_utils.value_from_raster(dtm,locations)
                        if(str(acontact[1][c_l['g']])=='None'):
                            ostr=str(x[i])+","+str(y[i])+","+str(height)+","+str(angle%180)+","+str(lsx)+","+str(lsy)+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+"\n"
                        else:
                            ostr=str(x[i])+","+str(y[i])+","+str(height)+","+str(angle%180)+","+str(lsx)+","+str(lsy)+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+","+acontact[1][c_l['g']].replace(" ","_").replace("-","_")+"\n"
                        f.write(ostr)
                        npts=npts+1
                i=i+1
        else:
            #display(acontact[1].geometry,acontact[1].geometry.coords)
            #for line in acontact[1]: # loop through line segments in LineString
            if(  m2l_utils.mod_safe(i,decimate)  ==0 and acontact[1][c_l['g']] in use_gcode):
                dlsx=acontact[1].geometry.coords[0][0]-acontact[1].geometry.coords[1][0]
                dlsy=acontact[1].geometry.coords[0][1]-acontact[1].geometry.coords[1][1]
                if(not acontact[1].geometry.coords[0][0]==acontact[1].geometry.coords[1][0] 
                   or not acontact[1].geometry.coords[0][1]==acontact[1].geometry.coords[1][1]):
                    lsx=dlsx/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                    lsy=dlsy/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                    x[i]=acontact[1].geometry.coords[1][0]+(dlsx/2)
                    y[i]=acontact[1].geometry.coords[1][1]+(dlsy/2)
                    angle=degrees(atan2(lsx,lsy))
                    l[i]=lsx
                    m[i]=lsy
                    locations=[(x[i],y[i])] #doesn't like point right on edge?
                    height=m2l_utils.value_from_raster(dtm,locations)
                    if(str(acontact[1][c_l['g']])=='None'):
                        ostr=str(x[i])+","+str(y[i])+","+str(height)+","+str(angle%180)+","+str(lsx)+","+str(lsy)+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+"\n"
                    else:
                        ostr=str(x[i])+","+str(y[i])+","+str(height)+","+str(angle%180)+","+str(lsx)+","+str(lsy)+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+","+acontact[1][c_l['g']].replace(" ","_").replace("-","_")+"\n"
                    #print(ostr)
                    f.write(ostr)
                    #print(npts,dlsx,dlsy)
                    npts=npts+1
                i=i+1
        j=j+1
    f.close()
    #print("i",i,"npts",npts)

    for i in range(0,npts):
        x[i]=x[i]+(np.random.ranf()*0.01)
        y[i]=y[i]+(np.random.ranf()*0.01)

    ZIl,ZIm,ZIn=call_interpolator(calc,x[:npts],y[:npts],l[:npts],m[:npts],0,xi,yi,nx,ny)    
    
    # Comparisons...
    plot(x,-y,l,ZIl)
    plt.title('l')
    plot(x,-y,m,ZIm)
    plt.title('m')

    fi=open(output_path+'interpolation_contacts_'+calc+'.csv','w')
    fl=open(output_path+'interpolation_contacts_l.csv','w')
    fm=open(output_path+'interpolation_contacts_m.csv','w')
    
    fi.write("x,y,angle\n")
    fl.write("x,y,l\n")
    fm.write("x,y,m\n")
    
    for xx in range (0,gridx):
        for yy in range (0,gridy):
            yyy=xx
            xxx=gridy-2-yy
            L=ZIl[xxx,yyy]/(sqrt((pow(ZIl[xxx,yyy],2.0))+(pow(ZIm[xxx,yyy],2.0))))
            M=ZIm[xxx,yyy]/(sqrt((pow(ZIl[xxx,yyy],2.0))+(pow(ZIm[xxx,yyy],2.0))))
            S=degrees(atan2(L,M))
    
            ostr=str(bbox[0]+(xx*((bbox[2]-bbox[0])/(gridx))))+","+str(bbox[1]+((gridy-2-yy)*((bbox[3]-bbox[1])/(gridy))))+","+str(int(S))+'\n'
            fi.write(ostr)
            
            ostr=str(xx)+","+str(yy)+","+str(L)+'\n'
            fl.write(ostr)
            ostr=str(xx)+","+str(yy)+","+str(M)+'\n'
            fm.write(ostr)
    fi.close()
    fl.close()
    fm.close()
    fig, ax = plt.subplots(figsize=(10, 10))
    q = ax.quiver(xi, yi, ZIl, ZIm,headwidth=0)
    plt.show()
    print("contacts interpolated as strike",output_path+'interpolation_contacts_'+calc+'.csv')
    print("contacts interpolated as l,m dir cos",output_path+'interpolation_contacts_l.csv etc.')

######################################
# save all contacts as vectors
######################################
def save_contact_vectors(geology_file,tmp_path,dtm,bbox,c_l,calc,decimate):
    geol_file = gpd.read_file(geology_file,bbox=bbox)
    print(len(geol_file))
    geol_file.plot( color='black',edgecolor='black') 
    
    npts = 0
    x = np.zeros(20000)
    y = np.zeros(20000)
    l = np.zeros(20000)
    m = np.zeros(20000)
    
    f=open(tmp_path+'raw_contacts.csv','w')
    f.write("X,Y,Z,angle,lsx,lsy,formation,group\n")
    j=0
    i=0
    for acontact in geol_file.iterrows():   #loop through distinct linestrings in MultiLineString
        if(acontact[1].geometry.type=='MultiLineString'):
            #print(i)
            for line in acontact[1].geometry: # loop through line segments
                #print(i,len(acontact[1].geometry))
                if(m2l_utils.mod_safe(i,decimate)  ==0):
                    #if(acontact[1]['id']==170): 
                        #display(npts,line.coords[0][0],line.coords[1][0]) 
                    dlsx=line.coords[0][0]-line.coords[1][0]
                    dlsy=line.coords[0][1]-line.coords[1][1]
                    if(not line.coords[0][0]==line.coords[1][0] or not line.coords[0][1]==line.coords[1][1]):               
                        lsx=dlsx/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                        lsy=dlsy/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                        x[i]=line.coords[1][0]+(dlsx/2)
                        y[i]=line.coords[1][1]+(dlsy/2)
                        angle=degrees(atan2(lsx,lsy))
                        l[i]=lsx
                        m[i]=lsy
                        locations=[(x[i],y[i])] #doesn't like point right on edge?
                        height=m2l_utils.value_from_raster(dtm,locations)
                        if(str(acontact[1][c_l['g']])=='None'):
                            ostr=str(x[i])+","+str(y[i])+","+str(height)+","+str(angle%180)+","+str(lsx)+","+str(lsy)+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+"\n"
                        else:
                            ostr=str(x[i])+","+str(y[i])+","+str(height)+","+str(angle%180)+","+str(lsx)+","+str(lsy)+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+","+acontact[1][c_l['g']].replace(" ","_").replace("-","_")+"\n"
                        f.write(ostr)
                        npts=npts+1
                i=i+1
        else:
            #display(acontact[1].geometry,acontact[1].geometry.coords)
            #for line in acontact[1]: # loop through line segments in LineString
            if(  m2l_utils.mod_safe(i,decimate)  ==0):
                dlsx=acontact[1].geometry.coords[0][0]-acontact[1].geometry.coords[1][0]
                dlsy=acontact[1].geometry.coords[0][1]-acontact[1].geometry.coords[1][1]
                if(not acontact[1].geometry.coords[0][0]==acontact[1].geometry.coords[1][0] 
                   or not acontact[1].geometry.coords[0][1]==acontact[1].geometry.coords[1][1]):
                    lsx=dlsx/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                    lsy=dlsy/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                    x[i]=acontact[1].geometry.coords[1][0]+(dlsx/2)
                    y[i]=acontact[1].geometry.coords[1][1]+(dlsy/2)
                    angle=degrees(atan2(lsx,lsy))
                    l[i]=lsx
                    m[i]=lsy
                    locations=[(x[i],y[i])] #doesn't like point right on edge?
                    height=m2l_utils.value_from_raster(dtm,locations)
                    if(str(acontact[1][c_l['g']])=='None'):
                        ostr=str(x[i])+","+str(y[i])+","+str(height)+","+str(angle%180)+","+str(lsx)+","+str(lsy)+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+"\n"
                    else:
                        ostr=str(x[i])+","+str(y[i])+","+str(height)+","+str(angle%180)+","+str(lsx)+","+str(lsy)+","+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+","+acontact[1][c_l['g']].replace(" ","_").replace("-","_")+"\n"
                    #print(ostr)
                    f.write(ostr)
                    #print(npts,dlsx,dlsy)
                    npts=npts+1
                i=i+1
        j=j+1
    f.close()
    print(npts,'points saved to',tmp_path+'raw_contacts.csv')


####################################
# combine interpolated contact information (to provide l,m with interpolated dip,dipdirection data (to provide n) 
#
# join_contacts_and_orientations(combo_file,geology_file,tmp_path,dtm_reproj_file,c_l,lo,mo,no,lc,mc,xy,dst_crs,bbox)
# combo_file path to temporary combined information geology_file path to basal contacts layer
# tmp_path directory of temporary outputs from m2l
# dtm_reproj_file path to reprojected dtm file
# c_l dictionary of codes and labels specific to input geo information layers
# lo,mo,no 3D direction cosines of interpolated orientations
# lc,mc 2D direction cosines of interpolated contacts
# xy interpolated orientations (used to get x,y locations only) dst_crs Coordinate Reference System of destination geotif (any length-based projection)
# bbox bounding box of region of interest
# 
# Combine interpolation orientations with interpolated basal contacts layers to produce regular grid of interpolated dip, dip direction estimates
# Uses normalised direction cosines (l,m,n):
# -- l,m from RBF of basal contact orientations -- signs of l & m from misorientation with RBF of orientation data and -- n from RBF of orientation data
# 
# Useful for adding data where no orientations are available (e.g. in fault bounded domains) and for calculating true thickness of layers. Assumes a 2D plane of data, but if 3D RBF was calulated and projected contact info was used it should apply with topography too.
####################################    
def join_contacts_and_orientations(combo_file,geology_file,output_path,dtm_reproj_file,c_l,lo,mo,no,lc,mc,xy,dst_crs,bbox):
    f=open(combo_file,'w')
    f.write('x,y,dip,dipdirection,misorientation,dotproduct\n')

    for i in range(0,len(lc)):
        scale=sqrt(1-pow(no[i,2],2)) #scaling contact dircos to *include* dip info
        lcscaled=scale*-mc[i,2] #includes 90 rotation to account for orthogonality of contact and dip direction
        mcscaled=scale*lc[i,2]
        scale2=sqrt(pow(lo[i,2],2)+pow(mo[i,2],2)) #scaling dip dipdir dircos to *exclude* dip info
        loscaled=lo[i,2]/scale2
        moscaled=mo[i,2]/scale2
        dotproduct=(-mc[i,2]*loscaled)+(lc[i,2]*moscaled) #includes 90 rotation to account for orthogonality of contact and dip direction
        if(dotproduct<0):
            lcscaled=-lcscaled
            mcscaled=-mcscaled
        misorientation=degrees(acos(dotproduct))
        dip,dipdir=m2l_utils.dircos2ddd(lcscaled,mcscaled,no[i,2])
        ostr=str(xy[i,0])+','+str(xy[i,1])+','+str(int(dip))+','+str(int(dipdir))+','+str(int(misorientation))+','+str(dotproduct)+'\n'
        f.write(ostr)
    f.close()   
    
    
    geology = gpd.read_file(geology_file,bbox=bbox)
    geology.crs=dst_crs
    geology = m2l_utils.explode(geology)
    
    data = pd.read_csv(combo_file)
    
    geometry = [Point(xy) for xy in zip(data['x'], data['y'])]
        
    gdf = GeoDataFrame(data, crs=dst_crs, geometry=geometry)
    
    gdf.crs=dst_crs
    print(gdf.crs,geology.crs)    
    structure_code = gpd.sjoin(gdf, geology, how="left", op="within")
    dtm = rasterio.open(dtm_reproj_file)
    f=open(output_path+'combo_full.csv','w')
    f.write('X,Y,Z,azimuth,dip,polarity,formation\n')
    for a_point in structure_code.iterrows():
        locations=[(a_point[1]['x'],a_point[1]['y'])]
        height=m2l_utils.value_from_raster(dtm,locations)
        ostr=str(a_point[1]['x'])+','
        ostr=ostr+str(a_point[1]['y'])+','
        ostr=ostr+str(height)+','+str(int(a_point[1]['dipdirection']))+','
        ostr=ostr+str(int(a_point[1]['dip']))+',1,'
        ostr=ostr+str(a_point[1][c_l['c']]).replace("-","_")+'\n'

        if(not str(a_point[1][c_l['c']])=='nan'):
            f.write(ostr)
    f.close()  
    print("contacts and orientations interpolated as dip dip direction",output_path+'combo_full.csv')
 