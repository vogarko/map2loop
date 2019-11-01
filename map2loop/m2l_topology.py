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
        #f.write(str(len(nlist))+" ")
        #f.write(str(len(GD))+"\n")
        for m in range(len(nlist)): #process all sorted graphs
            f.write('Choice '+str(m))
            for n in range(0,len(GD)): #display nodes for one sorted graph
                print(nlist[m][n],G.nodes[nlist[m][n]]['LabelGraphics']['text'].replace(" ","_").replace("-","_"))
                f.write(","+G.nodes[nlist[m][n]]['LabelGraphics']['text'].replace(" ","_").replace("-","_"))
            if(m<len(nlist)-1):
                print("....")
            f.write('\n')
        f.close()



#save out a list of max/min/ave ages of all formations in a group
def abs_age_groups(geol,tmp_path,c_l):
    groups=[]
    info=[]
    ages=[]
    for a_poly in geol.iterrows(): #loop through all polygons
        if(str(a_poly[1][c_l['g']])=='None'):
            grp=a_poly[1][c_l['c']].replace(" ","_").replace("-","_")
        else:
            grp=a_poly[1][c_l['g']].replace(" ","_").replace("-","_")
        #print(grp)
        if(not grp in groups):
            groups+=[(grp)]

        info+=[(grp,a_poly[1][c_l['min']],a_poly[1][c_l['max']])]

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
    
def save_group(G,path_out,glabels,geol,c_l):
    Gp=nx.Graph().to_directed() #New Group graph
    
    geology_file=gpd.read_file(path_out+'geol_clip.shp')

    abs_age_groups(geol,path_out,c_l)
    geology_file.drop_duplicates(subset =c_l['c'],  inplace = True)
    

    geology_file.set_index(c_l['c'],  inplace = True)
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
            #print(geology_file.loc[glabel_0][c_l['g']])
            if(str(geology_file.loc[glabel_0][c_l['g']])=='None'):
                grp0=glabel_0.replace(" ","_").replace("-","_")
            else:
                grp0=geology_file.loc[glabel_0][c_l['g']].replace(" ","_").replace("-","_")
            if(str(geology_file.loc[glabel_1][c_l['g']])=='None'):
                grp1=glabel_1.replace(" ","_").replace("-","_")
            else:
                grp1=geology_file.loc[glabel_1][c_l['g']].replace(" ","_").replace("-","_")
                
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
    print("group choices:",len(glist))
    #display(glist)
    nx.write_gml(Gp, path_out+'groups.gml')
    #plt.show()
   
    f = open(path_out+'groups.csv', 'w')
    #f.write(str(len(glist))+" ")
    #f.write(str(len(glist[0]))+"\n")
    #print("xxxx",len(glist),len(glist[0]))
    for n in range(0,len(glist)):
        f.write('Choice '+str(n))
        for m in range(0,len(glist[0])):    
            f.write(','+str(glabels[glist[n][m]])) #check underscore
        f.write('\n')
    f.close()


    #g=open(path_out+'groups.csv',"r")
    #contents =g.readlines()
    #g.close
    #hdr=contents[0].split(" ")
    contents=np.genfromtxt(path_out+'groups.csv',delimiter=',',dtype='U25')
    
    #display('lencon',len(contents[0]))
    k=0
    ag=open(path_out+'/all_sorts.csv',"w")
    ag.write("index,group number,index in group,number in group,code,group\n")
    for i in range(1,len(contents[0])):
        ucontents=np.genfromtxt(path_out+"/"+contents[0][i].replace("\n","").replace(" ","_")+".csv",delimiter=',',dtype='U25')
        #f=open(path_out+"/"+contents[i].replace("\n","").replace(" ","_")+".csv","r")#check underscore
        #ucontents =f.readlines()
        #f.close
        #print(len(ucontents.shape),ucontents)
        if(len(ucontents.shape)==1):
            for j in range(1,len(ucontents)):
                ag.write(str(k)+","+str(i)+","+str(j)+","+str(len(ucontents)-1)+","+ucontents[j].replace("\n","")+","+contents[0][i].replace("\n","").replace(" ","_").replace("-","_")+"\n")
                k=k+1
        else:
            for j in range(1,len(ucontents[0])):
                ag.write(str(k)+","+str(i)+","+str(j)+","+str(len(ucontents[0])-1)+","+ucontents[0][j].replace("\n","")+","+contents[0][i].replace("\n","").replace(" ","_").replace("-","_")+"\n")
                k=k+1
            
    ag.close()

def parse_fault_relationships(graph_path,tmp_path,output_path):
    uf=open(graph_path+'unit-fault-intersection.txt','r')
    contents =uf.readlines()
    uf.close()
    
    all_long_faults=np.genfromtxt(output_path+'fault_dimensions.csv',delimiter=',',dtype='U25')
    n_faults=len(all_long_faults)
    #print(n_faults)
    all_faults={}
    unique_list = [] 
    #display(unique_list)
    for i in range(1,n_faults):
        f=all_long_faults[i][0]
        #print(all_long_faults[i][0])
        if f not in unique_list: 
            unique_list.append(f.replace("Fault_","")) 
    
    #display('Long Faults',unique_list)
    
    uf=open(output_path+'unit-fault-relationships.csv','w')
    uf.write('code,'+str(unique_list).replace("[","Fault_").replace(",",",Fault_").replace("'","").replace("]","").replace(" ","")+'\n')
    for row in contents:
        row=row.replace("\n","").split("{")
        unit=row[0].split(',')
        faults=row[1].replace("}","").replace(" ","").split(",")
        ostr=str(unit[1]).strip().replace(" ","_").replace("-","_")
        for ul in unique_list:
            out=[item for item in faults if ul in item]
            if(len(out)>0 ):
                ostr=ostr+",1"
            else:
                ostr=ostr+",0" 
        uf.write(ostr+"\n")
    uf.close()

    summary=pd.read_csv(tmp_path+'all_sorts_clean.csv')
    summary.set_index("code", inplace=True)
    #display('summary',summary)
    uf_rel=pd.read_csv(output_path+'unit-fault-relationships.csv')

    groups=summary.group.unique()
    ngroups=len(summary.group.unique())
    print(ngroups,'groups',groups,groups[0])
    uf_array=uf_rel.to_numpy()
    gf_array=np.zeros((ngroups,uf_array.shape[1]),dtype='U25')

    for i in range(0,ngroups):
        for j in range(0,len(uf_rel)):
            if(uf_rel.iloc[j][0] in summary.index.values):
                gsummary=summary.loc[uf_rel.iloc[j][0]]
                if(groups[i].replace("\n","")==gsummary['group']):
                    for k in range(1,len(uf_rel.iloc[j])):
                        if(uf_rel.iloc[j][k]==1):
                            gf_array[i-1,k]='1'
                        else:
                            continue
                else:
                    continue
            else:
                continue

    ug=open(output_path+'group-fault-relationships.csv','w')
    ug.write('group')
    for k in range(1,len(uf_rel.iloc[0])):
        ug.write(','+uf_rel.columns[k])
    ug.write("\n")
    for i in range(0,ngroups):
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
    #display(unique_list)
    unique_list_ff = [] 

    for row in contents:
        row=row.replace("\n","").split("{")
        fault_1o=row[0].split(',')
        fault_1o=fault_1o[1]
        
        faults_2o=row[1].replace("(","").replace(")","").replace("}","").split(",")

        if ((fault_1o.replace(" ","") not in unique_list_ff) and (fault_1o.replace(" ","") in unique_list)) : 
                unique_list_ff.append(fault_1o.replace(" ","")) 
        for i in range (0,len(faults_2o),3):
            if ((faults_2o[i].replace(" ","") not in unique_list_ff) and (faults_2o[i].replace(" ","") in unique_list)): 
                    unique_list_ff.append(faults_2o[i].replace(" ","")) 
    #display(unique_list) 

    G = nx.DiGraph()
    ff=open(output_path+'fault-fault-relationships.csv','w')
    ff.write('fault_id')
    for i in range (0,len(unique_list_ff)):
        ff.write(','+'Fault_'+unique_list_ff[i])
        G.add_node('Fault_'+unique_list_ff[i])
    ff.write('\n')

    for i in range(0,len(unique_list_ff)): #loop thorugh rows
        ff.write('Fault_'+unique_list_ff[i]) 
        found=False
        #for j in range(0,len(unique_list)):
        for row in contents: #loop thorugh known intersections
            row=row.replace("\n","").split("{")
            fault_1o=row[0].split(',')
            fault_1o=fault_1o[1]
            faults_2o=row[1].replace("(","").replace(")","").replace("}","").split(",")

            if(unique_list_ff[i].replace(" ","")==fault_1o.replace(" ","")): #correct first order fault for this row
                found=True
                for k in range(0,len(unique_list_ff)): #loop through columns
                    found2=False
                    if(k==i): # no self intersections
                        ff.write(',0')
                    else:
                        for f2o in range (0,len(faults_2o),3): #loop through second order faults for this row
                            if (faults_2o[f2o].replace(" ","")==unique_list_ff[k].replace(" ","")):
                                ff.write(',1')
                                G.add_edge('Fault_'+unique_list_ff[i], 'Fault_'+faults_2o[f2o].replace(" ",""))
                                found2=True
                                break

                    if(not found2 and k!=i):
                        ff.write(',0') #this is not a second order fault for this row
            if(found):
                break
        if(not found): #this fault is not a first order fault relative to another fault
            for i in range (0,len(unique_list_ff)):
                ff.write(',0')

        ff.write('\n')

    ff.close()
    
    nx.draw(G, with_labels=True, font_weight='bold')
    nx.write_gml(G, tmp_path+"fault_network.gml")  
    
    try:
        print(list(nx.simple_cycles(G)))
    except:
        print('no cycles')

def yyyparse_fault_relationships(graph_path,tmp_path,output_path):
    uf=open(graph_path+'unit-fault-intersection.txt','r')
    contents =uf.readlines()
    uf.close()
    
    all_long_faults=np.genfromtxt(output_path+'fault_dimensions.csv',delimiter=',',dtype='U25')
    n_faults=len(all_long_faults)
    #print(n_faults)
    all_faults={}
    unique_list = [] 
    #display(unique_list)
    for i in range(1,n_faults):
        f=all_long_faults[i][0]
        #print(all_long_faults[i][0])
        if f not in unique_list: 
            unique_list.append(f.replace("Fault_","")) 
    
    #display('Long Faults',unique_list)
    
    uf=open(output_path+'unit-fault-relationships.csv','w')
    uf.write('code,'+str(unique_list).replace("[","Fault_").replace(",",",Fault_").replace("'","").replace("]","").replace(" ","")+'\n')
    for row in contents:
        row=row.replace("\n","").split("{")
        unit=row[0].split(',')
        faults=row[1].replace("}","").replace(" ","").split(",")
        ostr=str(unit[1]).strip().replace(" ","_").replace("-","_")
        for ul in unique_list:
            out=[item for item in faults if ul in item]
            if(len(out)>0 ):
                ostr=ostr+",1"
            else:
                ostr=ostr+",0" 
        uf.write(ostr+"\n")
    uf.close()

    summary=pd.read_csv(tmp_path+'all_sorts_clean.csv')
    summary.set_index("code", inplace=True)
    #display('summary',summary)
    uf_rel=pd.read_csv(output_path+'unit-fault-relationships.csv')

    groups=summary.group.unique()
    ngroups=len(summary.group.unique())
    print(ngroups,'groups',groups,groups[0])
    uf_array=uf_rel.to_numpy()
    gf_array=np.zeros((ngroups,uf_array.shape[1]),dtype='U25')

    for i in range(0,ngroups):
        for j in range(0,len(uf_rel)):
            if(uf_rel.iloc[j][0] in summary.index.values):
                gsummary=summary.loc[uf_rel.iloc[j][0]]
                if(groups[i].replace("\n","")==gsummary['group']):
                    for k in range(1,len(uf_rel.iloc[j])):
                        if(uf_rel.iloc[j][k]==1):
                            gf_array[i-1,k]='1'
                        else:
                            continue
                else:
                    continue
            else:
                continue

    ug=open(output_path+'group-fault-relationships.csv','w')
    ug.write('group')
    for k in range(1,len(uf_rel.iloc[0])):
        ug.write(','+uf_rel.columns[k])
    ug.write("\n")
    for i in range(0,ngroups):
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

    unique_list_ff = [] 

    for row in contents:
        row=row.replace("\n","").split("{")
        fault_1o=row[0].split(',')
        fault_1o='Fault_'+fault_1o[1]
        
        faults_2o=row[1].replace("(","").replace(")","").replace("}","").split(",")

        if ((fault_1o.replace(" ","") not in unique_list_ff) and (fault_1o.replace(" ","") in unique_list)) : 
                unique_list_ff.append('Fault_'+fault_1o.replace(" ","")) 
        for i in range (0,len(faults_2o),3):
            if ((faults_2o[i].replace(" ","") not in unique_list_ff) and ('Fault_'+faults_2o[i].replace(" ","") in unique_list)): 
                    unique_list_ff.append('Fault_'+faults_2o[i].replace(" ","")) 
    #display(unique_list) 

    ff=open(output_path+'fault-fault-relationships.csv','w')
    ff.write('fault_id')
    for i in range (0,len(unique_list_ff)):
        ff.write(','+unique_list_ff[i])
    ff.write('\n')

    for i in range(0,len(unique_list_ff)): #loop thorugh rows
        ff.write(unique_list_ff[i]) 
        found=False
        #for j in range(0,len(unique_list)):
        for row in contents: #loop thorugh known intersections
            row=row.replace("\n","").split("{")
            fault_1o=row[0].split(',')
            fault_1o='Fault_'+fault_1o[1]
            faults_2o=row[1].replace("(","").replace(")","").replace("}","").split(",")

            if(unique_list_ff[i].replace(" ","")==fault_1o.replace(" ","")): #correct first order fault for this row
                found=True
                for k in range(0,len(unique_list_ff)): #loop through columns
                    found2=False
                    if(k==i): # no self intersections
                        ff.write(',0')
                    else:
                        for f2o in range (0,len(faults_2o),3): #loop through second order faults for this row
                            if ('Fault_'+faults_2o[f2o].replace(" ","")==unique_list_ff[k].replace(" ","")):
                                ff.write(',1')
                                found2=True
                                break

                    if(not found2 and k!=i):
                        ff.write(',0') #this is not a second order fault for this row
            if(found):
                break
        if(not found): #this fault is not a first order fault relative to another fault
            for i in range (0,len(unique_list_ff)):
                ff.write(',0')

        ff.write('\n')

    ff.close()

def save_geol_wkt(sub_geol,geology_file_csv,c_l):
    #print(sub_geol,geology_file_csv,ocode,gcode,mincode,maxcode,ccode,r1code,r2code,dscode,ucode)
    f= open(geology_file_csv,"w+")
    f.write('WKT\t'+c_l['o'].replace("\n","")+'\t'+c_l['u'].replace("\n","")+'\t'+c_l['g'].replace("\n","")+'\t'+c_l['min'].replace("\n","")+'\t'+c_l['max'].replace("\n","")+'\t'+c_l['c'].replace("\n","")+'\t'+c_l['r1'].replace("\n","")+'\t'+c_l['r2'].replace("\n","")+'\t'+c_l['ds'].replace("\n","")+'\n')
    #display(sub_geol)        
    print(len(sub_geol)," polygons")
    #print(sub_geol)
    for i in range(0,len(sub_geol)):
        #print('**',sub_geol.loc[i][[c_l['o']]],'++')
        f.write("\""+str(sub_geol.loc[i].geometry)+"\"\t")
        f.write("\""+str(sub_geol.loc[i][c_l['o']])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][c_l['c']])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][c_l['g']]).replace("None","")+"\"\t") #since map2model is looking for "" not "None"
        f.write("\""+str(sub_geol.loc[i][c_l['min']])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][c_l['max']])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][c_l['u']])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][c_l['r1']])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][c_l['r2']])+"\"\t")
        f.write("\""+str(sub_geol.loc[i][c_l['ds']])+"\"\n")
    f.close()
        
def save_structure_wkt(sub_pts,structure_file_csv,c_l):
    f= open(structure_file_csv,"w+")
    f.write('WKT\t'+c_l['gi']+'\t'+c_l['d']+'\t'+c_l['dd']+'\n')

    print(len(sub_pts)," points")


    #for i in range(0,len(sub_pts)):
    #    for j in range(0,len(sub_geol)):
    #        if(sub_pts.loc[i].geometry.within(sub_geol.loc[j].geometry)):
    #            print(i,j)

    for i in range(0,len(sub_pts)):
        line="\""+str(sub_pts.loc[i].geometry)+"\"\t\""+str(sub_pts.loc[i][c_l['gi']])+"\"\t\""+\
          str(sub_pts.loc[i][c_l['d']])+"\"\t\""+str(sub_pts.loc[i][c_l['dd']])+"\"\n"    
        f.write(functools.reduce(operator.add, (line)))
        
    f.close()
    
def save_faults_wkt(sub_lines,fault_file_csv,c_l):
    f= open(fault_file_csv,"w+")
    f.write('WKT\t'+c_l['o']+'\t'+c_l['f']+'\n')

    print(len(sub_lines)," polylines")

    for i in range(0,len(sub_lines)):
        if(c_l['fault'] in sub_lines.loc[i][c_l['f']]):
            f.write("\""+str(sub_lines.loc[i].geometry)+"\"\t")
            f.write("\""+str(sub_lines.loc[i][c_l['o']])+"\"\t")
            f.write("\""+str(sub_lines.loc[i][c_l['f']])+"\"\n")
        
    f.close()

def save_Parfile(m2m_cpp_path,c_l,graph_path,geology_file_csv,fault_file_csv,structure_file_csv,minx,maxx,miny,maxy):
    f=open(m2m_cpp_path+'Parfile','w')
    f.write('--- COLUMN NAMES IN CSV DATA FILES: -------------------------------------------------------------\n')
    f.write('OBJECT COORDINATES              =WKT\n')
    f.write('FAULT: ID                       ='+c_l['o']+'\n')
    f.write('FAULT: FEATURE                  ='+c_l['f']+'\n')
    f.write('POINT: ID                       ='+c_l['gi']+'\n')
    f.write('POINT: DIP                      ='+c_l['d']+'\n')
    f.write('POINT: DIP DIR                  ='+c_l['dd']+'\n')
    f.write('POLYGON: ID                     ='+c_l['o']+'\n')
    f.write('POLYGON: LEVEL1 NAME            ='+c_l['u']+'\n')
    f.write('POLYGON: LEVEL2 NAME            ='+c_l['g']+'\n')
    f.write('POLYGON: MIN AGE                ='+c_l['min']+'\n')
    f.write('POLYGON: MAX AGE                ='+c_l['max']+'\n')
    f.write('POLYGON: CODE                   ='+c_l['c']+'\n')
    f.write('POLYGON: DESCRIPTION            ='+c_l['ds']+'\n')
    f.write('POLYGON: ROCKTYPE1              ='+c_l['r1']+'\n')
    f.write('POLYGON: ROCKTYPE2              ='+c_l['r2']+'\n')
    f.write('--- SOME CONSTANTS: ----------------------------------------------------------------------------\n')
    f.write('FAULT AXIAL FEATURE NAME        ='+c_l['fold']+'\n')
    f.write('SILL UNIT DESCRIPTION CONTAINS  ='+c_l['sill']+'\n')
    f.write('IGNEOUS ROCKTYPE CONTAINS                           ='+c_l['intrusive']+'\n')
    f.write('VOLCANIC ROCKTYPE CONTAINS                          ='+c_l['volcanic']+'\n')
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