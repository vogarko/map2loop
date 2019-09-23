import networkx as nx
import matplotlib.pyplot as plt

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

def save_group(G,mname,path_out,glabels):
    Gp=nx.Graph().to_directed() #New Group graph

    nlist=list(G.nodes)
    for n in nlist: # Find out total number of groups and their names groups
        if('isGroup' in G.nodes[n]):
            G.add_nodes_from([n])

    for e in G.edges:
        if(G.nodes[e[0]]['gid']!=G.nodes[e[1]]['gid']):
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
    print(glist)
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
    ag.write("index,group number,index in group, number in group,code,group\n")
    for i in range(1,int(hdr[1])+1):
        f=open(path_out+"/"+contents[i].replace("\n","")+".csv","r")#check underscore
        ucontents =f.readlines()
        f.close
        uhdr=ucontents[0].split(" ")
        for j in range(1,int(uhdr[1])+1):
            print(ucontents[j].replace("\n",""))
            ag.write(str(k)+","+str(i)+","+str(j)+","+uhdr[1].replace("\n","")+","+ucontents[j].replace("\n","")+","+contents[i].replace("\n","").replace(" ","_").replace("-","_")+"\n")
            k=k+1
    ag.close()