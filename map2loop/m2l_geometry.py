from shapely import geometry
from shapely.geometry import shape, Polygon, LineString, Point
import matplotlib.pyplot as plt
import requests
import rasterio
from pandas import DataFrame
from geopandas import GeoDataFrame
import geopandas as gpd
from math import acos, sqrt, cos, sin, degrees, radians, fabs, atan2
import m2l_utils

#Export orientation data in csv format with heights and strat code added
def save_orientations(structures,mname,path_out,ddcode,dcode,ccode,rcode,orientation_decimate,dtm):
    i=0
    f=open(path_out+'/'+mname+'_orientations.csv',"w")
    f.write("X,Y,Z,azimuth,dip,polarity,formation\n")
    for apoint in structures.iterrows():
        if(not 'intrusive' in apoint[1][rcode]):
            if(apoint[1][dcode]!=0 and m2l_utils.mod_safe(i,orientation_decimate)==0):
                locations=[(apoint[1]['geometry'].x, apoint[1]['geometry'].y)]
                if(apoint[1]['geometry'].x > dtm.bounds[0] and apoint[1]['geometry'].x < dtm.bounds[2] and  
                    apoint[1]['geometry'].y > dtm.bounds[1] and apoint[1]['geometry'].y < dtm.bounds[3]):       
                    height=m2l_utils.value_from_raster(dtm,locations)
                    ostr=str(apoint[1]['geometry'].x)+","+str(apoint[1]['geometry'].y)+","+height+","+str(apoint[1][ddcode])+","+str(apoint[1][dcode])+",1,"+str(apoint[1][ccode].replace(" ","_").replace("-","_"))+"\n"
                    f.write(ostr)
                    i+=1
        
    f.close()
    print(i,'orientations saved to',path_out+'/'+mname+'_orientations.csv')

#Find those series that don't have any orientation or contact point data and add some random data
def create_orientations(mname, path_in, path_out,dtm,geology,structures,ccode,gcode):
    f=open(path_in+'/'+mname+'_groups.csv',"r")
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

    f=open(path_out+'/'+mname+'_empty_series_orientations.csv',"w")
    f.write("X,Y,Z,azimuth,dip,polarity,formation\n")

    for i in range (0,ngroups):
        if(groups[i][1]==0):
            for ageol in geology.iterrows():
                if(ageol[1][ccode].replace("-","_")==groups[i][0] and groups[i][1]==0):
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
    print('extra orientations saved as',path_out+'/'+mname+'_empty_series_orientations.csv')

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
def save_basal_contacts(mname,path_in,dtm,geol_clip,contact_decimate,ccode,gcode,ocode,dscode,r1code,intrusion_mode):
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
               
    #dataset = rasterio.open(path_in+'/'+mname+'_dtm_rp.tif')
    ag=open(path_in+'/'+mname+'_all_sorts.csv',"r")
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

    allc=open(path_in+'/'+mname+'_all_contacts.csv',"w")
    allc.write('GROUP_,id,x,y,z,code\n')
    ac=open(path_in+'/'+mname+'_contacts.csv',"w")
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
    print("saved as",path_in+mname+'_all_contacts.csv',"and",path_in+mname+'_contacts.csv')
    return(ls_dict,ls_dict_decimate)

#Remove all basal contacts that are defined by faults and save to shapefile (no decimation)
def save_basal_no_faults(mname,path_out,path_fault,ls_dict,dist_buffer,ccode,gcode,dst_crs):
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
def save_contacts_with_faults_removed(mname,path_fault,path_out,dist_buffer,ls_dict,ls_dict_decimate,ccode,dst_crs,dataset):
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
    
    ac=open(path_out+'/'+mname+'_contacts4.csv',"w")
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
    print(i,"decimated contact points saved as",path_out+'/'+mname+'_contacts4.csv')
    
#Save faults as contact info and make vertical (for the moment)
def save_faults(mname,path_faults,path_fault_orientations,dataset,ncode,ocode,fcode,fault_decimate):
    faults_clip=gpd.read_file(path_faults)
    f=open(path_fault_orientations+'/'+mname+'_faults.csv',"w")
    f.write("X,Y,Z,formation\n")
    fo=open(path_fault_orientations+'/'+mname+'_fault_orientations.csv',"w")
    fo.write("X,Y,Z,azimuth,dip,polarity,formation\n")

    for flt in faults_clip.iterrows():
        #if(flt[1][ncode]=='Karra Well Fault'): #<<<<<<<<<<<< When too many faults gets ugly!
        if('Fault' in flt[1][fcode]):
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

    f.close()
    fo.close()
    print("fault orientations saved as",path_fault_orientations+mname+'_fault_orientations.csv')
    print("fault positions saved as",path_fault_orientations+mname+'_faults.csv')
    
#Save fold axial traces 
def save_fold_axial_traces(mname,path_folds,path_fold_orientations,dataset,ocode,tcode,fcode,fold_decimate):
    folds_clip=gpd.read_file(path_folds)
    fo=open(path_fold_orientations+'/'+mname+'_fold_axial_traces.csv',"w")
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
    print("fold axial traces saved as",path_fold_orientations+'/'+mname+'_fold_axial_traces.csv')

#Create basal contact points with orientation from orientations and basal points
def create_basal_contact_orientations(mname,contacts,structures,output_path,dtm,dist_buffer,ccode,gcode,dcode,ddcode):
    f=open(output_path+mname+'_projected_dip_contacts2.csv',"w")
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
    print("basal contact orientations saved as",output_path+mname+'_projected_dip_contacts2.csv')
