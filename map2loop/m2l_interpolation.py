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
import m2l_utils 
import rasterio

#inspired by https://stackoverflow.com/questions/3104781/inverse-distance-weighted-idw-interpolation-with-python

def simple_idw(x, y, z, xi, yi):
    dist = distance_matrix(x,y, xi,yi)

    # In IDW, weights are 1 / distance
    weights = 1.0 / (dist)

    # Make weights sum to one
    weights /= weights.sum(axis=0)

    # Multiply the weights for each interpolated point by all observed Z-values
    zi = np.dot(weights.T, z)
    return zi

def scipy_idw(x, y, z, xi, yi):
    interp = Rbf(x, y, z, function='linear')
    return interp(xi, yi)

def scipy_rbf(x, y, z, xi, yi):
    interp = Rbf(x, y, z, epsilon=1)
    return interp(xi, yi)

def distance_matrix(x0, y0, x1, y1):
    obs = np.vstack((x0, y0)).T
    interp = np.vstack((x1, y1)).T

    # Make a distance matrix between pairwise observations
    # Note: from <http://stackoverflow.com/questions/1871536>
    # (Yay for ufuncs!)
    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])

    return np.hypot(d0, d1)


def plot(x,y,z,grid):
    plt.figure()
    plt.imshow(grid, extent=(0,100,0,100))
    #plt.hold(True)
    #plt.scatter(x,100-y,c=z)
    plt.colorbar()
    
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
    ZIl = ZIl.reshape((ny-1, nx-1))
    
    if(calc=='simple_idw'):
        ZIm = simple_idw(x,y,m,xi,yi)
    if(calc=='scipy_rbf'):
        ZIm = scipy_rbf(x,y,m,xi,yi)
    if(calc=='scipy_idw'):
        ZIm = scipy_idw(x,y,m,xi,yi)
    ZIm = ZIm.reshape((ny-1, nx-1))
    
    if(type(n) is not int):
        if(calc=='simple_idw'):
            ZIn = simple_idw(x,y,n,xi,yi)
        if(calc=='scipy_rbf'):
            ZIn = scipy_rbf(x,y,n,xi,yi)
        if(calc=='scipy_idw'):
            ZIn = scipy_idw(x,y,n,xi,yi)
        ZIn = ZIn.reshape((ny-1, nx-1))   
    else:
        ZIn=0
        
    return(ZIl,ZIm,ZIn)
     
def interpolate_orientations(structure_file,output_path,bbox,dcode,ddcode,gcode,this_gcode,calc,gridx,gridy):
    print(structure_file,output_path,bbox,dcode,ddcode,gcode,this_gcode,calc,gridx,gridy)
    structure = gpd.read_file(structure_file,bbox=bbox)
    
    if(len(this_gcode)==1):       
        is_gp=structure[gcode] == thisgcode # subset orientations to just those with this group
        gp_structure = structure[is_gp]
    else:
        is_gp=structure[gcode] == this_gcode[0] # subset orientations to just those with this group
        gp_structure = structure[is_gp]
        gp_structure_all = gp_structure.copy()
        
        for i in range (1,len(this_gcode)):
            is_gp=structure[gcode] == this_gcode[i] # subset orientations to just those with this group
            temp_gp_structure = structure[is_gp]
            gp_structure_all = pd.concat([gp_structure_all, temp_gp_structure], ignore_index=True)
    

    npts = len(gp_structure_all)
    
    nx, ny = gridx,gridy

    xi = np.linspace(bbox[0],bbox[2], nx-1)
    yi = np.linspace(bbox[1],bbox[3], ny-1)
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
        dip[i] = a_pt[1][dcode]
        dipdir[i] = a_pt[1][ddcode]
        i=i+1
    
    l=np.zeros(npts)
    m=np.zeros(npts)
    n=np.zeros(npts)
    
    for i in range(0,npts):
        l[i],m[i],n[i]=m2l_utils.ddd2dircos(dip[i],dipdir[i])

    ZIl,ZIm,ZIn=call_interpolator(calc,x,y,l,m,n,xi,yi,nx,ny)
    
    # Comparisons...
    plot(x,y,l,ZIl)
    plt.title('l')
    plot(x,y,m,ZIm)
    plt.title('m')
    plot(x,y,n,ZIn)
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
    
    for xx in range (0,gridx-1):
        for yy in range (0,gridy-1):
            yyy=xx
            xxx=gridy-2-yy
            L=ZIl[xxx,yyy]/(sqrt((pow(ZIl[xxx,yyy],2.0))+(pow(ZIm[xxx,yyy],2.0))+(pow(ZIn[xxx,yyy],2.0))))
            M=ZIm[xxx,yyy]/(sqrt((pow(ZIl[xxx,yyy],2.0))+(pow(ZIm[xxx,yyy],2.0))+(pow(ZIn[xxx,yyy],2.0))))
            N=ZIn[xxx,yyy]/(sqrt((pow(ZIl[xxx,yyy],2.0))+(pow(ZIm[xxx,yyy],2.0))+(pow(ZIn[xxx,yyy],2.0))))
            
            dip,dipdir=m2l_utils.dircos2ddd(L,M,N)

            ostr=str(bbox[0]+(xx*((bbox[2]-bbox[0])/gridx+1)))+","+str(bbox[1]+((gridy-1-yy)*((bbox[3]-bbox[1])/gridy+1)))+","+str(int(dip))+","+str(int(dipdir))+'\n'
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

def interpolate_contacts(geology_file,output_path,bbox,dcode,ddcode,gcode,calc,gridx,gridy):
    print(geology_file,output_path,bbox,dcode,ddcode,gcode,calc,gridx,gridy)
    geol_file = gpd.read_file(geology_file,bbox=bbox)
    print(len(geol_file))
    geol_file.plot( color='black',edgecolor='black') 
    
    # Setup: Generate data...
    npts = 0
    decimate=1
    nx, ny = gridx,gridy

    xi = np.linspace(bbox[0],bbox[2], nx-1)
    yi = np.linspace(bbox[1],bbox[3], ny-1)
    xi, yi = np.meshgrid(xi, yi)
    xi, yi = xi.flatten(), yi.flatten()
    x = np.zeros(10000)
    y = np.zeros(10000)
    l = np.zeros(10000)
    m = np.zeros(10000)
    f=open(output_path+'raw_contacts.csv','w')
    f.write("x,y,angle,lsx,lsy\n")
    j=0
    i=0
    for acontact in geol_file.iterrows():   #loop through distinct linestrings in MultiLineString
        if(acontact[1].geometry.type=='MultiLineString'):
            #print(i)
            for line in acontact[1].geometry: # loop through line segments
                #print(i,len(acontact[1].geometry))
                if(i%decimate ==0):
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
                        ostr=str(x[i])+","+str(y[i])+","+str(angle%180)+","+str(lsx)+","+str(lsy)+"\n"
                        #print(ostr)
                        f.write(ostr)
                        npts=npts+1
                i=i+1
        else:
            #display(acontact[1].geometry,acontact[1].geometry.coords)
            #for line in acontact[1]: # loop through line segments in LineString
            if(  i%decimate ==0):
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
                    ostr=str(x[i])+","+str(y[i])+","+str(angle%180)+","+str(lsx)+","+str(lsy)+"\n"
                    #print(ostr)
                    f.write(ostr)
                    print(npts,dlsx,dlsy)
                    npts=npts+1
                i=i+1
        j=j+1
    f.close()
    print("i",i,"npts",npts)

    for i in range(0,npts):
        x[i]=x[i]+(np.random.ranf()*0.01)
        y[i]=y[i]+(np.random.ranf()*0.01)

    ZIl,ZIm,ZIn=call_interpolator(calc,x[:npts],y[:npts],l[:npts],m[:npts],0,xi,yi,nx,ny)    
    
    # Comparisons...
    plot(x,y,l,ZIl)
    plt.title('l')
    plot(x,y,m,ZIm)
    plt.title('m')

    fi=open(output_path+'interpolation_contacts_'+calc+'.csv','w')
    fl=open(output_path+'interpolation_contacts_l.csv','w')
    fm=open(output_path+'interpolation_contacts_m.csv','w')
    
    fi.write("x,y,angle\n")
    fl.write("x,y,l\n")
    fm.write("x,y,m\n")
    
    for xx in range (0,gridx-1):
        for yy in range (0,gridy-1):
            yyy=xx
            xxx=gridy-2-yy
            L=ZIl[xxx,yyy]/(sqrt((pow(ZIl[xxx,yyy],2.0))+(pow(ZIm[xxx,yyy],2.0))))
            M=ZIm[xxx,yyy]/(sqrt((pow(ZIl[xxx,yyy],2.0))+(pow(ZIm[xxx,yyy],2.0))))
            S=degrees(atan2(L,M))
    
            ostr=str(bbox[0]+(xx*((bbox[2]-bbox[0])/100)))+","+str(bbox[1]+((gridy-2-yy)*((bbox[3]-bbox[1])/100)))+","+str(int(S))+'\n'
            fi.write(ostr)
            
            ostr=str(xx)+","+str(yy)+","+str(L)+'\n'
            fl.write(ostr)
            ostr=str(xx)+","+str(yy)+","+str(M)+'\n'
            fm.write(ostr)
    fi.close()
    fl.close()
    fm.close()
    fig, ax = plt.subplots(figsize=(10, 10))
    q = ax.quiver(xi, yi, -ZIm, ZIl,headwidth=0)
    plt.show()
    
def join_contacts_and_orientations(combo_file,geology_file,output_path,dtm_reproj_file,ccode,lo,mo,no,lc,mc,xy,dst_crs,bbox):
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
        ostr=ostr+str(a_point[1][ccode]).replace("-","_")+'\n'

        if(not str(a_point[1][ccode])=='nan'):
            f.write(ostr)
    f.close()   