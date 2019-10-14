import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np
import functools 
import operator  

#parse stratigraphy GML file to get number of series and series names
def get_series(path_in,id_label):
    G=nx.read_gml(path_in,label=id_label) # load a stratigraphy with groups needs to feed via yed!!

    glabels = {}
    groups=0
    nlist=list(G.nodes)
    for n in nlist: # Find out total number of groups and their names groups
        if('isGroup' in G.nodes[n]):
            groups+=1
            glabels[n]=G.nodes[n]['LabelGraphics']['text'].replace(" ","_").replace("-","_")
    return(groups,glabels,G)

#parse stratigraphy GML file to save units for each series
def save_units(G,path_out,glabels):
    for p in glabels: #process each group, removing nodes that are not part of that group, and other groups
        GD=G.copy() #temporary copy of full graph
        print()
        print(p,glabels[p].replace(" ","_").replace("-","_"),"----------------------")
        nlist=list(G.nodes)
        #display(nlist)
        for n in nlist: # Calculate total number of groups and their names groups
            if('gid' in GD.nodes[n]): #normal node
                if(GD.nodes[n]['gid']!=p): #normal node but not part of current group
                    GD.remove_node(n)
            else:                     #group node
                GD.remove_node(n)
        elist=list(G.edges)
        #display(elist)
        egraphics=nx.get_edge_attributes(G,'graphics')
        #print(egraphics)

        
        labels = {}
        for node in GD.nodes():   #local store of node labels     
            labels[node] = G.nodes[node]['LabelGraphics']['text'].replace(" ","_").replace("-","_")
        
        plt.figure(p+1) #display strat graph for one group
        plt.title(glabels[p])
        nx.draw_networkx(GD, pos=nx.kamada_kawai_layout(GD), arrows=True,with_labels=False)
        nx.draw_networkx_labels(GD,pos=nx.kamada_kawai_layout(GD), labels=labels, font_size=12,font_family='sans-serif')
        
        nlist=list(nx.all_topological_sorts(GD)) #all possible sorted directional graphs
        f = open(path_out+"/"+glabels[p].replace(" ","_").replace("-","_")+'.csv', 'w')

        print("choices:",len(nlist))
        f.write(str(len(nlist))+" ")
        f.write(str(len(GD))+"\n")
        for m in range(len(nlist)): #process all sorted graphs
            for n in range(0,len(GD)): #display nodes for one sorted graph
                print(nlist[m][n],G.nodes[nlist[m][n]]['LabelGraphics']['text'].replace(" ","_").replace("-","_"))
                f.write(G.nodes[nlist[m][n]]['LabelGraphics']['text'].replace(" ","_").replace("-","_")+"\n")
            if(m<len(nlist)-1):
                print("....")
        f.close()


#save out a list of max/min/ave ages of all formations in a group
def abs_age_groups(geol,tmp_path,ccode,gcode,mincode,maxcode):
    groups=[]
    info=[]
    ages=[]
    for a_poly in geol.iterrows(): #loop through all polygons
        if(str(a_poly[1][gcode])=='None'):
            grp=a_poly[1][ccode].replace(" ","_").replace("-","_")
        else:
            grp=a_poly[1][gcode].replace(" ","_").replace("-","_")
        #print(grp)
        if(not grp in groups):
            groups+=[(grp)]

        info+=[(grp,a_poly[1][mincode],a_poly[1][maxcode])]

    #display(info)
    #display(groups)
    for j in range(0,len(groups)):
        #print(groups[j],'------------------')
        min_age=1e10
        max_age=0
        for i in range(0,len(info)):
            if(info[i][0]==groups[j]):
                if(float(info[i][1])<min_age):
                    min_age=float(info[i][1])
                    min_ind=i
                if(float(info[i][2])>max_age):
                    max_age=float(info[i][2])
                    max_ind=i
#        print(groups[j],min_age,max_age,(max_age+min_age)/2)
        ages+=[(groups[j],min_age,max_age,(max_age+min_age)/2)]
#    print()
#    for j in range(0,len(ages)):
#        print(ages[j][0],ages[j][1],ages[j][2],ages[j][3],sep='\t')
#    print()

    slist=sorted(ages,key=lambda l:l[3])
    f=open(tmp_path+'age_sorted_groups.csv','w')
    f.write('index,group_,min,max,ave\n')
    for j in range(0,len(slist)):
        f.write(str(j)+','+slist[j][0]+','+str(slist[j][1])+','+str(slist[j][2])+','+str(slist[j][3])+'\n')
    f.close()
    
    
def save_group(G,mname,path_out,glabels,geol,ccode,gcode,mincode,maxcode):
    Gp=nx.Graph().to_directed() #New Group graph
    
    geology_file=gpd.read_file(path_out+'geol_clip.shp')

    abs_age_groups(geol,path_out,ccode,gcode,mincode,maxcode)
    geology_file.drop_duplicates(subset =ccode,  inplace = True)
    

    geology_file.set_index(ccode,  inplace = True)
    #display(geology_file)
    
    gp_ages = pd.read_csv(path_out+'age_sorted_groups.csv') 
    display(gp_ages)
    gp_ages.set_index('group_',  inplace = True)

    display(gp_ages)
    gp_ids=[]
    nlist=list(G.nodes)
    for n in nlist: # Find out total number of groups and their names groups
        if('isGroup' in G.nodes[n]):
            G.add_nodes_from([n])
    
    display(gp_ids)
    for e in G.edges:
        if(G.nodes[e[0]]['gid']!=G.nodes[e[1]]['gid']):
            glabel_0=G.nodes[e[0]]['LabelGraphics']['text']
            glabel_1=G.nodes[e[1]]['LabelGraphics']['text']
            #print(glabel_0,glabel_1)
            #print(geology_file.loc[glabel_0][gcode])
            if(str(geology_file.loc[glabel_0][gcode])=='None'):
                grp0=glabel_0.replace(" ","_").replace("-","_")
            else:
                grp0=geology_file.loc[glabel_0][gcode].replace(" ","_").replace("-","_")
            if(str(geology_file.loc[glabel_1][gcode])=='None'):
                grp1=glabel_1.replace(" ","_").replace("-","_")
            else:
                grp1=geology_file.loc[glabel_1][gcode].replace(" ","_").replace("-","_")
                
            #print(glabel_0,glabel_1,gp_ages.loc[grp0],gp_ages.loc[grp1])
            if(gp_ages.loc[grp0]['ave']<gp_ages.loc[grp1]['ave']):
                Gp.add_edge(G.nodes[e[0]]['gid'],G.nodes[e[1]]['gid'])
    
    GpD=Gp.copy() #temporary copy of full graph
    GpD2=Gp.copy() #temporary copy of full graph

    for e in GpD2.edges: #remove duplicate edges with opposite directions
        for f in GpD.edges:
            if(e[0]==f[1] and e[1]==f[0] and e[0]<f[0]): #arbitrary choice to ensure edge is not completely removed
                Gp.remove_edge(e[0],e[1])

    plt.figure(1) #display strat graph for one group
    plt.title("groups")
    nx.draw_networkx(Gp, pos=nx.kamada_kawai_layout(Gp), arrows=True,with_labels=False)
    nx.draw_networkx_labels(Gp,pos=nx.kamada_kawai_layout(Gp), labels=glabels, font_size=12,font_family='sans-serif')

    glist=list(nx.all_topological_sorts(Gp)) #all possible sorted directional graphs    
    #print("group choices:",len(glist))
    #print(glist)
    nx.write_gml(Gp, path_out+"/"+mname+'_groups.gml')
    plt.show()

    f = open(path_out+"/"+mname+'_groups.csv', 'w')
    f.write(str(len(glist))+" ")
    f.write(str(len(glist[0]))+"\n")

    for n in range(0,len(glist)):
        for m in range(0,len(glist[0])):    
            f.write(str(glabels[glist[0][m]])+"\n") #check underscore
    f.close()


    g=open(path_out+"/"+mname+'_groups.csv',"r")
    contents =g.readlines()
    g.close
    hdr=contents[0].split(" ")

    k=0
    ag=open(path_out+"/"+mname+'_all_sorts.csv',"w")
    ag.write("index,group number,index in group,number in group,code,group\n")
    for i in range(1,int(hdr[1])+1):
        f=open(path_out+"/"+contents[i].replace("\n","").replace(" ","_")+".csv","r")#check underscore
        ucontents =f.readlines()
        f.close
        uhdr=ucontents[0].split(" ")
        for j in range(1,int(uhdr[1])+1):
            print(ucontents[j].replace("\n",""))
            ag.write(str(k)+","+str(i)+","+str(j)+","+uhdr[1].replace("\n","")+","+ucontents[j].replace("\n","")+","+contents[i].replace("\n","").replace(" ","_").replace("-","_")+"\n")
            k=k+1
    ag.close()
    
def parse_fault_relationships(graph_path,tmp_path,output_path):
    uf=open(graph_path+'unit-fault-intersection.txt','r')
    contents =uf.readlines()
    uf.close()

    all_faults={}
    unique_list = [] 

    for row in contents:
        row=row.replace("\n","").split("{")
        unit=row[0].split(',')
        faults=row[1].replace("}","").replace(" ","").split(",")

        for f in faults:
            if f not in unique_list: 
                unique_list.append(f) 

    uf=open(output_path+'unit-fault-relationships.csv','w')
    uf.write('code,'+str(unique_list).replace("[","").replace("'","").replace("]","").replace(" ","")+'\n')
    for row in contents:
        row=row.replace("\n","").split("{")
        unit=row[0].split(',')
        faults=row[1].replace("}","").replace(" ","").split(",")
        ostr=str(unit[1]).strip().replace(" ","_").replace("-","_")
        for ul in unique_list:
            out=[item for item in faults if ul in item]
            if(len(out)>0):
                ostr=ostr+",1"
            else:
                ostr=ostr+",0" 
        uf.write(ostr+"\n")
    uf.close()

    summary=pd.read_csv(tmp_path+'hams3_all_sorts.csv')
    summary.set_index("code", inplace=True)

    uf_rel=pd.read_csv(output_path+'unit-fault-relationships.csv')

    f=open(tmp_path+'hams3_groups.csv',"r")
    groups =f.readlines()
    f.close
    ngroups=groups[0].split(" ")
    ngroups=int(ngroups[1])


    uf_array=uf_rel.to_numpy()
    gf_array=np.zeros((ngroups,uf_array.shape[1]),dtype='U25')
    #print(gf_array.shape)
    #display(uf_array)

    #print(summary.index.values)
    for i in range(1,ngroups+1):
        #print("---------")
        for j in range(0,len(uf_rel)):
            #print("uf_rel",uf_rel.iloc[j][0])
            #print("sum gp",uf_rel.iloc[j][0])
            if(uf_rel.iloc[j][0] in summary.index.values):
                gsummary=summary.loc[uf_rel.iloc[j][0]]
                #print("sum gp",groups[i].replace("\n",""),gsummary['group'])
                if(groups[i].replace("\n","")==gsummary['group']):
                    #print("yes group", groups[i].replace("\n",""),gsummary['group'])
                    for k in range(1,len(uf_rel.iloc[j])):
                        if(uf_rel.iloc[j][k]==1):
                            gf_array[i-1,k]='1'
                            #print(contents[i].replace("\n",""),au,uf_rel.columns[k],uf_rel.iloc[j][k])
                        else:
                            continue
                            #print(contents[i].replace("\n",""),au,uf_rel.columns[k],'nope')
                else:
                    continue
                    #print("not group", groups[i].replace("\n",""),gsummary['group'])
            else:
                continue
                #print("not found",uf_rel.iloc[j][0])
    #display(gf_array)

    #display(gf_array)

    ug=open(output_path+'group-fault-relationships.csv','w')
    ug.write('group')
    for k in range(1,len(uf_rel.iloc[0])):
        ug.write(','+uf_rel.columns[k])
    ug.write("\n")
    for i in range(1,ngroups+1):
        ug.write(groups[i].replace("\n",""))
        for k in range(1,len(uf_rel.iloc[0])):
            if(gf_array[i-1,k]=='1'):
                ug.write(',1')
            else:
                ug.write(',0')
        ug.write("\n")

    ug.close()

    uf=open(graph_path+'fault-fault-intersection.txt','r')
    contents =uf.readlines()
    uf.close()

    unique_list = [] 

    for row in contents:
        row=row.replace("\n","").split("{")
        fault_1o=row[0].split(',')
        fault_1o=fault_1o[1]
        faults_2o=row[1].replace("(","").replace(")","").replace("}","").split(",")

        if fault_1o.replace(" ","") not in unique_list: 
                unique_list.append(fault_1o.replace(" ","")) 
        for i in range (0,len(faults_2o),3):
            if faults_2o[i].replace(" ","") not in unique_list: 
                    unique_list.append(faults_2o[i].replace(" ","")) 
    #display(unique_list) 

    ff=open(output_path+'fault-fault-relationships.csv','w')
    ff.write('fault_id')
    for i in range (0,len(unique_list)):
        ff.write(','+unique_list[i])
    ff.write('\n')

    for i in range(0,len(unique_list)): #loop thorugh rows
        ff.write(unique_list[i]) 
        found=False
        #for j in range(0,len(unique_list)):
        for row in contents: #loop thorugh known intersections
            row=row.replace("\n","").split("{")
            fault_1o=row[0].split(',')
            fault_1o=fault_1o[1]
            faults_2o=row[1].replace("(","").replace(")","").replace("}","").split(",")

            if(unique_list[i].replace(" ","")==fault_1o.replace(" ","")): #correct first order fault for this row
                found=True
                for k in range(0,len(unique_list)): #loop through columns
                    found2=False
                    if(k==i): # no self intersections
                        ff.write(',0')
                    else:
                        for f2o in range (0,len(faults_2o),3): #loop through second order faults for this row
                            if (faults_2o[f2o].replace(" ","")==unique_list[k].replace(" ","")):
                                ff.write(',1')
                                found2=True
                                break

                    if(not found2 and k!=i):
                        ff.write(',0') #this is not a second order fault for this row
            if(found):
                break
        if(not found): #this fault is not a first order fault relative to another fault
            for i in range (0,len(unique_list)):
                ff.write(',0')

        ff.write('\n')

    ff.close()
    print('fault-fault, fault-group and fault-unit relationship tables saved as:')
    print(output_path+'fault-fault-relationships.csv')
    print(output_path+'group-fault-relationships.csv')
    print(output_path+'unit-fault-relationships.csv')

def save_geol_wkt(sub_geol,geology_file_csv,ocode,gcode,mincode,maxcode,ccode,r1code,r2code,dscode,ucode):
    f= open(geology_file_csv,"w+")
    f.write('WKT\t'+ocode+'\t'+ucode+'\t'+gcode+'\t'+mincode+'\t'+maxcode+'\t'+ccode+'\t'+r1code+'\t'+r2code+'\t'+dscode+'\n')
    #display(sub_geol)        
    print(len(sub_geol)," polygons")
    #print(sub_geol)
    for i in range(0,len(sub_geol)):
        f.write("\""+str(sub_geol.loc[i].geometry)+"\"\t")
        f.write("\""+str(sub_geol.loc[i][ocode])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][ccode])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][gcode]).replace("None","")+"\"\t") #since map2model is looking for "" not "None"
        f.write("\""+str(sub_geol.loc[i][mincode])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][maxcode])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][ucode])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][r1code])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][r2code])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][dscode])+"\"\n")
    f.close()
        
def save_structure_wkt(sub_pts,structure_file_csv,gcode,dcode,ddcode,gicode):
    f= open(structure_file_csv,"w+")
    f.write('WKT\t'+gicode+'\t'+dcode+'\t'+ddcode+'\n')

    print(len(sub_pts)," points")


    #for i in range(0,len(sub_pts)):
    #    for j in range(0,len(sub_geol)):
    #        if(sub_pts.loc[i].geometry.within(sub_geol.loc[j].geometry)):
    #            print(i,j)

    for i in range(0,len(sub_pts)):
        line="\""+str(sub_pts.loc[i].geometry)+"\"\t\""+str(sub_pts.loc[i][gicode])+"\"\t\""+\
          str(sub_pts.loc[i][dcode])+"\"\t\""+str(sub_pts.loc[i][ddcode])+"\"\n"    
        f.write(functools.reduce(operator.add, (line)))
        
    f.close()
    
def save_faults_wkt(sub_lines,fault_file_csv,ocode,fcode):
    f= open(fault_file_csv,"w+")
    f.write('WKT\t'+ocode+'\t'+fcode+'\n')

    print(len(sub_lines)," polylines")

    for i in range(0,len(sub_lines)):
        if('Fault' in sub_lines.loc[i][fcode]):
            f.write("\""+str(sub_lines.loc[i].geometry)+"\"\t")
            f.write("\""+str(sub_lines.loc[i][ocode])+"\"\t")
            f.write("\""+str(sub_lines.loc[i][fcode])+"\"\n")
        
    f.close()

def save_Parfile(m2m_cpp_path,ocode,fcode,gicode,dcode,ddcode,ucode,gcode,mincode,maxcode,ccode,dscode,r1code,r2code,fold_label,sill_label,graph_path,geology_file_csv,fault_file_csv,structure_file_csv,minx,maxx,miny,maxy):
    f=open(m2m_cpp_path+'Parfile','w')
    f.write('--- COLUMN NAMES IN CSV DATA FILES: -------------------------------------------------------------\n')
    f.write('OBJECT COORDINATES              =WKT\n')
    f.write('FAULT: ID                       ='+ocode+'\n')
    f.write('FAULT: FEATURE                  ='+fcode+'\n')
    f.write('POINT: ID                       ='+gicode+'\n')
    f.write('POINT: DIP                      ='+dcode+'\n')
    f.write('POINT: DIP DIR                  ='+ddcode+'\n')
    f.write('POLYGON: ID                     ='+ocode+'\n')
    f.write('POLYGON: LEVEL1 NAME            ='+ucode+'\n')
    f.write('POLYGON: LEVEL2 NAME            ='+gcode+'\n')
    f.write('POLYGON: MIN AGE                ='+mincode+'\n')
    f.write('POLYGON: MAX AGE                ='+maxcode+'\n')
    f.write('POLYGON: CODE                   ='+ccode+'\n')
    f.write('POLYGON: DESCRIPTION            ='+dscode+'\n')
    f.write('POLYGON: ROCKTYPE1              ='+r1code+'\n')
    f.write('POLYGON: ROCKTYPE2              ='+r2code+'\n')
    f.write('--- SOME CONSTANTS: ----------------------------------------------------------------------------\n')
    f.write('FAULT AXIAL FEATURE NAME        ='+fold_label+'\n')
    f.write('SILL UNIT DESCRIPTION CONTAINS  ='+sill_label+'\n')
    f.write('IGNEOUS ROCKTYPE CONTAINS                           =igneous\n')
    f.write('VOLCANIC ROCKTYPE CONTAINS                          =volcanic\n')
    f.write('Intersect Contact With Fault: angle epsilon (deg)   =1.0\n')
    f.write('Intersect Contact With Fault: distance epsilon (m)  =15.0\n')
    f.write('------------------------------------------------------------------------------------------------\n')
    f.write('Path to the output data folder                      ='+graph_path+'\n')
    f.write('Path to geology data file                           ='+geology_file_csv+'\n')
    f.write('Path to faults data file                            ='+fault_file_csv+'\n')
    f.write('Path to points data file                            ='+structure_file_csv+'\n')
    f.write('------------------------------------------------------------------------------------------------\n')
    f.write('Clipping window X1 Y1 X2 Y2 (zeros for infinite)    ='+str(minx)+' '+str(miny)+' '+str(maxx)+' '+str(maxy)+'\n')
    f.write('Min length fraction for strat/fault graphs          =0.0\n')
    f.write('Graph edge width categories (three doubles)         =2000. 20000. 200000.\n')
    f.write('Graph edge direction (0-min age, 1-max age, 2-avg)  =2\n')
    f.write('Partial graph polygon ID                            =32\n')
    f.write('Partial graph depth                                 =4\n')
    f.write('Map subregion size dx, dy [m] (zeros for full map)  =0. 0.\n')
    f.write('------------------------------------------------------------------------------------------------\n')
    f.close()