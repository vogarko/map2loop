from shapely import geometry
from shapely.geometry import shape, Polygon, LineString, Point
import matplotlib.pyplot as plt
import requests
import rasterio
from pandas import DataFrame
from geopandas import GeoDataFrame
import geopandas as gpd
import pandas as pd
from math import acos, sqrt, cos, sin, degrees, radians, fabs, atan2
from map2loop import m2l_utils
from map2loop import m2l_interpolation
import numpy as np

####################################################
# Export orientation data in csv format with heights and strat code added
####################################################
def save_orientations(structures,path_out,c_l,orientation_decimate,dtm):
    i=0
    f=open(path_out+'/orientations.csv',"w")
    f.write("X,Y,Z,azimuth,dip,polarity,formation\n")
    for apoint in structures.iterrows():
        if(not c_l['intrusive'] in apoint[1][c_l['r1']]):
            if(apoint[1][c_l['d']]!=0 and m2l_utils.mod_safe(i,orientation_decimate)==0):
                locations=[(apoint[1]['geometry'].x, apoint[1]['geometry'].y)]
                if(apoint[1]['geometry'].x > dtm.bounds[0] and apoint[1]['geometry'].x < dtm.bounds[2] and  
                    apoint[1]['geometry'].y > dtm.bounds[1] and apoint[1]['geometry'].y < dtm.bounds[3]):       
                    height=m2l_utils.value_from_raster(dtm,locations)
                    ostr=str(apoint[1]['geometry'].x)+","+str(apoint[1]['geometry'].y)+","+height+","+str(apoint[1][c_l['dd']])+","+str(apoint[1][c_l['d']])+",1,"+str(apoint[1][c_l['c']].replace(" ","_").replace("-","_"))+"\n"
                    f.write(ostr)
                    i+=1
        
    f.close()
    print(i,'orientations saved to',path_out+'/orientations.csv')

####################################################
# Find those series that don't have any orientation or contact point data and add some random data
####################################################
def create_orientations( path_in, path_out,dtm,geology,structures,c_l):
    #f=open(path_in+'/groups.csv',"r")
    #contents =f.readlines()
    #f.close

    #ngroups=contents[0].split(" ")
    #ngroups=int(ngroups[1])
    contents=np.genfromtxt(path_in+'groups.csv',delimiter=',',dtype='U25')
    ngroups=len(contents[0])-1
    print(len(contents[0]))
    groups=[]
    for i in range (1,int(ngroups)+1):
        print(contents[0][i].replace("\n",""))
        groups.append((contents[0][i].replace("\n",""),0))

    print(ngroups,groups)

    for i in range (1,ngroups):
        for apoint in structures.iterrows():
            if(str(apoint[1][c_l['g']])=='None'):
                agroup=apoint[1][c_l['c']].replace(" ","_").replace("-","_")
            else:
                agroup=apoint[1][c_l['g']].replace(" ","_").replace("-","_")
            #print(agroup)
            if(groups[i][0]==agroup):
                lgroups=list(groups[i])
                lgroups[1]=1
                lgroups=tuple(lgroups)
                groups[i]=lgroups

    print("Orientations----------\n",ngroups,groups)

    for i in range (0,ngroups):
        for apoly in geology.iterrows():
            agroup=apoint[1][c_l['g']].replace(" ","_").replace("-","_")
            #print(agroup)
            if(groups[i][0]==agroup):
                lgroups=list(groups[i])
                lgroups[1]=1
                lgroups=tuple(lgroups)
                groups[i]=lgroups

    all_codes=[]
    for ageol in geology.iterrows(): # central polygon
            all_codes.append(ageol[1][c_l['c']])

    print("Contacts----------\n",len(set(all_codes)),set(all_codes))

    f=open(path_out+'/empty_series_orientations.csv',"w")
    #f.write("X,Y,Z,azimuth,dip,polarity,formation\n")
    f.write("X,Y,Z,DipDirection,dip,dippolarity,formation\n")

    for i in range (0,ngroups):
        if(groups[i][1]==0):
            for ageol in geology.iterrows():
                if(ageol[1][c_l['c']].replace("-","_")==groups[i][0] and groups[i][1]==0 and not c_l['intrusive'] in ageol[1][c_l['r1']] ):
                    apoly=Polygon(ageol[1]['geometry'])
                    apoint=apoly.representative_point()
                    #print(apoint.x,apoint.y)
                    locations=[(apoint.x,apoint.y)]
                    height=m2l_utils.value_from_raster(dtm,locations)
                    if(height==-999):
                        print("point off map",locations)
                        height=0   # needs a better solution!
                    ostr=str(apoint.x)+","+str(apoint.y)+","+height+",0,45,1"+","+str(ageol[1][c_l['c']].replace(" ","_").replace("-","_"))+"\n"
                    f.write(ostr)
                    #plt.title(str(ageol[1][c_l['c']].replace(" ","_").replace("-","_")))
                    #plt.scatter(apoint.x,apoint.y,color="red")
                    #plt.plot(*apoly.exterior.xy)
                    #plt.show()
                    break

    f.close()
    print('extra orientations saved as',path_out+'/empty_series_orientations.csv')

####################################################
# Convert polygons with holes into distinct poygons
#modified from https://stackoverflow.com/questions/21824157/how-to-extract-interior-polygon-coordinates-using-shapely
####################################################
def extract_poly_coords(geom,i):

    if geom.type == 'Polygon':
        exterior_coords = geom.exterior.coords[:]
        interior_coords = []
        for interior in geom.interiors:
            interior_coords += (i,interior.coords[:])
            i=i+1

    elif geom.type == 'MultiPolygon':
        exterior_coords = []
        interior_coords = []
        for part in geom:
            epc = extract_poly_coords(part,i)  # Recursive call
            exterior_coords += epc['exterior_coords']
            interior_coords += epc['interior_coords']
            i=i+1
    else:
        raise ValueError('Unhandled geometry type: ' + repr(geom.type))
    return {'exterior_coords': exterior_coords,
            'interior_coords': interior_coords}

####################################################
# extract stratigraphically lower contacts from geology polygons and save as points
####################################################
def save_basal_contacts(path_in,dtm,geol_clip,contact_decimate,c_l,intrusion_mode):
    print("decimation: 1 /",contact_decimate)
    plist=[]
    i=0
    all_geom=m2l_utils.explode(geol_clip)

    #print(type(all_geom))

    for ageol in all_geom.iterrows(): # central polygon
        all_coords=extract_poly_coords(ageol[1].geometry,0)
        plist+=(i,list(all_coords['exterior_coords']),ageol[1][c_l['c']],ageol[1][c_l['ds']],ageol[1][c_l['g']],ageol[1][c_l['r1']],ageol[1][c_l['o']])
        i=i+1
        for j in range(0,len(all_coords['interior_coords']),2):
            plist+=(i,list(all_coords['interior_coords'][j+1]),ageol[1][c_l['c']],ageol[1][c_l['ds']],ageol[1][c_l['g']],ageol[1][c_l['r1']],ageol[1][c_l['o']])
            i=i+1
               
    #dataset = rasterio.open(path_in+'/dtm_rp.tif')
    ag=open(path_in+'/all_sorts.csv',"r")
    contents =ag.readlines()
    ag.close
    print("surfaces:",len(contents))
    print("polygons:",len(all_geom))
    ulist=[]
    for i in range(1,len(contents)):
        #print(contents[i].replace("\n",""))
        cont_list=contents[i].split(",")
        ulist.append([i, cont_list[4].replace("\n","")])
    print(ulist)

    allc=open(path_in+'/all_contacts.csv',"w")
    allc.write('GROUP_,id,x,y,z,code\n')
    ac=open(path_in+'/contacts.csv',"w")
    ac.write("X,Y,Z,formation\n")
    print(dtm.bounds)
    j=0
    allpts=0
    deci_points=0
    ls_dict={}
    ls_dict_decimate={}
    id=0
    #print(len(plist))
    for a_poly in range(0,len(plist),7):
        if( not 'intrusive' in plist[a_poly+5]):
            a_polygon=Polygon(plist[a_poly+1])
            agp=str(plist[a_poly+4])
            if(agp=='None'):
                agp=plist[a_poly+2].replace(" ","_").replace("-","_")

            neighbours=[]
            j+=1
            out=[item for item in ulist if plist[a_poly+2].replace(" ","_").replace("-","_") in item]
            if(len(out)>0):
                central=out[0][0]    #relative age of central polygon

                for b_poly in range(0,len(plist),7):
                    b_polygon=LineString(plist[b_poly+1])

                    if(plist[a_poly] != plist[b_poly]): #do not compare with self

                        if (a_polygon.intersects(b_polygon)) : # is a neighbour, but not a sill
                           if(  (not c_l['sill'] in plist[b_poly+3] or not c_l['intrusive'] in plist[b_poly+5]) and intrusion_mode==0): #intrusion_mode=0 (sills only excluded)
                                 neighbours.append((b_poly))                               
                           elif((not c_l['intrusive'] in plist[b_poly+5])  and intrusion_mode==1): #intrusion_mode=1 (all intrusions  excluded)
                                 neighbours.append((b_poly))                               


                if(len(neighbours) >0):
                    for i in range (0,len(neighbours)):
                        b_polygon=LineString(plist[neighbours[i]+1])

                        out=[item for item in ulist if plist[neighbours[i]+2].replace(" ","_").replace("-","_")  in item]

                        if(len(out)>0):
                            #if(out[0][0] > central and out[0][0] < youngest_older): # neighbour is older than central, and younger than previous candidate
                            if(out[0][0] > central  ): # neighbour is older than central

                                if(not a_polygon.is_valid ):
                                    a_polygon = a_polygon.buffer(0)
                                if(not b_polygon.is_valid):
                                    b_polygon = b_polygon.buffer(0)                                    
                                LineStringC = a_polygon.intersection(b_polygon)

                                if(LineStringC.wkt.split(" ")[0]=='GEOMETRYCOLLECTION' ): #ignore weird intersections for now, worry about them later!
                                    #print("debug:GC")
                                    continue
                                elif(LineStringC.wkt.split(" ")[0]=='MULTIPOLYGON' or
                                     LineStringC.wkt.split(" ")[0]=='POLYGON'):
                                         print("debug:MP,P",ageol[1][c_l['c']])

                                elif(LineStringC.wkt.split(" ")[0]=='MULTILINESTRING'):
                                    k=0

                                    if(str(plist[a_poly+4])=='None'):
                                        ls_dict[id] = {"id": id,c_l['c']:plist[a_poly+2].replace(" ","_").replace("-","_"),c_l['g']:plist[a_poly+2].replace(" ","_").replace("-","_"), "geometry": LineStringC}
                                    else:
                                        ls_dict[id] = {"id": id,c_l['c']:plist[a_poly+2].replace(" ","_").replace("-","_"),c_l['g']:plist[a_poly+4].replace(" ","_").replace("-","_"), "geometry": LineStringC}
                                    id=id+1
                                    for lineC in LineStringC: #process all linestrings
                                        if(m2l_utils.mod_safe(k,contact_decimate)==0 or k==int((len(LineStringC)-1)/2) or k==len(LineStringC)-1): #decimate to reduce number of points, but also take second and third point of a series to keep gempy happy
                                            locations=[(lineC.coords[0][0],lineC.coords[0][1])] #doesn't like point right on edge?
                                            if(lineC.coords[0][0] > dtm.bounds[0] and lineC.coords[0][0] < dtm.bounds[2] and  
                                               lineC.coords[0][1] > dtm.bounds[1] and lineC.coords[0][1] < dtm.bounds[3]):       
                                                    height=m2l_utils.value_from_raster(dtm,locations)
                                                    ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+height+","+str(plist[a_poly+2].replace(" ","_").replace("-","_"))+"\n"
                                                    ac.write(ostr)
                                                    allc.write(agp+","+str(ageol[1][c_l['o']])+","+ostr)
                                                    if(str(plist[a_poly+4])=='None'):
                                                        ls_dict_decimate[deci_points] = {"id": allpts,c_l['c']:plist[a_poly+2].replace(" ","_").replace("-","_"),c_l['g']:plist[a_poly+2].replace(" ","_").replace("-","_"), "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                                    else:
                                                        ls_dict_decimate[deci_points] = {"id": allpts,c_l['c']:plist[a_poly+2].replace(" ","_").replace("-","_"),c_l['g']:plist[a_poly+4].replace(" ","_").replace("-","_"), "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                                    allpts+=1 
                                                    deci_points=deci_points+1
                                            else:
                                                continue
                                                #print("debug:edge points")
                                        else:
                                            locations=[(lineC.coords[0][0]+0.0000001,lineC.coords[0][1])] #doesn't like point right on edge?
                                            if(lineC.coords[0][0] > dtm.bounds[0] and lineC.coords[0][0] < dtm.bounds[2] and  
                                                lineC.coords[0][1] > dtm.bounds[1] and lineC.coords[0][1] < dtm.bounds[3]):       
                                                height=m2l_utils.value_from_raster(dtm,locations)
                                                ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+height+","+str(plist[a_poly+2].replace(" ","_").replace("-","_"))+"\n"
                                                allc.write(agp+","+str(ageol[1][c_l['o']])+","+ostr)
                                                allpts+=1    
                                        k+=1
                                elif(LineStringC.wkt.split(" ")[0]=='LINESTRING'): # apparently this is not needed
                                    k=0
                                    for pt in LineStringC.coords: #process one linestring
                                        k+=1
                                elif(LineStringC.wkt.split(" ")[0]=='POINT'): # apparently this is not needed
                                    #print("debug:POINT")
                                    k=0
                                    k+=1
                                else:
                                    k=0
                                    k+=1


    ac.close()
    allc.close()
    print("basal contacts saved allpts=",allpts,"deci_pts=",deci_points)
    print("saved as",path_in+'all_contacts.csv',"and",path_in+'contacts.csv')
    return(ls_dict,ls_dict_decimate)

#########################################
# Remove all basal contacts that are defined by faults and save to shapefile (no decimation)
#########################################
def save_basal_no_faults(path_out,path_fault,ls_dict,dist_buffer,c_l,dst_crs):
    faults_clip = gpd.read_file(path_fault)


    df = DataFrame.from_dict(ls_dict, "index")
    contacts = GeoDataFrame(df,crs=dst_crs, geometry='geometry')

    fault_zone = faults_clip.buffer(dist_buffer) #defines buffer around faults where strat nodes will be removed
    all_fz = fault_zone.unary_union

    contacts_nofaults = contacts.difference(all_fz) #deletes contact nodes within buffer
    ls_nf={}

    cnf_copy=contacts_nofaults.copy()

    print(contacts_nofaults.shape)
    for i in range(0,len(contacts_nofaults)): 
        j=len(contacts_nofaults)-i-1
        #print(j)
        if(cnf_copy.iloc[j].geom_type=="GeometryCollection"):#remove rows with geometry collections (== empty?)
            cnf_copy.drop([j,j],inplace=True)
        else: # save to dataframe
            ls_nf[j]= {"id": j,c_l['c']:df.iloc[j][c_l['c']].replace(" ","_").replace("-","_"),c_l['g']:df.iloc[j][c_l['g']].replace(" ","_").replace("-","_"), "geometry": cnf_copy.iloc[j]}



    df_nf = DataFrame.from_dict(ls_nf, "index")

    contacts_nf = GeoDataFrame(df_nf,crs=dst_crs, geometry='geometry')
    contacts_nf.to_file(driver = 'ESRI Shapefile', filename= path_out)

    #contacts_nofaults = gpd.read_file('./data/faults_clip.shp')
    print("basal contacts without faults saved as",path_out)

#########################################
# Save basal contacts from shapefile with decimation
#########################################
def save_basal_contacts_csv(contacts,output_path,dtm,contact_decimate):
    f=open(output_path+'contacts4.csv','w')
    f.write('X,Y,Z,formation\n')
    for index,contact in contacts.iterrows():
        i=0
        lastx,lasty=-1e7,-1e7
        first=True
        if contact.geometry.type == 'MultiLineString':
            for line in contact.geometry: 
                if(line.coords[0][0]==lastx and line.coords[0][1]==lasty): #continuation of line
                    if(m2l_utils.mod_safe(i,contact_decimate)==0 or i==int((len(contact.geometry)-1)/2) or i==len(contact.geometry)-1):
                        locations=[(line.coords[0][0],line.coords[0][1])]
                        height=m2l_utils.value_from_raster(dtm,locations)
                        ostr=str(line.coords[0][0])+','+str(line.coords[0][1])+','+str(height)+','+str(contact.CODE)+'\n'
                        f.write(ostr)
                else: #new line
                    if(not first):
                        locations=[(lastx,lasty)]
                        height=m2l_utils.value_from_raster(dtm,locations)                        
                        ostr=str(lastx)+','+str(lasty)+','+str(height)+','+str(contact.CODE)+'\n'
                        f.write(ostr)
                    locations=[(line.coords[0][0],line.coords[0][1])]
                    height=m2l_utils.value_from_raster(dtm,locations)                        
                    ostr=str(line.coords[0][0])+','+str(line.coords[0][1])+','+str(height)+','+str(contact.CODE)+'\n'
                    f.write(ostr)
                    first=False
                i=i+1
                lastx=line.coords[1][0]
                lasty=line.coords[1][1]

        elif contact.geometry.type == 'LineString':
            locations=[(contact.geometry.coords[0][0],contact.geometry.coords[0][1])]
            height=m2l_utils.value_from_raster(dtm,locations)                        
            ostr=str(contact.geometry.coords[0][0])+','+str(contact.geometry.coords[0][1])+','+str(height)+','+str(contact.CODE)+'\n'
            f.write(ostr)
            locations=[(contact.geometry.coords[1][0],contact.geometry.coords[1][1])]
            height=m2l_utils.value_from_raster(dtm,locations)                        
            ostr=str(contact.geometry.coords[1][0])+','+str(contact.geometry.coords[1][1])+','+str(height)+','+str(contact.CODE)+'\n'
            f.write(ostr)
    f.close()
    print('decimated contacts saved as',output_path+'contacts4.csv')
    
#########################################
# Remove faults from decimated basal contacts as save as csv file   (superceded by save_basal_contacts_csv)
#########################################
def save_contacts_with_faults_removed(path_fault,path_out,dist_buffer,ls_dict,ls_dict_decimate,c_l,dst_crs,dataset):
    faults_clip = gpd.read_file(path_fault)

    df = DataFrame.from_dict(ls_dict, "index")
    contacts = GeoDataFrame(df,crs=dst_crs, geometry='geometry')
    fault_zone = faults_clip.buffer(dist_buffer) #defines buffer around faults where strat nodes will be removed
    all_fz = fault_zone.unary_union
    #display(all_fz)
    print("undecimated points:",len(ls_dict_decimate))
    df_nf = DataFrame.from_dict(ls_dict_decimate, "index")

    contacts_nf_deci = GeoDataFrame(df_nf,crs=dst_crs, geometry='geometry')
    
    #contacts_decimate_nofaults = contacts_nf_deci.difference(all_fz) #deletes contact nodes within buffer
    
    contacts_decimate_nofaults = contacts_nf_deci[~contacts_nf_deci.geometry.within(all_fz)]
    
    cnf_de_copy=contacts_decimate_nofaults.copy()
    
    ac=open(path_out+'/contacts4.csv',"w")
    ac.write("X,Y,Z,formation\n")
    i=0
    for cdn in contacts_decimate_nofaults.iterrows():
        if(not cdn[1].geometry.geom_type=="GeometryCollection"):
            #print(cdn.x,cdn.y)
            locations=[(cdn[1].geometry.x,cdn[1].geometry.y)] #doesn't like point right on edge?
          
            height=m2l_utils.value_from_raster(dataset,locations)
            ostr=str(cdn[1].geometry.x)+","+str(cdn[1].geometry.y)+","+height+","+str(cdn[1][c_l['c']].replace(" ","_").replace("-","_"))+"\n"
            ac.write(ostr)

        i=i+1
    ac.close()
    print(i,"decimated contact points saved as",path_out+'/contacts4.csv')
    
#########################################
# Save faults as contact info and make vertical (for the moment)
#########################################  
def save_faults(path_faults,path_fault_orientations,dataset,c_l,fault_decimate,fault_min_len):
    faults_clip=gpd.read_file(path_faults)
    f=open(path_fault_orientations+'/faults.csv',"w")
    f.write("X,Y,Z,formation\n")
    fo=open(path_fault_orientations+'/fault_orientations.csv',"w")
    fo.write("X,Y,Z,DipDirection,dip,DipPolarity,formation\n")
    #fo.write("X,Y,Z,azimuth,dip,polarity,formation\n")
    fd=open(path_fault_orientations+'/fault_dimensions.csv',"w")
    fd.write("Fault,HorizontalRadius,VerticalRadius,InfluenceDistance\n")
    #fd.write("Fault_ID,strike,dip_direction,down_dip\n")

    for flt in faults_clip.iterrows():
        if(c_l['fault'] in flt[1][c_l['f']]):
            fault_name='Fault_'+str(flt[1][c_l['o']])
            flt_ls=LineString(flt[1].geometry)
            dlsx=flt_ls.coords[0][0]-flt_ls.coords[len(flt_ls.coords)-1][0]
            dlsy=flt_ls.coords[0][1]-flt_ls.coords[len(flt_ls.coords)-1][1]
            strike=sqrt((dlsx*dlsx)+(dlsy*dlsy))
            if(strike>fault_min_len):
                i=0
                for afs in flt_ls.coords:
                    if(m2l_utils.mod_safe(i,fault_decimate)==0 or i==int((len(flt_ls.coords)-1)/2) or i==len(flt_ls.coords)-1): #decimate to reduce number of points, but also take mid and end points of a series to keep some shape
                        locations=[(afs[0],afs[1])]     
                        height=m2l_utils.value_from_raster(dataset,locations)
                        ostr=str(afs[0])+","+str(afs[1])+","+str(height)+","+fault_name+"\n"
                        f.write(ostr)                
                    i=i+1  
                if(dlsx==0.0 or dlsy == 0.0):
                    continue
                lsx=dlsx/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                lsy=dlsy/sqrt((dlsx*dlsx)+(dlsy*dlsy))        
                azimuth=degrees(atan2(lsy,-lsx)) % 180 #normal to line segment           
                locations=[(flt_ls.coords[int((len(afs)-1)/2)][0],flt_ls.coords[int((len(afs)-1)/2)][1])]     
                height=m2l_utils.value_from_raster(dataset,locations)
                ostr=str(flt_ls.coords[int((len(flt_ls.coords)-1)/2)][0])+","+str(flt_ls.coords[int((len(flt_ls.coords)-1)/2)][1])+","+height+","+str(azimuth)+",90,1,"+fault_name+"\n"
                fo.write(ostr)
                ostr=fault_name+","+str(strike)+","+str(strike)+","+str(strike/2.0)+"\n"
                fd.write(ostr)

    f.close()
    fo.close()
    fd.close()
    print("fault orientations saved as",path_fault_orientations+'fault_orientations.csv')
    print("fault positions saved as",path_fault_orientations+'faults.csv')
    print("fault dimensions saved as",path_fault_orientations+'fault_dimensions.csv')
    
#Save fold axial traces 
def save_fold_axial_traces(path_folds,path_fold_orientations,dataset,c_l,fold_decimate):
    folds_clip=gpd.read_file(path_folds)
    fo=open(path_fold_orientations+'/fold_axial_traces.csv',"w")
    fo.write("X,Y,Z,code,type\n")

    for fold in folds_clip.iterrows():
        fold_name=str(fold[1][c_l['o']])   
        fold_ls=LineString(fold[1].geometry)

        i=0
        for afs in fold_ls.coords:
            if(c_l['fold'] in fold[1][c_l['f']]):
                if(m2l_utils.mod_safe(i,fold_decimate)==0 or i==int((len(fold_ls.coords)-1)/2) or i==len(fold_ls.coords)-1): #decimate to reduce number of points, but also take mid and end points of a series to keep some shape
                    locations=[(afs[0],afs[1])]     
                    height=m2l_utils.value_from_raster(dataset,locations)
                    ostr=str(afs[0])+','+str(afs[1])+','+str(height)+','+'FA_'+fold_name+','+fold[1][c_l['t']].replace(',','')+'\n'
                    fo.write(ostr)                
            i=i+1  

    fo.close()
    print("fold axial traces saved as",path_fold_orientations+'fold_axial_traces.csv')

#########################################
# Create basal contact points with orientation from orientations and basal points
#########################################
def create_basal_contact_orientations(contacts,structures,output_path,dtm,dist_buffer,c_l):
    f=open(output_path+'projected_dip_contacts2.csv',"w")
    f.write('X,Y,Z,azimuth,dip,polarity,formation\n')
    #print("len=",len(contacts))
    i=0
    for acontact in contacts.iterrows():   #loop through distinct linestrings
        #display(acontact[1].geometry)
        thegroup=acontact[1][c_l['g']].replace("_"," ")
        #print("thegroup=",thegroup)
        is_gp=structures[c_l['g']] == thegroup # subset orientations to just those with this group
        all_structures = structures[is_gp]

        for astr in all_structures.iterrows(): # loop through valid orientations

            orig = Point(astr[1]['geometry'])
            np = acontact[1].geometry.interpolate(acontact[1].geometry.project(orig))
            if(np.distance(orig)<dist_buffer):

                for line in acontact[1].geometry: # loop through line segments
                    for pair in m2l_utils.pairs(list(line.coords)): # loop through line segments
                        segpair=LineString((pair[0],pair[1]))
                        if segpair.distance(np)< 0.0001: # line segment closest to close point
                            ddx=sin(radians(astr[1][c_l['d']]))
                            ddy=cos(radians(astr[1][c_l['d']]))
                            dlsx=pair[0][0]-pair[1][0]
                            dlsy=pair[0][1]-pair[1][1]
                            lsx=dlsx/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                            lsy=dlsy/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                            angle=degrees(acos((ddx*lsx)+(ddy*lsy)))

                            if(fabs(angle-90)<30.0): # dip_dir normal and contact are close enough to parallel
                                locations=[(np.x,np.y)]
                                height= m2l_utils.value_from_raster(dtm,locations)
                                ls_ddir=degrees(atan2(lsy,-lsx)) #normal to line segment

                               
                                if (ddx*lsy)+(-ddy*lsx)<0: #dot product tests right quadrant
                                    ls_ddir=(ls_ddir-180)%360
                                ostr=str(np.x)+","+str(np.y)+","+height+","+str(ls_ddir)+","+str(astr[1][c_l['d']])+",1,"+acontact[1][c_l['c']].replace(" ","_").replace("-","_")+"\n" 
                                f.write(ostr)
                                i=i+1


    f.close()
    print("basal contact orientations saved as",output_path+'projected_dip_contacts2.csv')

#########################################
# For each pluton polygon, create dip info based on ideal form with azimuth parallel to local contact
#########################################
def process_plutons(tmp_path,output_path,geol_clip,local_paths,dtm,pluton_form,pluton_dip,contact_decimate,c_l):
    
    groups=np.genfromtxt(tmp_path+'groups.csv',delimiter=',',dtype='U25')
    ngroups=len(groups[0])-1

    orig_ngroups=ngroups

    gp_ages=np.zeros((1000,3))
    gp_names=np.zeros((1000),dtype='U25')

    for i in range (0,ngroups):
        gp_ages[i,0]=-1e6 # group max_age
        gp_ages[i,1]=1e6 # group min_age
        gp_ages[i,2]=i # group index
        gp_names[i]=groups[0][i+1].replace("\n","")
        print(i,gp_names[i])

    print(local_paths)  

    allc=open(output_path+'all_ign_contacts.csv',"w")
    allc.write('GROUP_,id,x,y,z,code\n')
    ac=open(output_path+'ign_contacts.csv',"w")
    ac.write("X,Y,Z,formation\n")
    ao=open(output_path+'ign_orientations_'+pluton_form+'.csv',"w")
    ao.write("X,Y,Z,azimuth,dip,polarity,formation\n")
    print(output_path+'ign_orientations_'+pluton_form+'.csv')
    j=0
    allpts=0
    ls_dict={}
    ls_dict_decimate={}
    id=0
    for ageol in geol_clip.iterrows(): 
        ades=str(ageol[1][c_l['ds']])
        arck=str(ageol[1][c_l['r1']])
        if(str(ageol[1][c_l['g']])=='None'):
            agroup=str(ageol[1][c_l['c']])
        else:
            agroup=str(ageol[1][c_l['g']])
        
        for i in range(0,ngroups):
            if (gp_names[i]==agroup):
                if(int(ageol[1][c_l['max']]) > gp_ages[i][0]  ):
                    gp_ages[i][0] = ageol[1][c_l['max']]
                if(int(ageol[1][c_l['min']]) < gp_ages[i][1]  ):
                    gp_ages[i][1] = ageol[1][c_l['min']]
        if(c_l['intrusive'] in arck and c_l['sill'] not in ades):
            newgp=str(ageol[1][c_l['c']])
            print(newgp)
            if(str(ageol[1][c_l['g']])=='None'):
                agp=str(ageol[1][c_l['c']])
            else:
                agp=str(ageol[1][c_l['g']])

            if(not newgp  in gp_names):
                gp_names[ngroups]=newgp
                gp_ages[ngroups][0]=ageol[1][c_l['max']]
                gp_ages[ngroups][1]=ageol[1][c_l['min']]
                gp_ages[ngroups][2]=ngroups
                ngroups=ngroups+1
                
            neighbours=[]
            j+=1
            central_age=ageol[1][c_l['min']]    #absolute age of central polygon
            central_poly=ageol[1].geometry
            for bgeol in geol_clip.iterrows(): #potential neighbouring polygons  
                if(ageol[1].geometry!=bgeol[1].geometry): #do not compare with self
                    if (ageol[1].geometry.intersects(bgeol[1].geometry)): # is a neighbour
                        neighbours.append([(bgeol[1][c_l['c']],bgeol[1][c_l['min']],bgeol[1][c_l['r1']],bgeol[1][c_l['ds']],bgeol[1].geometry)])  
            #display(neighbours)
            if(len(neighbours) >0):
                for i in range (0,len(neighbours)):
                    if((c_l['intrusive'] in neighbours[i][0][2] and c_l['sill'] not in ades) 
                       #or ('intrusive' not in neighbours[i][0][2]) and neighbours[i][0][1] > central_age ): # neighbour is older than central
                       or (c_l['intrusive'] not in neighbours[i][0][2]) and neighbours[i][0][1]  ): # neighbour is older than central
                        older_polygon=neighbours[i][0][4]
                        if(not central_poly.is_valid ):
                            central_poly = central_poly.buffer(0)
                        if(not older_polygon.is_valid):
                            older_polygon = older_polygon.buffer(0)
                        LineStringC = central_poly.intersection(older_polygon)
                        if(LineStringC.wkt.split(" ")[0]=='GEOMETRYCOLLECTION' or 
                           LineStringC.wkt.split(" ")[0]=='MULTIPOLYGON' or
                           LineStringC.wkt.split(" ")[0]=='POLYGON'): #ignore polygon intersections for now, worry about them later!
                            #print("debug:GC,MP,P")
                            continue

                        elif(LineStringC.wkt.split(" ")[0]=='MULTILINESTRING'):
                            k=0
                            ls_dict[id] = {"id": id,c_l['c']:newgp,c_l['g']:newgp, "geometry": LineStringC}
                            id=id+1
                            for lineC in LineStringC: #process all linestrings
                                if(m2l_utils.mod_safe(k,contact_decimate)==0 or k==int((len(LineStringC)-1)/2) or k==len(LineStringC)-1): #decimate to reduce number of points, but also take second and third point of a series to keep gempy happy
                                    locations=[(lineC.coords[0][0],lineC.coords[0][1])] #doesn't like point right on edge?
                                    if(lineC.coords[0][0] > dtm.bounds[0] and lineC.coords[0][0] < dtm.bounds[2] and  
                                       lineC.coords[0][1] > dtm.bounds[1] and lineC.coords[0][1] < dtm.bounds[3]):       
                                            height=m2l_utils.value_from_raster(dtm,locations)
                                            ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+height+","+newgp.replace(" ","_").replace("-","_")+"\n"
                                            ac.write(ostr)
                                            allc.write(agp+","+str(ageol[1][c_l['o']])+","+ostr)
                                            ls_dict_decimate[allpts] = {"id": allpts,c_l['c']:newgp,c_l['g']:newgp, "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                            allpts+=1 
                                    else:
                                        continue
                                else:
                                    if(lineC.coords[0][0] > dtm.bounds[0] and lineC.coords[0][0] < dtm.bounds[2] and  
                                            lineC.coords[0][1] > dtm.bounds[1] and lineC.coords[0][1] < dtm.bounds[3]):       
                                        height=m2l_utils.value_from_raster(dtm,locations)
                                        ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+height+","+newgp.replace(" ","_").replace("-","_")+"\n"
                                        #ls_dict_decimate[allpts] = {"id": id,"CODE":ageol[1]['CODE'],"GROUP_":ageol[1]['GROUP_'], "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                        allc.write(agp+","+str(ageol[1][c_l['o']])+","+ostr)
                                        allpts+=1
                                
                                if(m2l_utils.mod_safe(k,contact_decimate)==0 or k==int((len(LineStringC)-1)/2) or k==len(LineStringC)-1): #decimate to reduce number of points, but also take second and third point of a series to keep gempy happy
                                    dlsx=lineC.coords[0][0]-lineC.coords[1][0]
                                    dlsy=lineC.coords[0][1]-lineC.coords[1][1]
                                    lsx=dlsx/sqrt((dlsx*dlsx)+(dlsy*dlsy))
                                    lsy=dlsy/sqrt((dlsx*dlsx)+(dlsy*dlsy))                                        

                                    locations=[(lineC.coords[0][0],lineC.coords[0][1])]
                                    height= m2l_utils.value_from_raster(dtm,locations)
                                    azimuth=(180+degrees(atan2(lsy,-lsx)))%360 #normal to line segment
                                    testpx=lineC.coords[0][0]+lsy # pt just a bit in/out from line
                                    testpy=lineC.coords[0][0]+lsx

                                    for cgeol in geol_clip.iterrows(): # check on direction to dip
                                        if LineString(central_poly.exterior.coords).contains(Point(testpx, testpy)):
                                            azimuth=(azimuth-180)%360
                                            break
                                    if(pluton_form=='saucers'):
                                        ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+str(height)+","+str(azimuth)+","+str(pluton_dip)+",1,"+newgp.replace(" ","_").replace("-","_")+"\n"
                                    elif(pluton_form=='domes'):
                                        azimuth=(azimuth-180)%360
                                        ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+str(height)+","+str(azimuth)+","+str(pluton_dip)+",0,"+newgp.replace(" ","_").replace("-","_")+"\n"
                                    elif(pluton_form=='pendant'):
                                        ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+str(height)+","+str(azimuth)+","+str(pluton_dip)+",0,"+newgp.replace(" ","_").replace("-","_")+"\n"
                                    else: #pluton_form == batholith
                                        azimuth=(azimuth-180)%360
                                        ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+str(height)+","+str(azimuth)+","+str(pluton_dip)+",1,"+newgp.replace(" ","_").replace("-","_")+"\n"
                                        
                                    ao.write(ostr)

                                k+=1
                        elif(LineStringC.wkt.split(" ")[0]=='LINESTRING'): # apparently this is not needed
                            #print("debug:LINESTRING")
                            k=0
                            for pt in LineStringC.coords: #process one linestring
                                k+=1
                        elif(LineStringC.wkt.split(" ")[0]=='POINT'): # apparently this is not needed
                            #print("debug:POINT")
                            k+=1
                        else:
                            #print(LineStringC.wkt.split(" ")[0]) # apparently this is not needed
                            k+=1
    ac.close()
    ao.close()
    allc.close()

      
    an=open(tmp_path+'groups2.csv',"w")

    for i in range (0,orig_ngroups):
        print(i,gp_names[i].replace(" ","_").replace("-","_"))
        an.write(gp_names[i].replace(" ","_").replace("-","_")+'\n')
    an.close()

    all_sorts=pd.read_csv(tmp_path+'all_sorts.csv',",")

    as_2=open(tmp_path+'all_sorts.csv',"r")
    contents =as_2.readlines()
    as_2.close

    all_sorts_file=open(tmp_path+'all_sorts2.csv',"w")
    all_sorts_file.write('index,group number,index in group,number in group,code,group\n')
    j=1

    for i in range(1,len(all_sorts)+1):    
        all_sorts_file.write(contents[i]) #don't write out if already there in new groups list#
        
    all_sorts_file.close()
    print('pluton contacts and orientations saved as:')
    print(output_path+'ign_contacts.csv')
    print(output_path+'ign_orientations_'+pluton_form+'.csv')

###################################
# Remove orientations that don't belong to actual formations in mode
# Remove groups for which there are no formations
###################################
def tidy_data(output_path,tmp_path,use_group,use_interpolations,use_fat,pluton_form):
    contacts=pd.read_csv(output_path+'contacts4.csv',",")
    orientations=pd.read_csv(output_path+'orientations.csv',",")
    invented_orientations=pd.read_csv(output_path+'empty_series_orientations.csv',",")
    interpolated_orientations=pd.read_csv(tmp_path+'combo_full.csv',",")
    intrusive_orientations=pd.read_csv(output_path+'ign_orientations_'+pluton_form+'.csv',",")
    intrusive_contacts=pd.read_csv(output_path+'ign_contacts.csv',",")
    fault_contact=pd.read_csv(output_path+'faults.csv',",")
    fault_orientations=pd.read_csv(output_path+'fault_orientations.csv',",")
    fat_orientations=pd.read_csv(output_path+'fold_axial_trace_orientations2.csv',",")
    all_sorts=pd.read_csv(tmp_path+'all_sorts2.csv',",")
    combo_full_orientations=pd.read_csv(tmp_path+'combo_full.csv',",")

    if(use_interpolations):
        all_orientations=pd.concat([orientations,invented_orientations,intrusive_orientations,combo_full_orientations.iloc[::2, :]])
    else:
        all_orientations=pd.concat([orientations,invented_orientations,intrusive_orientations])

    if(use_fat):
        all_orientations=pd.concat([all_orientations,fat_orientations])
        
    all_orientations.reset_index(inplace=True)

    all_sorts.set_index('code',  inplace = True)

    all_contacts=pd.concat([intrusive_contacts,contacts])
    all_contacts.reset_index(inplace=True)
    display(all_sorts)
    all_groups=set(all_sorts['group'])

    unique_contacts=set(all_contacts['formation'])

    # Remove groups that don't have any contact info
    no_contacts=[]
    groups=[]
    for agroup in all_groups:
        found=False
        for acontact in all_contacts.iterrows():
            if(all_sorts.loc[acontact[1]['formation']]['group'] in agroup ):
                found=True
                break
        if(not found):
            no_contacts.append(agroup)
            print('no contacts for the group:',agroup)
        else:
            groups.append(agroup)

    # Update list of all groups that have formations info

    f=open(tmp_path+'groups2.csv',"r")
    contents =f.readlines()
    f.close

    #ngroups=contents[0].split(" ")
    #ngroups=int(ngroups[1])  
    ngroups=len(contents)
    no_contacts=[]
    groups=[]
    
    for i in range(0,ngroups):
        print(i,ngroups,contents[i])
        found=False
        #print('GROUP',agroup)
        for acontact in all_contacts.iterrows():
            #print(all_sorts.loc[acontact[1]['formation']]['group'])
            if(all_sorts.loc[acontact[1]['formation']]['group'] in contents[i] and all_sorts.loc[acontact[1]['formation']]['group'] in use_group):
                found=True
                break
        if(not found):
            no_contacts.append(contents[i].replace("\n",""))
            print('no contacts for the group:',contents[i].replace("\n",""))
        else:
            groups.append(contents[i].replace("\n",""))

    # Make new list of groups

    fgp=open(tmp_path+'groups_clean.csv',"w")
    for i in range(0,len(groups)):
        fgp.write(contents[i+1].replace("\n","")+'\n')
    fgp.close()        

    # Remove orientations with no equivalent formations info

    for agroup in all_groups:
        found=False
        for ano in all_orientations.iterrows():
            if(all_sorts.loc[ano[1]['formation']]['group'] in agroup and all_sorts.loc[ano[1]['formation']]['group'] in use_group):
                found=True
                break
        if(not found):
            no_contacts.append(agroup)
            print('no orientations for the group:',agroup)

    print(no_contacts)

    # Update master list of  groups and formations info

    fas=open(tmp_path+'all_sorts_clean.csv',"w")
    fas.write('index,group number,index in group,number in group,code,group,uctype\n')
    for a_sort in all_sorts.iterrows():
        if(a_sort[1]['group'] not in no_contacts):
            ostr=str(a_sort[1]['index'])+","+str(a_sort[1]['group number'])+","+str(a_sort[1]['index in group'])+","+str(a_sort[1]['number in group'])+","+a_sort[0]+","+a_sort[1]['group']+",erode\n"
            fas.write(ostr)
    fas.close()

    # Update orientation info

    fao=open(output_path+'orientations_clean.csv',"w")
    fao.write('X,Y,Z,azimuth,dip,polarity,formation\n')

    for ano in all_orientations.iterrows():
        if(all_sorts.loc[ano[1]['formation']]['group'] in no_contacts or not ano[1]['formation'] in unique_contacts or not all_sorts.loc[ano[1]['formation']]['group'] in use_group):  #fix here################################
            print('dud orientation:',ano[1]['formation'])
        else:
            ostr=str(ano[1]['X'])+","+str(ano[1]['Y'])+","+str(ano[1]['Z'])+","+\
                 str(ano[1]['azimuth'])+","+str(ano[1]['dip'])+","+str(ano[1]['polarity'])+","+ano[1]['formation']+"\n"
            fao.write(ostr)

    fao.close()

    # Update formation info

    fac=open(output_path+'contacts_clean.csv',"w")
    fac.write('X,Y,Z,formation\n')

    for acontact in all_contacts.iterrows():
        if(all_sorts.loc[acontact[1]['formation']]['group'] in no_contacts or not all_sorts.loc[acontact[1]['formation']]['group'] in use_group):
            print('dud contact:',acontact[1]['formation'])
        else:
            ostr=str(acontact[1]['X'])+","+str(acontact[1]['Y'])+","+str(acontact[1]['Z'])+","+acontact[1]['formation']+"\n"
            fac.write(ostr)

    fac.close()


####################################################
# calculate distance between two points
####################################################
def pt_dist(x1,y1,x2,y2):
    dist=sqrt(pow(x1-x2,2)+pow(y1-y2,2))
    return(dist)

####################################################
# determine if two bounding boxes overlap
####################################################

def bboxes_intersect(bbox1,bbox2):
        if(bbox1[0]<=bbox2[2] and bbox1[0]>=bbox2[0] and bbox1[1]<=bbox2[3] and bbox1[1]<=bbox2[1]):
            return(True)
        elif(bbox1[0]<=bbox2[2] and bbox1[0]>=bbox2[0] and bbox1[3]<=bbox2[3] and bbox1[3]<=bbox2[1]):
            return(True)
        elif(bbox1[2]<=bbox2[2] and bbox1[2]>=bbox2[0] and bbox1[1]<=bbox2[3] and bbox1[1]<=bbox2[1]):
            return(True)
        elif(bbox1[2]<=bbox2[2] and bbox1[2]>=bbox2[0] and bbox1[3]<=bbox2[3] and bbox1[3]<=bbox2[1]):
            return(True)
        elif(bbox2[0]<=bbox1[2] and bbox2[0]>=bbox1[0] and bbox2[3]<=bbox1[3] and bbox2[3]<=bbox1[1]):
            return(True)
        else:
            return(False)

####################################
# Calculate local formation thickness estimates by finding intersection of normals to basal contacts 
# with next upper formation in stratigraphy, and using interpolated orientaiton estimates to calculate true thickness
####################################
def calc_thickness(tmp_path,output_path,buffer,max_thickness_allowed):
    contact_points_file=tmp_path+'raw_contacts.csv'
    interpolated_combo_file=tmp_path+'combo_full.csv'
    contact_lines = gpd.read_file(tmp_path+'/basal_contacts.shp') #load orientation data as geopandas dataframe 
    all_sorts=pd.read_csv(tmp_path+'all_sorts.csv')
    contacts=pd.read_csv(contact_points_file)
    orientations=pd.read_csv(interpolated_combo_file)
    olength=len(orientations)
    clength=len(contacts)
    cx=contacts['X'].to_numpy()

    cy=contacts['Y'].to_numpy()
    cl=contacts['lsx'].to_numpy(dtype=float)
    cm=contacts['lsy'].to_numpy(dtype=float)
    ctextcode=contacts['formation'].to_numpy()
    ox=orientations['X'].to_numpy()
    oy=orientations['Y'].to_numpy()
    dip=orientations['dip'].to_numpy().reshape(olength,1)
    azimuth=orientations['azimuth'].to_numpy().reshape(olength,1)

    l = np.zeros(len(ox))
    m = np.zeros(len(ox))
    n = np.zeros(len(ox))    
    file=open(output_path+'formation_thicknesses.csv','w')
    file.write('X,Y,formation,thickness,cl,cm,meanl,meanm,meann,p1x,p1y,p2x,p2y,dip\n')
    dist=m2l_interpolation.distance_matrix(ox,oy,cx,cy)
    
    #np.savetxt(tmp_path+'dist.csv',dist,delimiter=',')
    #display("ppp",cx.shape,cy.shape,ox.shape,oy.shape,dip.shape,azimuth.shape,dist.shape)
    n_est=0
    for k in range(0,clength): #loop through all contact segments
        a_dist=dist[:,k:k+1]
        is_close=a_dist<buffer 
        #display("ic",a_dist.shape,is_close.shape,dip.shape)
        close_dip=dip[is_close]
        #print("cd",close_dip.shape)
        #print(close_dip)
        close_azimuth=azimuth[is_close]
        n_good=0
        for j in range(0,len(close_dip)): #find averaged dips within buffer
            l[n_good],m[n_good],n[n_good]=m2l_utils.ddd2dircos(float(close_dip[j]),float(close_azimuth[j])+90.0)
            #print(k,len(close_dip),n_good,l[n_good],m[n_good],n[n_good])
            n_good=n_good+1
        if(n_good>0): #if we found any candidates
            lm=np.mean(l[:n_good]) #average direction cosine of points within buffer range
            mm=np.mean(m[:n_good])
            nm=np.mean(n[:n_good])
            dip_mean,dipdirection_mean=m2l_utils.dircos2ddd(lm,mm,nm)
            #print(k,type(cm[k]),type(buffer))

            dx1=-cm[k]*buffer
            dy1=cl[k]*buffer
            dx2=-dx1
            dy2=-dy1
            p1=Point((dx1+cx[k],dy1+cy[k]))
            p2=Point((dx2+cx[k],dy2+cy[k]))
            ddline=LineString((p1,p2))
            orig = Point((cx[k],cy[k]))
            
            crossings=np.zeros((1000,5))
            
            g=0
            for apair in all_sorts.iterrows(): #loop through all basal contacts

                if(ctextcode[k]==apair[1]['code']):
                    #if(all_sorts.iloc[g]['group']==all_sorts.iloc[g-1]['group']):
                    is_contacta=contact_lines['CODE'] == all_sorts.iloc[g-1]['code'] # subset contacts to just those with 'a' code
                    acontacts = contact_lines[is_contacta]
                    i=0 
                    for acontact in acontacts.iterrows():   #loop through distinct linestrings for upper contact
                        #if(bboxes_intersect(ddline.bounds,acontact[1].geometry.bounds)):

                        if(ddline.intersects(acontact[1].geometry)): 
                            isects=ddline.intersection(acontact[1].geometry)
                            if(isects.geom_type=="MultiPoint"):
                                for pt in isects: 
                                    if(pt.distance(orig)<buffer*2):
                                        #print(i,",", pt.x, ",",pt.y,",",apair[1]['code'],",",apair[1]['group'])
                                        crossings[i,0]=i
                                        crossings[i,1]=int(apair[1]['index'])
                                        crossings[i,2]=0
                                        crossings[i,3]=pt.x
                                        crossings[i,4]=pt.y
                                        i=i+1
                            else:
                                if(isects.distance(orig)<buffer*2):
                                    #print(i,",", isects.x,",", isects.y,",",apair[1]['code'],",",apair[1]['group'])
                                    crossings[i,0]=i
                                    crossings[i,1]=int(apair[1]['index'])
                                    crossings[i,2]=0
                                    crossings[i,3]=isects.x
                                    crossings[i,4]=isects.y
                                    i=i+1
                    if(i>0): #if we found any intersections with base of next higher unit
                        min_dist=1e8
                        min_pt=0
                        for f in range(0,i): #find closest hit
                            this_dist=pt_dist(crossings[f,3],crossings[f,4],cx[k],cy[k])
                            if(this_dist<min_dist):
                                min_dist=this_dist
                                min_pt=f
                        if(min_dist<max_thickness_allowed): #if not too far, add to output
                            true_thick=sin(radians(dip_mean))*min_dist
                            ostr=str(cx[k])+','+str(cy[k])+','+ctextcode[k]+','+str(int(true_thick))+\
                                ','+str(cl[k])+','+str(cm[k])+','+str(lm)+','+str(mm)+','+str(nm)+','+\
                                str(p1.x)+','+str(p1.y)+','+str(p2.x)+','+str(p2.y)+','+str(dip_mean)+'\n'
                            file.write(ostr)
                            n_est=n_est+1
                                
                g=g+1
    print(n_est,'thickness estimates saved as',output_path+'formation_thicknesses.csv')

####################################
# Normalise thickness for each estimate to median for that formation
####################################
def normalise_thickness(output_path):
    thickness=pd.read_csv(output_path+'formation_thicknesses.csv', sep=',')
    
    codes=thickness.formation.unique()

    f=open(output_path+'formation_thicknesses_norm.csv','w')
    f.write('x,y,formation,thickness,norm_th\n')
    fs=open(output_path+'formation_summary_thicknesses.csv','w')
    fs.write('formation,thickness median,thickness std\n')
    for code in codes:
        is_code=thickness.formation.str.contains(code, regex=False)
        all_thick = thickness[is_code]
        print(code,all_thick.loc[:,"thickness"].median(),all_thick.loc[:,"thickness"].std())
        ostr=str(code)+","+str(all_thick.loc[:,"thickness"].median())+","+str(all_thick.loc[:,"thickness"].std())+"\n"    
        fs.write(ostr)
        
        med=all_thick.loc[:,"thickness"].median()
        std=all_thick.loc[:,"thickness"].std()
        
        thick=all_thick.to_numpy()
    
        for i in range(len(thick)):
            if(med>0):
                ostr=str(thick[i,0])+","+str(thick[i,1])+","+str(thick[i,2])+","+str(thick[i,3])+","+str(thick[i,3]/med)+"\n"    
                f.write(ostr)
    f.close()
    fs.close()
    
def bboxes_intersect(bbox1,bbox2):
        if(bbox1[0]<=bbox2[2] and bbox1[0]>=bbox2[0] and bbox1[1]<=bbox2[3] and bbox1[1]>=bbox2[1]):
            return(True)
        elif(bbox1[0]<=bbox2[2] and bbox1[0]>=bbox2[0] and bbox1[3]<=bbox2[3] and bbox1[3]>=bbox2[1]):
            return(True)
        elif(bbox1[2]<=bbox2[2] and bbox1[2]>=bbox2[0] and bbox1[1]<=bbox2[3] and bbox1[1]>=bbox2[1]):
            return(True)
        elif(bbox1[2]<=bbox2[2] and bbox1[2]>=bbox2[0] and bbox1[3]<=bbox2[3] and bbox1[3]>=bbox2[1]):
            return(True)
        elif(bbox2[0]<=bbox1[2] and bbox2[0]>=bbox1[0] and bbox2[3]<=bbox1[3] and bbox2[3]>=bbox1[1]):
            return(True)
        else:
            return(False)
        
####################################################
# For each fault string:

#    incementally advance along polyline every at each inter-node (no point in doing more?)
#    find local stratigraphy 10m to left and right of fault
# Once full fault has been traversed:

#    Find list of contacts left
#    Find equivalent contacts on right
#    use interpolated orientations to estimate minimum true offset assuming vertical displacement and store
#    if no equivalent found, flag as domain fault and find min strat offset for contact, use cumulative minimum thickness estimate and store with flag (not implemented)
#    estimate median & sd of minimum fault offset and store with flag (not implemented)
# Local Orientations: Since much of the code is the same, we benefit by calculating local orientation data either side of 
# fault so that geomodeller/gempy have satisfied fault compartment orientation data
###################################################
def save_fold_axial_traces_orientations(path_folds,output_path,tmp_path,dataset,c_l,dst_crs,fold_decimate,fat_step,close_dip):
    geology = gpd.read_file(tmp_path+'geol_clip.shp')
    contacts=np.genfromtxt(tmp_path+'interpolation_contacts_scipy_rbf.csv',delimiter=',',dtype='float')
    f=open(output_path+'fold_axial_trace_orientations2.csv','w')
    f.write('X,Y,Z,azimuth,dip,polarity,formation\n')
    folds_clip=gpd.read_file(path_folds,)
    fo=open(output_path+'fold_axial_traces.csv',"w")
    fo.write("X,Y,Z,code,type\n")
    dummy=[]
    dummy.append(1)
    for indx,fold in folds_clip.iterrows():
        fold_name=str(fold[c_l['o']])   
        fold_ls=LineString(fold.geometry)
        i=0
        first=True
        for afs in fold_ls.coords:
            if(c_l['fold'] in fold[c_l['f']]):
                # save out current geometry of FAT
                if(m2l_utils.mod_safe(i,fold_decimate)==0 or i==int((len(fold_ls.coords)-1)/2) or i==len(fold_ls.coords)-1): #decimate to reduce number of points, but also take mid and end points of a series to keep some shape
                    locations=[(afs[0],afs[1])]                  
                    height=m2l_utils.value_from_raster(dataset,locations)
                    ostr=str(afs[0])+','+str(afs[1])+','+str(height)+','+'FA_'+fold_name+','+fold[c_l['t']].replace(',','')+'\n'
                    fo.write(ostr)  
                    # calculate FAT normal offsets  
                    if(not first):
                        l,m=m2l_utils.pts2dircos(lastx,lasty,afs[0],afs[1])
                        midx=lastx+((afs[0]-lastx)/2)
                        midy=lasty+((afs[1]-lasty)/2)
                        midxr=midx+(fat_step*-m)
                        midyr=midy+(fat_step*l)
                        midxl=midx-(fat_step*-m)
                        midyl=midy-(fat_step*l)
                        dip,dipdir=m2l_utils.dircos2ddd(-m,l,cos(radians(close_dip)))
                        if(c_l['syn'] in fold[c_l['t']]):
                            dipdir=dipdir+180
                        mindist=1e9
                        minind=-1
                        for i in range(1,len(contacts)):
                            dist=m2l_utils.ptsdist(contacts[i,0],contacts[i,1],midx,midy)
                            if(dist<mindist):
                                mindist=dist
                                minind=i
                        lc=sin(radians(contacts[minind,2]))
                        mc=cos(radians(contacts[minind,2]))
                        dotprod=fabs((l*lc)+(m*mc))
                        #print(dotprod,midx,midy,minind,contacts[minind,2],l,m,lc,mc)   
                        # if FAT is sub-parallel to local interpolated contacts, save out as orientations  
                        if(dotprod>0.85):
                            geometry = [Point(midxr,midyr)]
                            gdf = GeoDataFrame(dummy, crs=dst_crs, geometry=geometry)
                            structure_code = gpd.sjoin(gdf, geology, how="left", op="within")
                            if(not str(structure_code.iloc[0]['CODE'])=='nan'):
                                locations=[(midxr,midyr)]                  
                                height=m2l_utils.value_from_raster(dataset,locations)
                                ostr=str(midxr)+','+str(midyr)+','+str(height)+','+str(dipdir)+','+str(int(dip))+',1,'+str(structure_code.iloc[0]['CODE']).replace(" ","_").replace("-","_")+'\n'
                                f.write(ostr)
                            
                            geometry = [Point(midxl,midyl)]
                            gdf = GeoDataFrame(dummy, crs=dst_crs, geometry=geometry)
                            structure_code = gpd.sjoin(gdf, geology, how="left", op="within")
                            if(not str(structure_code.iloc[0]['CODE'])=='nan'):
                                locations=[(midxl,midyl)]                  
                                height=m2l_utils.value_from_raster(dataset,locations)
                                ostr=str(midxl)+','+str(midyl)+','+str(height)+','+str(dipdir+180)+','+str(int(dip))+',1,'+str(structure_code.iloc[0]['CODE']).replace(" ","_").replace("-","_")+'\n'
                                f.write(ostr)
                    first=False
                    lastx=afs[0]
                    lasty=afs[1]
            i=i+1  

    fo.close()
    f.close()
    print("fold axial traces saved as",output_path+'fold_axial_traces.csv')
    print("fold axial trace orientations saved as",output_path+'fold_axial_trace_orientations.csv')
