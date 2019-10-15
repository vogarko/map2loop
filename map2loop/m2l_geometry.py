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
import numpy as np

#Export orientation data in csv format with heights and strat code added
def save_orientations(structures,path_out,ddcode,dcode,ccode,rcode,intrusive_label,orientation_decimate,dtm):
    i=0
    f=open(path_out+'/orientations.csv',"w")
    f.write("X,Y,Z,azimuth,dip,polarity,formation\n")
    for apoint in structures.iterrows():
        if(not intrusive_label in apoint[1][rcode]):
            if(apoint[1][dcode]!=0 and m2l_utils.mod_safe(i,orientation_decimate)==0):
                locations=[(apoint[1]['geometry'].x, apoint[1]['geometry'].y)]
                if(apoint[1]['geometry'].x > dtm.bounds[0] and apoint[1]['geometry'].x < dtm.bounds[2] and  
                    apoint[1]['geometry'].y > dtm.bounds[1] and apoint[1]['geometry'].y < dtm.bounds[3]):       
                    height=m2l_utils.value_from_raster(dtm,locations)
                    ostr=str(apoint[1]['geometry'].x)+","+str(apoint[1]['geometry'].y)+","+height+","+str(apoint[1][ddcode])+","+str(apoint[1][dcode])+",1,"+str(apoint[1][ccode].replace(" ","_").replace("-","_"))+"\n"
                    f.write(ostr)
                    i+=1
        
    f.close()
    print(i,'orientations saved to',path_out+'/orientations.csv')

#Find those series that don't have any orientation or contact point data and add some random data
def create_orientations( path_in, path_out,dtm,geology,structures,ccode,gcode,r1code,intrusive_label):
    f=open(path_in+'/groups.csv',"r")
    contents =f.readlines()
    f.close

    ngroups=contents[0].split(" ")
    ngroups=int(ngroups[1])

    groups=[]
    for i in range (1,int(ngroups)+1):
        #print(contents[i].replace("\n",""))
        groups.append((contents[i].replace("\n",""),0))

    #print(ngroups,groups)

    for i in range (0,ngroups):
        for apoint in structures.iterrows():
            if(str(apoint[1][gcode])=='None'):
                agroup=apoint[1][ccode].replace(" ","_").replace("-","_")
            else:
                agroup=apoint[1][gcode].replace(" ","_").replace("-","_")
            #print(agroup)
            if(groups[i][0]==agroup):
                lgroups=list(groups[i])
                lgroups[1]=1
                lgroups=tuple(lgroups)
                groups[i]=lgroups

    print("Orientations----------\n",ngroups,groups)

    for i in range (0,ngroups):
        for apoly in geology.iterrows():
            agroup=apoint[1][gcode].replace(" ","_").replace("-","_")
            #print(agroup)
            if(groups[i][0]==agroup):
                lgroups=list(groups[i])
                lgroups[1]=1
                lgroups=tuple(lgroups)
                groups[i]=lgroups

    all_codes=[]
    for ageol in geology.iterrows(): # central polygon
            all_codes.append(ageol[1][ccode])

    print("Contacts----------\n",len(set(all_codes)),set(all_codes))

    f=open(path_out+'/empty_series_orientations.csv',"w")
    f.write("X,Y,Z,azimuth,dip,polarity,formation\n")

    for i in range (0,ngroups):
        if(groups[i][1]==0):
            for ageol in geology.iterrows():
                if(ageol[1][ccode].replace("-","_")==groups[i][0] and groups[i][1]==0 and not intrusive_label in ageol[1][r1code] ):
                    apoly=Polygon(ageol[1]['geometry'])
                    apoint=apoly.representative_point()
                    #print(apoint.x,apoint.y)
                    locations=[(apoint.x,apoint.y)]
                    height=m2l_utils.value_from_raster(dtm,locations)
                    if(height==-999):
                        print("point off map",locations)
                        height=0   # needs a better solution!
                    ostr=str(apoint.x)+","+str(apoint.y)+","+height+",0,45,1"+","+str(ageol[1][ccode].replace(" ","_").replace("-","_"))+"\n"
                    f.write(ostr)
                    plt.title(str(ageol[1][ccode].replace(" ","_").replace("-","_")))
                    plt.scatter(apoint.x,apoint.y,color="red")
                    plt.plot(*apoly.exterior.xy)
                    plt.show()
                    break

    f.close()
    print('extra orientations saved as',path_out+'/empty_series_orientations.csv')

#modified from https://stackoverflow.com/questions/21824157/how-to-extract-interior-polygon-coordinates-using-shapely
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

#Export contact information subset of each polygon to csv format
def save_basal_contacts(path_in,dtm,geol_clip,contact_decimate,ccode,gcode,ocode,dscode,r1code,intrusion_mode):
    print("decimation: 1 /",contact_decimate)
    plist=[]
    i=0
    all_geom=m2l_utils.explode(geol_clip)

    #print(type(all_geom))

    for ageol in all_geom.iterrows(): # central polygon
        all_coords=extract_poly_coords(ageol[1].geometry,0)
        plist+=(i,list(all_coords['exterior_coords']),ageol[1][ccode],ageol[1][dscode],ageol[1][gcode],ageol[1][r1code],ageol[1][ocode])
        i=i+1
        for j in range(0,len(all_coords['interior_coords']),2):
            plist+=(i,list(all_coords['interior_coords'][j+1]),ageol[1][ccode],ageol[1][dscode],ageol[1][gcode],ageol[1][r1code],ageol[1][ocode])
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
                        #c_polygon=snap(a_polygon,b_polygon,5)
                        #if(plist[a_poly+6]==98 and plist[b_poly+6]==84):
                            #display(plist[a_poly],plist[b_poly],plist[b_poly+3],plist[b_poly+5])
                        if (a_polygon.intersects(b_polygon)) : # is a neighbour, but not a sill
                           if(  (not 'sill' in plist[b_poly+3] or not 'intrusive' in plist[b_poly+5]) and intrusion_mode==0): #intrusion_mode=0 (sills only excluded)
                                 neighbours.append((b_poly))                               
                           elif((not 'intrusive' in plist[b_poly+5])  and intrusion_mode==1): #intrusion_mode=1 (all intrusions  excluded)
                                 neighbours.append((b_poly))                               
                            #elif( not 'sill' in plist[b_poly+3] or not 'intrusive' in plist[b_poly+5]):
                                #neighbours.append((b_poly))
                               # print(b_polygon)

                #print(plist[a_poly+6],len(neighbours)) 

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
                                if(plist[a_poly+6]==98 and neighbours[i]==84):
                                    display(LineStringC)
                                if(LineStringC.wkt.split(" ")[0]=='GEOMETRYCOLLECTION' ): #ignore weird intersections for now, worry about them later!
                                    #print("debug:GC")
                                    continue
                                elif(LineStringC.wkt.split(" ")[0]=='MULTIPOLYGON' or
                                     LineStringC.wkt.split(" ")[0]=='POLYGON'):
                                         print("debug:MP,P",ageol[1][ccode])
                                         #display(LineStringC)

                                elif(LineStringC.wkt.split(" ")[0]=='MULTILINESTRING'):
                                    k=0

                                    if(str(plist[a_poly+4])=='None'):
                                        ls_dict[id] = {"id": id,ccode:plist[a_poly+2].replace(" ","_").replace("-","_"),gcode:plist[a_poly+2].replace(" ","_").replace("-","_"), "geometry": LineStringC}
                                    else:
                                        ls_dict[id] = {"id": id,ccode:plist[a_poly+2].replace(" ","_").replace("-","_"),gcode:plist[a_poly+4].replace(" ","_").replace("-","_"), "geometry": LineStringC}
                                    id=id+1
                                    for lineC in LineStringC: #process all linestrings
                                        #print(ageol[1][ccode],len(LineStringC))
                                        if(m2l_utils.mod_safe(k,contact_decimate)==0 or k==int((len(LineStringC)-1)/2) or k==len(LineStringC)-1): #decimate to reduce number of points, but also take second and third point of a series to keep gempy happy
                                            locations=[(lineC.coords[0][0],lineC.coords[0][1])] #doesn't like point right on edge?
                                            #print(k,type(lineC))
                                            if(lineC.coords[0][0] > dtm.bounds[0] and lineC.coords[0][0] < dtm.bounds[2] and  
                                               lineC.coords[0][1] > dtm.bounds[1] and lineC.coords[0][1] < dtm.bounds[3]):       
                                                    height=m2l_utils.value_from_raster(dtm,locations)
                                                    ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+height+","+str(plist[a_poly+2].replace(" ","_").replace("-","_"))+"\n"
                                                    ac.write(ostr)
                                                    allc.write(agp+","+str(ageol[1][ocode])+","+ostr)
                                                    if(str(plist[neighbours[i]+4])=='None'):
                                                        ls_dict_decimate[deci_points] = {"id": allpts,ccode:plist[a_poly+2].replace(" ","_").replace("-","_"),gcode:plist[a_poly+2].replace(" ","_").replace("-","_"), "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                                    else:
                                                        ls_dict_decimate[deci_points] = {"id": allpts,ccode:plist[a_poly+2].replace(" ","_").replace("-","_"),gcode:plist[a_poly+4].replace(" ","_").replace("-","_"), "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                                    #ls_dict_decimate[allpts] = {"id": allpts,"CODE":ageol[1][ccode].replace(" ","_").replace("-","_"),"GROUP_":ageol[1][gcode].replace(" ","_").replace("-","_"), "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
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
                                                #ls_dict_decimate[allpts] = {"id": id,"CODE":ageol[1]['CODE'],"GROUP_":ageol[1]['GROUP_'], "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                                allc.write(agp+","+str(ageol[1][ocode])+","+ostr)
                                                allpts+=1    
                                        """        
                                        else:
                                            locations=[(lineC.coords[0][0]+0.0000001,lineC.coords[0][1])] #doesn't like point right on edge?
                                            if(lineC.coords[0][0] > dataset.bounds[0] and lineC.coords[0][0] < dataset.bounds[2] and  
                                                lineC.coords[0][1] > dataset.bounds[1] and lineC.coords[0][1] < dataset.bounds[3]):       
                                                for val in dataset.sample(locations):
                                                    height=str(val).replace("[","").replace("]","")
                                                ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+height+","+str(ageol[1][ccode])+"\n"
                                                ac.write(ostr)
                                                allc.write(agp+","+str(ageol[1]['OBJECTID_1'])+","+ostr)
                                                ls_dict_decimate[allpts] = {"id": id,"CODE":ageol[1]['CODE'],"GROUP_":ageol[1]['GROUP_'], "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                                allpts+=1
                                        """
                                        k+=1
                                elif(LineStringC.wkt.split(" ")[0]=='LINESTRING'): # apparently this is not needed
                                    #print("debug:LINESTRING",ageol[1][ocode],ageol[1][ccode],list(LineStringC.coords))
                                    #display(LineStringC)
                                    k=0
                                    for pt in LineStringC.coords: #process one linestring
                                        #if(i%contact_decimate==0): #decimate to reduce number of points
                                        #print("ls",pt)
                                        """
                                        locations=[(float(pt[0]),float(pt[1]))]
                                        for val in dataset.sample(locations):
                                            height=str(val).replace("[","").replace("]","")
                                        ostr=str(pt[0])+","+str(pt[1])+","+height+","+str(ageol[1][ccode])+"\n"
                                        ac.write(ostr)
                                        """
                                        k+=1
                                elif(LineStringC.wkt.split(" ")[0]=='POINT'): # apparently this is not needed
                                    #print("debug:POINT")
                                    k=0
                                    #print("pt",LineStringC.coords)
                                    """
                                    locations=[(float(pt[0]),float(pt[1]))]
                                    for val in dataset.sample(locations):
                                        height=str(val).replace("[","").replace("]","")
                                    ostr=str(pt[0])+","+str(pt[1])+","+height+","+str(ageol[1][ccode])+"\n"
                                    ac.write(ostr)
                                    """
                                    k+=1
                                else:
                                    k=0
                                    #print(LineStringC.wkt.split(" ")[0]) # apparently this is not needed
                                    k+=1


    ac.close()
    allc.close()
    print("basal contacts saved allpts=",allpts,"deci_pts=",deci_points)
    print("saved as",path_in+'all_contacts.csv',"and",path_in+'contacts.csv')
    return(ls_dict,ls_dict_decimate)

#Remove all basal contacts that are defined by faults and save to shapefile (no decimation)
def save_basal_no_faults(path_out,path_fault,ls_dict,dist_buffer,ccode,gcode,dst_crs):
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
            ls_nf[j]= {"id": j,ccode:df.iloc[j][ccode].replace(" ","_").replace("-","_"),gcode:df.iloc[j][gcode].replace(" ","_").replace("-","_"), "geometry": cnf_copy.iloc[j]}



    df_nf = DataFrame.from_dict(ls_nf, "index")

    contacts_nf = GeoDataFrame(df_nf,crs=dst_crs, geometry='geometry')
    contacts_nf.to_file(driver = 'ESRI Shapefile', filename= path_out)

    #contacts_nofaults = gpd.read_file('./data/faults_clip.shp')
    print("basal contacts without faults saved as",path_out)

#Remove faults from decimated basal contacts as save as csv file   
def save_contacts_with_faults_removed(path_fault,path_out,dist_buffer,ls_dict,ls_dict_decimate,ccode,dst_crs,dataset):
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
            ostr=str(cdn[1].geometry.x)+","+str(cdn[1].geometry.y)+","+height+","+str(cdn[1][ccode].replace(" ","_").replace("-","_"))+"\n"
            ac.write(ostr)

        i=i+1
    ac.close()
    print(i,"decimated contact points saved as",path_out+'/contacts4.csv')
    
#Save faults as contact info and make vertical (for the moment)
def save_faults(path_faults,path_fault_orientations,dataset,ncode,ocode,fcode,fault_decimate,fault_label):
    faults_clip=gpd.read_file(path_faults)
    f=open(path_fault_orientations+'/faults.csv',"w")
    f.write("X,Y,Z,formation\n")
    fo=open(path_fault_orientations+'/fault_orientations.csv',"w")
    fo.write("X,Y,Z,azimuth,dip,polarity,formation\n")
    fd=open(path_fault_orientations+'/fault_dimensions.csv',"w")
    fd.write("Fault_ID,strike,dip_direction,down_dip\n")

    for flt in faults_clip.iterrows():
        #if(flt[1][ncode]=='Karra Well Fault'): #<<<<<<<<<<<< When too many faults gets ugly!
        if(fault_label in flt[1][fcode]):
            #if(str(flt[1][ncode])=='None'):
            fault_name='Fault_'+str(flt[1][ocode])
            #else:
            #fault_name=str(flt[1][ncode])   
            #print(flt)
            flt_ls=LineString(flt[1].geometry)
            #print(flt_ls)

            i=0
            #print(len(flt_ls.coords))
            for afs in flt_ls.coords:
                #print(afs[1])
                if(m2l_utils.mod_safe(i,fault_decimate)==0 or i==int((len(flt_ls.coords)-1)/2) or i==len(flt_ls.coords)-1): #decimate to reduce number of points, but also take mid and end points of a series to keep some shape
                    locations=[(afs[0],afs[1])]     
                    height=m2l_utils.value_from_raster(dataset,locations)
                    ostr=str(afs[0])+","+str(afs[1])+","+str(height)+","+fault_name+"\n"
                    f.write(ostr)                
                i=i+1  
            #print(flt_ls.coords[0][0],flt_ls.coords[0][1],flt_ls.coords[len(flt_ls.coords)-1][0],flt_ls.coords[len(flt_ls.coords)-1][1])
            #print()
            dlsx=flt_ls.coords[0][0]-flt_ls.coords[len(flt_ls.coords)-1][0]
            dlsy=flt_ls.coords[0][1]-flt_ls.coords[len(flt_ls.coords)-1][1]
            if(dlsx==0.0 or dlsy == 0.0):
                continue
            lsx=dlsx/sqrt((dlsx*dlsx)+(dlsy*dlsy))
            lsy=dlsy/sqrt((dlsx*dlsx)+(dlsy*dlsy))        
            #angle = acos(lsx)
            azimuth=degrees(atan2(lsy,-lsx)) % 180 #normal to line segment           
            #azimuth = (degrees(angle) + 360) % 180 
            #print(azimuth)
            locations=[(flt_ls.coords[int((len(afs)-1)/2)][0],flt_ls.coords[int((len(afs)-1)/2)][1])]     
            height=m2l_utils.value_from_raster(dataset,locations)
            ostr=str(flt_ls.coords[int((len(flt_ls.coords)-1)/2)][0])+","+str(flt_ls.coords[int((len(flt_ls.coords)-1)/2)][1])+","+height+","+str(azimuth)+",90,1,"+fault_name+"\n"
            fo.write(ostr)
            strike=sqrt((dlsx*dlsx)+(dlsy*dlsy))
            ostr=fault_name+","+str(strike)+","+str(strike/2.0)+","+str(strike)+"\n"
            fd.write(ostr)

    f.close()
    fo.close()
    fd.close()
    print("fault orientations saved as",path_fault_orientations+'fault_orientations.csv')
    print("fault positions saved as",path_fault_orientations+'faults.csv')
    print("fault dimensions saved as",path_fault_orientations+'fault_dimensions.csv')
    
#Save fold axial traces 
def save_fold_axial_traces(path_folds,path_fold_orientations,dataset,ocode,tcode,fcode,fold_decimate):
    folds_clip=gpd.read_file(path_folds)
    fo=open(path_fold_orientations+'/fold_axial_traces.csv',"w")
    fo.write("X,Y,Z,code,type\n")

    for fold in folds_clip.iterrows():
        fold_name=str(fold[1][ocode])   
        fold_ls=LineString(fold[1].geometry)

        i=0
        for afs in fold_ls.coords:
            if('Fold' in fold[1][fcode]):
                if(m2l_utils.mod_safe(i,fold_decimate)==0 or i==int((len(fold_ls.coords)-1)/2) or i==len(fold_ls.coords)-1): #decimate to reduce number of points, but also take mid and end points of a series to keep some shape
                    locations=[(afs[0],afs[1])]     
                    height=m2l_utils.value_from_raster(dataset,locations)
                    ostr=str(afs[0])+','+str(afs[1])+','+str(height)+','+'FA_'+fold_name+','+fold[1][tcode].replace(',','')+'\n'
                    fo.write(ostr)                
            i=i+1  

    fo.close()
    print("fold axial traces saved as",path_fold_orientations+'fold_axial_traces.csv')

#Create basal contact points with orientation from orientations and basal points
def create_basal_contact_orientations(contacts,structures,output_path,dtm,dist_buffer,ccode,gcode,dcode,ddcode):
    f=open(output_path+'projected_dip_contacts2.csv',"w")
    f.write('X,Y,Z,azimuth,dip,polarity,formation\n')
    #print("len=",len(contacts))
    i=0
    for acontact in contacts.iterrows():   #loop through distinct linestrings
        #display(acontact[1].geometry)
        thegroup=acontact[1][gcode].replace("_"," ")
        #print("thegroup=",thegroup)
        is_gp=structures[gcode] == thegroup # subset orientations to just those with this group
        all_structures = structures[is_gp]

        for astr in all_structures.iterrows(): # loop through valid orientations

            orig = Point(astr[1]['geometry'])
            np = acontact[1].geometry.interpolate(acontact[1].geometry.project(orig))
            if(np.distance(orig)<dist_buffer):

                for line in acontact[1].geometry: # loop through line segments
                    for pair in m2l_utils.pairs(list(line.coords)): # loop through line segments
                        segpair=LineString((pair[0],pair[1]))
                        if segpair.distance(np)< 0.0001: # line segment closest to close point
                            ddx=sin(radians(astr[1][ddcode]))
                            ddy=cos(radians(astr[1][ddcode]))
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
                                ostr=str(np.x)+","+str(np.y)+","+height+","+str(ls_ddir)+","+str(astr[1][dcode])+",1,"+acontact[1][ccode].replace(" ","_").replace("-","_")+"\n" 
                                f.write(ostr)
                                i=i+1


    f.close()
    print("basal contact orientations saved as",output_path+'projected_dip_contacts2.csv')

def process_plutons(tmp_path,output_path,geol_clip,local_paths,dtm,sill_label,pluton_form,pluton_dip,intrusive_label,contact_decimate,mincode,maxcode,ccode,gcode,ocode,r1code,dscode):
    f=open(tmp_path+'groups.csv',"r")
    groups =f.readlines()
    f.close

    ngroups=groups[0].split(" ")
    ngroups=int(ngroups[1])

    orig_ngroups=ngroups

    gp_ages=np.zeros((1000,3))
    gp_names=np.zeros((1000),dtype='U25')

    for i in range (0,ngroups):
        gp_ages[i,0]=-1e6 # group max_age
        gp_ages[i,1]=1e6 # group min_age
        gp_ages[i,2]=i # group index
        gp_names[i]=groups[i+1].replace("\n","")
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
        ades=str(ageol[1][dscode])
        arck=str(ageol[1][r1code])
        if(str(ageol[1][gcode])=='None'):
            agroup=str(ageol[1][ccode])
        else:
            agroup=str(ageol[1][gcode])
        
        for i in range(0,ngroups):
            if (gp_names[i]==agroup):
                if(int(ageol[1][maxcode]) > gp_ages[i][0]  ):
                    gp_ages[i][0] = ageol[1][maxcode]
                    #print("max",agroup,gp_ages[i][0])
                if(int(ageol[1][mincode]) < gp_ages[i][1]  ):
                    gp_ages[i][1] = ageol[1][mincode]
                    #print("min",agroup,gp_ages[i][1])
        if(intrusive_label in arck and sill_label not in ades):
            newgp=str(ageol[1][ccode])+'_'+str(ageol[1][ocode])
            #agp=str(ageol[1][gcode])
            #print(newgp)
            if(str(ageol[1][gcode])=='None'):
                agp=str(ageol[1][ccode])
            else:
                agp=str(ageol[1][gcode])

            if(not newgp  in gp_names):
                #print("MMMMM",ngroups,newgp)
                gp_names[ngroups]=newgp
                gp_ages[ngroups][0]=ageol[1][maxcode]
                gp_ages[ngroups][1]=ageol[1][mincode]
                gp_ages[ngroups][2]=ngroups
                ngroups=ngroups+1
            #else:
                #print("-----",ngroups,newgp)
                
            neighbours=[]
            j+=1
            central_age=ageol[1][mincode]    #absolute age of central polygon
            central_poly=ageol[1].geometry
            for bgeol in geol_clip.iterrows(): #potential neighbouring polygons  
                if(ageol[1].geometry!=bgeol[1].geometry): #do not compare with self
                    if (ageol[1].geometry.intersects(bgeol[1].geometry)): # is a neighbour
                        neighbours.append([(bgeol[1][ccode],bgeol[1][mincode],bgeol[1][r1code],bgeol[1][dscode],bgeol[1].geometry)])  
            #display(neighbours)
            if(len(neighbours) >0):
                for i in range (0,len(neighbours)):
                    if((intrusive_label in neighbours[i][0][2] and sill_label not in ades) 
                       #or ('intrusive' not in neighbours[i][0][2]) and neighbours[i][0][1] > central_age ): # neighbour is older than central
                       or (intrusive_label not in neighbours[i][0][2]) and neighbours[i][0][1]  ): # neighbour is older than central
                        #print(ageol[1][ccode],neighbours[i][0][0])
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
                            #print("lenlenlen",len(LineStringC))

                            #display(LineStringC)
                            ls_dict[id] = {"id": id,ccode:newgp,gcode:newgp, "geometry": LineStringC}
                            id=id+1
                            for lineC in LineStringC: #process all linestrings
                                #if(contact_decimate!=0): #decimate to reduce number of points
                                if(m2l_utils.mod_safe(k,contact_decimate)==0 or k==int((len(LineStringC)-1)/2) or k==len(LineStringC)-1): #decimate to reduce number of points, but also take second and third point of a series to keep gempy happy
                                    locations=[(lineC.coords[0][0],lineC.coords[0][1])] #doesn't like point right on edge?
                                    #print(k,type(lineC))
                                    if(lineC.coords[0][0] > dtm.bounds[0] and lineC.coords[0][0] < dtm.bounds[2] and  
                                       lineC.coords[0][1] > dtm.bounds[1] and lineC.coords[0][1] < dtm.bounds[3]):       
                                            height=m2l_utils.value_from_raster(dtm,locations)
                                            ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+height+","+newgp.replace(" ","_").replace("-","_")+"\n"
                                            ac.write(ostr)
                                            allc.write(agp+","+str(ageol[1][ocode])+","+ostr)
                                            ls_dict_decimate[allpts] = {"id": allpts,ccode:newgp,gcode:newgp, "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                            allpts+=1 
                                    else:
                                        continue
                                        #print("debug:edge points")
                                else:
                                    if(lineC.coords[0][0] > dtm.bounds[0] and lineC.coords[0][0] < dtm.bounds[2] and  
                                            lineC.coords[0][1] > dtm.bounds[1] and lineC.coords[0][1] < dtm.bounds[3]):       
                                        height=m2l_utils.value_from_raster(dtm,locations)
                                        ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+height+","+newgp.replace(" ","_").replace("-","_")+"\n"
                                        #ls_dict_decimate[allpts] = {"id": id,"CODE":ageol[1]['CODE'],"GROUP_":ageol[1]['GROUP_'], "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                        allc.write(agp+","+str(ageol[1][ocode])+","+ostr)
                                        allpts+=1
                                
                                #print(m2l_utils.mod_safe(k,contact_decimate))
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
                                    elif(pluton_form=='dontknow'):
                                        ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+str(height)+","+str(azimuth)+","+str(pluton_dip)+",0,"+newgp.replace(" ","_").replace("-","_")+"\n"
                                    else: #pluton_form == pancakes
                                        azimuth=(azimuth-180)%360
                                        ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+str(height)+","+str(azimuth)+","+str(pluton_dip)+",1,"+newgp.replace(" ","_").replace("-","_")+"\n"
                                        
                                    ao.write(ostr)

                                k+=1
                        elif(LineStringC.wkt.split(" ")[0]=='LINESTRING'): # apparently this is not needed
                            #print("debug:LINESTRING")
                            k=0
                            for pt in LineStringC.coords: #process one linestring
                                #if(i%contact_decimate==0): #decimate to reduce number of points
                                #print("ls",pt)
                                k+=1
                        elif(LineStringC.wkt.split(" ")[0]=='POINT'): # apparently this is not needed
                            #print("debug:POINT")
                            #print("pt",LineStringC.coords)
                            k+=1
                        else:
                            #print(LineStringC.wkt.split(" ")[0]) # apparently this is not needed
                            k+=1
    ac.close()
    ao.close()
    allc.close()

    #print(ngroups)
    #for i in range (0,ngroups):
    #    print(i,gp_names[i])

    #display(gp_ages[:ngroups])
    #display(gp_names[:ngroups])

    #ga=gp_ages[:ngroups]
    #print("XXXXXXXXXXXXX",ga)
    #f=ga[:,0].argsort()
    #display(f)
      
    an=open(tmp_path+'groups2.csv',"w")
    an.write('1 '+str(ngroups)+'\n')
    for i in range (orig_ngroups,ngroups):
        print(i,gp_names[i].replace(" ","_").replace("-","_"))
        an.write(gp_names[i].replace(" ","_").replace("-","_")+'\n')
        gp=open(tmp_path+''+gp_names[i].replace(" ","_").replace("-","_")+'.csv',"w")
        gp.write('1 1\n'+gp_names[i].replace(" ","_").replace("-","_")+'\n')
        gp.close()
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
    for i in range (orig_ngroups,ngroups):
        index=str(int(all_sorts.iloc[len(all_sorts)-1]['index'])+j)
        group_number=str(int(all_sorts.iloc[len(all_sorts)-1]['group number'])+j)
        print(i,gp_names[i].replace(" ","_").replace("-","_"))
        ostr=index+","+group_number+",1,1,"+gp_names[i].replace(" ","_").replace("-","_")+","+gp_names[i].replace(" ","_").replace("-","_")+"\n"
        all_sorts_file.write(ostr)
        j=j+1

    for i in range(1,len(all_sorts)+1):    
        all_sorts_file.write(contents[i])
        
    all_sorts_file.close()
    print('pluton contacts and orientations saved as:')
    print(output_path+'ign_contacts.csv')
    print(output_path+'ign_orientations_'+pluton_form+'.csv')

def tidy_data(output_path,tmp_path,use_group,use_interpolations):
    contacts=pd.read_csv(output_path+'contacts4.csv',",")
    orientations=pd.read_csv(output_path+'orientations.csv',",")
    invented_orientations=pd.read_csv(output_path+'empty_series_orientations.csv',",")
    interpolated_orientations=pd.read_csv(tmp_path+'combo_full.csv',",")
    intrusive_orientations=pd.read_csv(output_path+'ign_orientations_saucers.csv',",")
    intrusive_contacts=pd.read_csv(output_path+'ign_contacts.csv',",")
    fault_contact=pd.read_csv(output_path+'faults.csv',",")
    fault_orientations=pd.read_csv(output_path+'fault_orientations.csv',",")
    all_sorts=pd.read_csv(tmp_path+'all_sorts2.csv',",")
    combo_full_orientations=pd.read_csv(tmp_path+'combo_full.csv',",")

    if(use_interpolations):
        all_orientations=pd.concat([orientations,invented_orientations,intrusive_orientations,combo_full_orientations.iloc[::2, :]])
    else:
        all_orientations=pd.concat([orientations,invented_orientations,intrusive_orientations])
        
    all_orientations.reset_index(inplace=True)

    all_sorts.set_index('code',  inplace = True)

    #all_contacts=pd.concat([intrusive_contacts,contacts.iloc[::2, :]])
    all_contacts=pd.concat([intrusive_contacts,contacts])
    all_contacts.reset_index(inplace=True)
    #display(all_sorts)
    all_groups=set(all_sorts['group'])
    #print(all_groups)
    #display("all_sorts",all_sorts,"all_contact_fm",all_contacts.formation.unique(),"all_gps",all_groups,"use_gp",use_group)
    unique_contacts=set(all_contacts['formation'])

    # Remove groups that don't have any contact info
    no_contacts=[]
    groups=[]
    for agroup in all_groups:
        found=False
        #print('GROUP',agroup)
        for acontact in all_contacts.iterrows():
            #if(all_sorts.loc[acontact[1]['formation']]['group'] in agroup and all_sorts.loc[acontact[1]['formation']]['group'] in use_group):
            if(all_sorts.loc[acontact[1]['formation']]['group'] in agroup ):
                found=True
                #print(all_sorts.loc[acontact[1]['formation']]['group'])
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

    ngroups=contents[0].split(" ")
    ngroups=int(ngroups[1])       
    no_contacts=[]
    groups=[]

    for i in range(1,ngroups+1):
        found=False
        #print('GROUP',agroup)
        for acontact in all_contacts.iterrows():
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
    fgp.write('1 '+str(len(groups))+'\n')
    for i in range(0,len(groups)):
        fgp.write(contents[i+1].replace("\n","")+'\n')
    fgp.close()        

    # Remove orientations with no equivalent formations info

    for agroup in all_groups:
        found=False
        #print('GROUP',agroup)
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
        #print(a_sort[0])
        if(a_sort[1]['group'] not in no_contacts):
            ostr=str(a_sort[1]['index'])+","+str(a_sort[1]['group number'])+","+str(a_sort[1]['index in group'])+","+str(a_sort[1]['number in group'])+","+a_sort[0]+","+a_sort[1]['group']+",erode\n"
            fas.write(ostr)
    fas.close()

    # Update orientation info

    fao=open(output_path+'orientations_clean.csv',"w")
    fao.write('X,Y,Z,azimuth,dip,polarity,formation\n')

    for ano in all_orientations.iterrows():
        #if any(grp in all_sorts.loc[ano[1]['formation']]['group'] for grp in no_contacts):
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

    