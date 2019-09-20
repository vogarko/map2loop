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
def save_orientations(structures,mname,path_out,ddcode,dcode,ccode,orientation_decimate,dtm):
    i=0
    f=open(path_out+'/'+mname+'_orientations.txt',"w")
    f.write("X,Y,Z,azimuth,dip,polarity,formation\n")
    for apoint in structures.iterrows():
        if(apoint[1][dcode]!=0 and m2l_utils.mod_safe(i,orientation_decimate)==0):
            locations=[(apoint[1]['geometry'].x, apoint[1]['geometry'].y)]

        if(apoint[1]['geometry'].x > dtm.bounds[0] and apoint[1]['geometry'].x < dtm.bounds[2] and  
               apoint[1]['geometry'].y > dtm.bounds[1] and apoint[1]['geometry'].y < dtm.bounds[3]):       
                height=m2l_utils.value_from_raster(dtm,locations)
                ostr=str(apoint[1]['geometry'].x)+","+str(apoint[1]['geometry'].y)+","+height+","+str(apoint[1][ddcode])+","+str(apoint[1][dcode])+",1,"+str(apoint[1][ccode])+"\n"
                f.write(ostr)
                i+=1
        
    f.close()

#Find those series that don't have any orientation or contact point data and add some random data
def create_orientations(mname, path_in, dtm,geology,structures,ccode,gcode):
    f=open(path_in+'/'+mname+'_groups.txt',"r")
    contents =f.readlines()
    f.close

    ngroups=contents[0].split(" ")
    ngroups=int(ngroups[1])

    groups=[]
    for i in range (1,int(ngroups)+1):
        #print(contents[i].replace("\n",""))
        groups.append((contents[i].replace("\n",""),0))

    print(ngroups,groups)

    for i in range (0,ngroups):
        for apoint in structures.iterrows():
            agroup=apoint[1][gcode]
            #print(agroup)
            if(groups[i][0]==agroup):
                lgroups=list(groups[i])
                lgroups[1]=1
                lgroups=tuple(lgroups)
                groups[i]=lgroups

    print("Orientations----------\n",ngroups,groups)

    for i in range (0,ngroups):
        for apoly in geology.iterrows():
            agroup=apoint[1][gcode]
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

    f=open(path_in+'/'+mname+'_orientations.txt',"a")

    for i in range (0,ngroups):
        if(groups[i][1]==0):
            for ageol in geology.iterrows():
                if(ageol[1][ccode]==groups[i][0] and groups[i][1]==0):
                    apoly=Polygon(ageol[1]['geometry'])
                    apoint=apoly.representative_point()
                    #print(apoint.x,apoint.y)
                    locations=[(apoint.x,apoint.y)]
                    height=m2l_utils.value_from_raster(dtm,locations)
                    if(height==-999):
                        print("point off map",locations)
                        height=0   # needs a better solution!
                    ostr=str(apoint.x)+","+str(apoint.y)+","+height+",0,45,1"+","+str(ageol[1][ccode])+"\n"
                    f.write(ostr)
                    plt.title(str(ageol[1][ccode]))
                    plt.scatter(apoint.x,apoint.y,color="red")
                    plt.plot(*apoly.exterior.xy)
                    plt.show()
                    break

    f.close()

#Export contact information subset of each polygon to csv format
def save_basal_contacts(mname,path_in,dtm,geol_clip,contact_decimate,ccode,gcode):
    print("decimation: 1 /",contact_decimate)

    ## Reproject topography to approriate metre-based CRS
               
    #dataset = rasterio.open(path_in+'/'+mname+'_dtm_rp.tif')
    ag=open(path_in+'/'+mname+'_all_sorts.txt',"r")
    contents =ag.readlines()
    ag.close
    print("surfaces:",len(contents))
    print("polygons:",len(geol_clip))
    ulist=[]
    for i in range(1,len(contents)):
        #print(contents[i].replace("\n",""))
        cont_list=contents[i].split(",")
        ulist.append([i, cont_list[4].replace("\n","")])
    print(ulist)

    allc=open(path_in+'/'+mname+'all_contacts.txt',"w")
    allc.write('GROUP_,id,x,y,z,code\n')
    ac=open(path_in+'/'+mname+'_contacts.txt',"w")
    ac.write("X,Y,Z,formation\n")
    print(dtm.bounds)
    j=0
    allpts=0
    ls_dict={}
    ls_dict_decimate={}
    id=0
    for ageol in geol_clip.iterrows(): # central polygon
        agp=str(ageol[1]['GROUP_'])
        if(agp=='None'):
            agp=ageol[1]['CODE']
        #print(agp,type(agp))
        neighbours=[]
        #print(ageol[1].geometry)
        j+=1
        out=[item for item in ulist if ageol[1][ccode] in item]
        if(len(out)>0):
            central=out[0][0]    #relative age of central polygon
            central_poly=ageol[1].geometry
            for bgeol in geol_clip.iterrows(): #potential neighbouring polygons  
                if(ageol[1].geometry!=bgeol[1].geometry): #do not compare with self
                    if (ageol[1].geometry.intersects(bgeol[1].geometry)): # is a neighbour
                        neighbours.append([(bgeol[1][ccode],bgeol[1].geometry)])  

            if(len(neighbours) >0):
                for i in range (0,len(neighbours)):
                    out=[item for item in ulist if neighbours[i][0][0] in item]
                    #print(out)
                    if(len(out)>0):
                        #if(out[0][0] > central and out[0][0] < youngest_older): # neighbour is older than central, and younger than previous candidate
                        if(out[0][0] > central ): # neighbour is older than central
                            older_polygon=neighbours[i][0][1]
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
                                ls_dict[id] = {"id": id,"CODE":ageol[1][ccode],"GROUP_":ageol[1][gcode], "geometry": LineStringC}
                                id=id+1
                                for lineC in LineStringC: #process all linestrings
                                    #if(contact_decimate!=0): #decimate to reduce number of points
                                    if(m2l_utils.mod_safe(k,contact_decimate)==0 or k==int((len(LineStringC)-1)/2) or k==len(LineStringC)-1): #decimate to reduce number of points, but also take second and third point of a series to keep gempy happy
                                        locations=[(lineC.coords[0][0],lineC.coords[0][1])] #doesn't like point right on edge?
                                        #print(k,type(lineC))
                                        if(lineC.coords[0][0] > dtm.bounds[0] and lineC.coords[0][0] < dtm.bounds[2] and  
                                           lineC.coords[0][1] > dtm.bounds[1] and lineC.coords[0][1] < dtm.bounds[3]):       
                                                height=m2l_utils.value_from_raster(dtm,locations)
                                                ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+height+","+str(ageol[1][ccode])+"\n"
                                                ac.write(ostr)
                                                allc.write(agp+","+str(ageol[1]['OBJECTID_1'])+","+ostr)
                                                ls_dict_decimate[allpts] = {"id": allpts,"CODE":ageol[1]['CODE'],"GROUP_":ageol[1]['GROUP_'], "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                                allpts+=1 
                                        else:
                                            continue
                                            #print("debug:edge points")
                                    else:
                                        locations=[(lineC.coords[0][0]+0.0000001,lineC.coords[0][1])] #doesn't like point right on edge?
                                        if(lineC.coords[0][0] > dtm.bounds[0] and lineC.coords[0][0] < dtm.bounds[2] and  
                                            lineC.coords[0][1] > dtm.bounds[1] and lineC.coords[0][1] < dtm.bounds[3]):       
                                            height=m2l_utils.value_from_raster(dtm,locations)
                                            ostr=str(lineC.coords[0][0])+","+str(lineC.coords[0][1])+","+height+","+str(ageol[1][ccode])+"\n"
                                            #ls_dict_decimate[allpts] = {"id": id,"CODE":ageol[1]['CODE'],"GROUP_":ageol[1]['GROUP_'], "geometry": Point(lineC.coords[0][0],lineC.coords[0][1])}
                                            allc.write(agp+","+str(ageol[1]['OBJECTID_1'])+","+ostr)
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
                                #print("debug:LINESTRING")
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
                                #print(LineStringC.wkt.split(" ")[0]) # apparently this is not needed
                                k+=1


    ac.close()
    allc.close()
    print("allpts=",allpts)
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

        if(cnf_copy.iloc[j].geom_type=="GeometryCollection"):#remove rows with geometry collections (== empty?)
            cnf_copy.drop([j-1,j],inplace=True)
        else: # save to dataframe
            ls_nf[i]= {"id": i,"CODE":df.iloc[i][ccode],"GROUP_":df.iloc[i][gcode], "geometry": cnf_copy.iloc[j]}



    df_nf = DataFrame.from_dict(ls_nf, "index")

    contacts_nf = GeoDataFrame(df_nf,crs=dst_crs, geometry='geometry')
    contacts_nf.to_file(driver = 'ESRI Shapefile', filename= path_out)

    #contacts_nofaults = gpd.read_file('./data/faults_clip.shp')
    #print(contacts_nofaults.shape)

#Remove faults from decimated basal contacts as save as csv file   
def save_contacts_with_faults_removed(mname,path_fault,path_out,dist_buffer,ls_dict,ls_dict_decimate,ccode,dst_crs,dataset):
    faults_clip = gpd.read_file(path_fault)

    df = DataFrame.from_dict(ls_dict, "index")
    contacts = GeoDataFrame(df,crs=dst_crs, geometry='geometry')

    fault_zone = faults_clip.buffer(dist_buffer) #defines buffer around faults where strat nodes will be removed
    all_fz = fault_zone.unary_union

    print(len(ls_dict_decimate))
    df_nf = DataFrame.from_dict(ls_dict_decimate, "index")

    contacts_nf_deci = GeoDataFrame(df_nf,crs=dst_crs, geometry='geometry')
 
 
    contacts_decimate_nofaults = contacts_nf_deci.difference(all_fz) #deletes contact nodes within buffer
    cnf_de_copy=contacts_decimate_nofaults.copy()

    ac=open(path_out+'/'+mname+'_contacts4.txt',"w")
    ac.write("X,Y,Z,formation\n")
    i=0
    for cdn in contacts_decimate_nofaults:
        if(not cdn.geom_type=="GeometryCollection"):
            #print(cdn.x,cdn.y)
            locations=[(cdn.x,cdn.y)] #doesn't like point right on edge?
          
            height=m2l_utils.value_from_raster(dataset,locations)
            ostr=str(cdn.x)+","+str(cdn.y)+","+height+","+str(df_nf.iloc[i][ccode])+"\n"
            ac.write(ostr)

        i=i+1
    ac.close()
    print("decimated points:",i)

#Save faults as contact info and make vertical (for the moment)
def save_faults(mname,path_faults,path_fault_orientations,dataset,ncode,fault_decimate):
    faults_clip=gpd.read_file(path_faults)
    f=open(path_fault_orientations+'/'+mname+'_faults.txt',"w")
    f.write("X,Y,Z,formation\n")
    fo=open(path_fault_orientations+'/'+mname+'_fault_orientations.txt',"w")
    fo.write("X,Y,Z,azimuth,dip,polarity,formation\n")

    for flt in faults_clip.iterrows():
        #if(flt[1][ncode]=='Karra Well Fault'): #<<<<<<<<<<<< When too many faults gets ugly!
        if(True): #<<<<<<<<<<<< Not sure what to do with so many faults!
            if(str(flt[1]['NAME'])=='None'):
                fault_name='Fault_'+str(flt[1]['OBJECTID'])
            else:
                fault_name=str(flt[1]['NAME'])   
            #print(flt)
            flt_ls=LineString(flt[1].geometry)
            #print(flt_ls)

            i=0
            print(len(flt_ls.coords))
            for afs in flt_ls.coords:
                #print(afs[1])
                if(m2l_utils.mod_safe(i,fault_decimate)==0 or i==int((len(flt_ls.coords)-1)/2) or i==len(flt_ls.coords)-1): #decimate to reduce number of points, but also take mid and end points of a series to keep some shape
                    locations=[(afs[0],afs[1])]     
                    height=m2l_utils.value_from_raster(dataset,locations)
                    ostr=str(afs[0])+","+str(afs[1])+","+height+","+fault_name+"\n"
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
            print(azimuth)
            locations=[(flt_ls.coords[int((len(afs)-1)/2)][0],flt_ls.coords[int((len(afs)-1)/2)][1])]     
            height=m2l_utils.value_from_raster(dataset,locations)
            ostr=str(flt_ls.coords[int((len(flt_ls.coords)-1)/2)][0])+","+str(flt_ls.coords[int((len(flt_ls.coords)-1)/2)][1])+","+height+","+str(azimuth)+",90,1,"+fault_name+"\n"
            fo.write(ostr)

    f.close()
    fo.close()

#Create basal contact points with orientation from orientations and basal points
def create_basal_contact_orientations(mname,contacts,structures,output_path,dtm,dist_buffer,ccode,gcode,dcode,ddcode):
    f=open(output_path+mname+'_projected_dip_contacts2.txt',"w")
    f.write('X,Y,Z,azimuth,dip,polarity,formation\n')
    #print("len=",len(contacts))
    i=0
    for acontact in contacts.iterrows():   #loop through distinct linestrings
        #display(acontact[1].geometry)
        thegroup=acontact[1][gcode]
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
                                ostr=str(np.x)+","+str(np.y)+","+height+","+str(ls_ddir)+","+str(astr[1][dcode])+",1,"+acontact[1][ccode]+"\n" 
                                f.write(ostr)
                                i=i+1


    f.close()
