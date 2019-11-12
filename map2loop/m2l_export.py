from map2loop import m2l_topology
import networkx as nx
import random
import numpy as np
import pandas as pd
import os

def loop2geomodeller(test_data_path,tmp_path,output_path,save_faults):
    f=open(test_data_path+'m2l.taskfile','w')
    f.write('#---------------------------------------------------------------\n')
    f.write('#-----------------------Project Header-----------------------\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('name: "UWA_Intrepid"\n')
    f.write('description: "Automate_batch_Model"\n')
    f.write('    GeomodellerTask {\n')
    f.write('    CreateProject {\n')
    f.write('        name: "Hamersley"\n')
    f.write('        author: "Des/Mark"\n')
    f.write('        date: "23/10/2019  0: 0: 0"\n')
    f.write('        projection { map_projection: "GDA94 / MGA50"}\n')
    f.write('        version: "2.0"\n')
    f.write('        units: meters\n')
    f.write('        precision: 1.0\n')
    f.write('        Extents {\n')
    f.write('            xmin: 500000\n')
    f.write('            ymin: 7455500\n')
    f.write('            zmin: -3000\n')
    f.write('            xmax: 603000\n')
    f.write('            ymax: 7568000\n')
    f.write('            zmax: 1000\n')
    f.write('        }\n')
    f.write('        deflection2d: 0.001\n')
    f.write('        deflection3d: 0.001\n')
    f.write('        discretisation: 10.0\n')
    f.write('        referenceTop: false\n')
    f.write('        CustomDTM {\n')
    f.write('            Extents {\n')
    f.write('                xmin: 500000\n')
    f.write('                ymin: 7455500\n')
    f.write('                xmax: 603000\n')
    f.write('                ymax: 7568000\n')
    f.write('            }\n')
    f.write('            name: "Topography"\n')
    f.write('            filename {\n')
    f.write('                Grid_Name: "./dtm/hammersley_sheet_dtm.ers"\n')
    f.write('            }\n')
    f.write('            nx: 10\n')
    f.write('            ny: 10\n')
    f.write('        }\n')
    f.write('    }\n')
    f.write('}\n')


    orientations=pd.read_csv(output_path+'orientations_clean.csv',',')
    contacts=pd.read_csv(output_path+'contacts_clean.csv',',')
    all_sorts=pd.read_csv(tmp_path+'all_sorts_clean.csv',',')

    empty_fm=[]

    for indx,afm in all_sorts.iterrows():
        foundcontact=False
        for indx2,acontact in contacts.iterrows():
            if(acontact['formation'] in afm['code']):
                foundcontact=True
                break
        foundorientation=False
        for indx3,ano in orientations.iterrows():
            if(ano['formation'] in afm['code']):
                foundorientation=True
                break
        if(not foundcontact or not foundorientation):
            empty_fm.append(afm['code'])

    #print(empty_fm)

    all_sorts=np.genfromtxt(tmp_path+'all_sorts_clean.csv',delimiter=',',dtype='U25')
    nformations=len(all_sorts)

    f.write('#---------------------------------------------------------------\n')
    f.write('#-----------------------Create Formations-----------------------\n')
    f.write('#---------------------------------------------------------------\n')

    for i in range (1,nformations):
        if( not all_sorts[i,4] in empty_fm):
            f.write('GeomodellerTask {\n')
            f.write('CreateFormation {\n')

            ostr='    name: "'+all_sorts[i,4].replace("\n","")+'"\n'
            f.write(ostr)

            ostr='    red: '+str(random.randint(1,256)-1)+'\n'
            f.write(ostr)

            ostr='    green: '+str(random.randint(1,256)-1)+'\n'
            f.write(ostr)

            ostr='    blue: '+str(random.randint(1,256)-1)+'\n'
            f.write(ostr)

            f.write('    }\n')
            f.write('}\n')

    f.write('#---------------------------------------------------------------\n')
    f.write('#-----------------------Set Stratigraphic Pile------------------\n')
    f.write('#---------------------------------------------------------------\n')


    for i in range (1,nformations):
    #for i in range (nformations-1,0,-1):
        if(all_sorts[i,2]==str(1)):
            f.write('GeomodellerTask {\n')
            f.write('SetSeries {\n')

            ostr='    name: "'+all_sorts[i][5].replace("\n","")+'"\n'
            f.write(ostr)

            ostr='    position: 1\n'
            f.write(ostr)

            ostr='    relation: "erode"\n'
            f.write(ostr)

            f.write('    }\n')
            f.write('}\n')

            for j in range(nformations-1,0,-1):
    #        for j in range(1,nformations):
                if(all_sorts[j,1]==all_sorts[i,1]):
                    if( not all_sorts[j][4] in empty_fm):
                        f.write('GeomodellerTask {\n')
                        f.write('AddFormationToSeries {\n')

                        ostr='    series: "'+all_sorts[j][5]+'"\n'
                        f.write(ostr)

                        ostr='    formation: "'+all_sorts[j][4]+'"\n'
                        f.write(ostr)

                        f.write('    }\n')
                        f.write('}\n')    

    if(save_faults):
        output_path='../test_data3/output/'

        faults_len=pd.read_csv(output_path+'fault_dimensions.csv')

        n_allfaults=len(faults_len)

        fcount=0
        for i in range(0,n_allfaults):
            f.write('GeomodellerTask {\n')
            f.write('CreateFault {\n')
            ostr='    name: "'+faults_len.iloc[i]["Fault"]+'"\n'
            f.write(ostr)

            ostr='    red: '+str(random.randint(1,256)-1)+'\n'
            f.write(ostr)

            ostr='    green: '+str(random.randint(1,256)-1)+'\n'
            f.write(ostr)

            ostr='    blue: '+str(random.randint(1,256)-1)+'\n'
            f.write(ostr)

            f.write('    }\n')
            f.write('}\n')
            fcount=fcount+1
            
            f.write('GeomodellerTask {\n')
            f.write('    Set3dFaultLimits {\n')
            f.write('        Fault_name: "'+faults_len.iloc[i]["Fault"]+ '"\n')
            f.write('        Horizontal: '+str(faults_len.iloc[i]["HorizontalRadius"])+ '\n')
            f.write('        Vertical: '+str(faults_len.iloc[i]["VerticalRadius"])+ '\n')
            f.write('        InfluenceDistance: '+str(faults_len.iloc[i]["InfluenceDistance"])+ '\n')
            f.write('    }\n')
            f.write('}\n')
            

    f.write('#---------------------------------------------------------------\n')
    f.write('#-----------------------Import 3D contact data ---Base Model----\n')
    f.write('#---------------------------------------------------------------\n')

    contacts=pd.read_csv(output_path+'contacts_clean.csv',',')
    all_sorts=pd.read_csv(tmp_path+'all_sorts_clean.csv',',')
    #all_sorts.set_index('code',  inplace = True)
    #display(all_sorts)

    for inx,afm in all_sorts.iterrows():
        #print(afm[0])
        if( not afm['code'] in empty_fm):
            f.write('GeomodellerTask {\n')
            f.write('    Add3DInterfacesToFormation {\n')
            f.write('          formation: "'+str(afm['code'])+'"\n')

            for indx2,acontact in contacts.iterrows():
                if(acontact['formation'] in afm['code'] ):
                    ostr='              point {x:'+str(acontact['X'])+'; y:'+str(acontact['Y'])+'; z:'+str(acontact['Z'])+'}\n'
                    f.write(ostr)
            f.write('    }\n')
            f.write('}\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('#------------------Import 3D orientation data ---Base Model-----\n')
    f.write('#---------------------------------------------------------------\n')

    orientations=pd.read_csv(output_path+'orientations_clean.csv',',')
    all_sorts=pd.read_csv(tmp_path+'all_sorts_clean.csv',',')
    #all_sorts.set_index('code',  inplace = True)
    #display(all_sorts)

    for inx,afm in all_sorts.iterrows():
        #print(groups[agp])
        if( not afm['code'] in empty_fm):
            f.write('GeomodellerTask {\n')
            f.write('    Add3DFoliationToFormation {\n')
            f.write('          formation: "'+str(afm['code'])+'"\n')
            for indx2,ano in orientations.iterrows():
                if(ano['formation'] in afm['code']):
                    f.write('           foliation {\n')
                    ostr='                  Point3D {x:'+str(ano['X'])+'; y:'+str(ano['Y'])+'; z:'+str(ano['Z'])+'}\n'
                    f.write(ostr)
                    ostr='                  direction: '+str(ano['azimuth'])+'\n'
                    f.write(ostr)
                    ostr='                  dip: '+str(ano['dip'])+'\n'
                    f.write(ostr)
                    if(ano['polarity']==1):
                        ostr='                  polarity: Normal_Polarity\n'
                    else:
                        ostr='                  polarity: Reverse_Polarity\n'
                    f.write(ostr)            
                    ostr='           }\n'
                    f.write(ostr)
            f.write('    }\n')
            f.write('}\n')

    f.write('#---------------------------------------------------------------\n')
    f.write('#-----------------------Import 3D fault data ---Base Model------\n')
    f.write('#---------------------------------------------------------------\n')

    contacts=pd.read_csv(output_path+'faults.csv',',')
    faults=pd.read_csv(output_path+'fault_dimensions.csv',',')

    for indx,afault in faults.iterrows():
        f.write('GeomodellerTask {\n')
        f.write('    Add3DInterfacesToFormation {\n')
        f.write('          formation: "'+str(afault['Fault'])+'"\n')
        for indx2,acontact in contacts.iterrows():
            if(acontact['formation'] in afault['Fault']):
                ostr='              point {x:'+str(acontact['X'])+'; y:'+str(acontact['Y'])+'; z:'+str(acontact['Z'])+'}\n'
                f.write(ostr)
        f.write('    }\n')
        f.write('}\n')

    f.write('#---------------------------------------------------------------\n')
    f.write('#------------------Import 3D fault orientation data ------------\n')
    f.write('#---------------------------------------------------------------\n')

    orientations=pd.read_csv(output_path+'fault_orientations.csv',',')
    faults=pd.read_csv(output_path+'fault_dimensions.csv',',')

    for indx,afault in faults.iterrows():
        f.write('GeomodellerTask {\n')
        f.write('    Add3DFoliationToFormation {\n')
        f.write('          formation: "'+str(afault['Fault'])+'"\n')
        for indx2,ano in orientations.iterrows():
            if(ano['formation'] in afault['Fault']):
                f.write('           foliation {\n')
                ostr='                  Point3D {x:'+str(ano['X'])+'; y:'+str(ano['Y'])+'; z:'+str(ano['Z'])+'}\n'
                f.write(ostr)
                ostr='                  direction: '+str(ano['DipDirection'])+'\n'
                f.write(ostr)
                ostr='                  dip: '+str(ano['dip'])+'\n'
                f.write(ostr)
                if(ano['DipPolarity']==1):
                    ostr='                  polarity: Normal_Polarity\n'
                else:
                    ostr='                  polarity: Reverse_Polarity\n'
                f.write(ostr)            
                ostr='           }\n'
                f.write(ostr)
        f.write('    }\n')
        f.write('}\n')

    if(save_faults):
        G=nx.read_gml(tmp_path+"fault_network.gml",label='label')
        #nx.draw(G, with_labels=True, font_weight='bold')
        edges=list(G.edges)
        #for i in range(0,len(edges)):
            #print(edges[i][0],edges[i][1])
        cycles=list(nx.simple_cycles(G))
        #display(cycles)
        f.write('#---------------------------------------------------------------\n')
        f.write('#-----------------------Link faults with faults ----------------\n')
        f.write('#---------------------------------------------------------------\n')
        f.write('GeomodellerTask {\n')
        f.write('    LinkFaultsWithFaults {\n')

        for i in range(0,len(edges)):
                found=False
                for j in range(0,len(cycles)):
                    if(edges[i][0]== cycles[j][0] and edges[i][1]== cycles[j][1]):
                        found=True # fault pair is first two elements in a cycle list so don't save to taskfile
                if(not found):
                    ostr='        FaultStopsOnFaults{ fault: "'+edges[i][1]+'"; stopson: "'+edges[i][0]+'"}\n'
                    f.write(ostr)

        f.write('    }\n')
        f.write('}\n')

    if(save_faults):
        all_fault_group=np.genfromtxt(output_path+'group-fault-relationships.csv',delimiter=',',dtype='U25')
        ngroups=len(all_fault_group)
        all_fault_group=np.transpose(all_fault_group)
        nfaults=len(all_fault_group)

        f.write('#---------------------------------------------------------------\n')
        f.write('#-----------------------Link series with faults ----------------\n')
        f.write('#---------------------------------------------------------------\n')
        f.write('GeomodellerTask {\n')
        f.write('    LinkFaultsWithSeries {\n')

        for i in range(1,nfaults):
            first=True
            for j in range(1,ngroups):
                if(all_fault_group[i,j]==str(1)):
                    if(first):
                        ostr='    FaultSeriesLinks{ fault: "'+all_fault_group[i,0]+'"; series: ['
                        f.write(ostr)
                        ostr='"'+all_fault_group[0,j]+'"'
                        f.write(ostr)
                        first=False
                    else:
                        ostr=', "'+all_fault_group[0,j]+'"'
                        f.write(ostr)
            if(not first):
                ostr=']}\n'
                f.write(ostr)

        f.write('    }\n')
        f.write('}\n')
    

    f.write('GeomodellerTask {\n')
    f.write('    SaveProjectAs {\n')
    f.write('        filename: "./Models_Prelim/Models_UWA.xml"\n')
    f.write('    }\n')
    f.write('}\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('#----------------------------Compute Model----------------------\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('\n')
    f.write('GeomodellerTask {\n')
    f.write('    ComputeModel {\n')
    f.write('        SeriesList {\n')
    f.write('            node: "All"\n')
    f.write('        }\n')
    f.write('        SectionList {\n')
    f.write('            node: "All"\n')
    f.write('        }\n')
    f.write('        Extents {\n')
    f.write('            xmin: 500000\n')
    f.write('            ymin: 7455500\n')
    f.write('            zmin: -3000\n')
    f.write('            xmax: 603000\n')
    f.write('            ymax: 7568000\n')
    f.write('            zmax: 1000\n')
    f.write('        }\n')
    f.write('        radius: 10.0\n')
    f.write('    }\n')
    f.write('}\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('#-----------------------Add geophysical Properties--------------\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('\n')
    f.write('\n')
    f.write('\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('#--------------------------Export Lithology Voxet---------------\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('GeomodellerTask {\n')
    f.write('    SaveLithologyVoxet {\n')
    f.write('        nx: 100\n')
    f.write('        ny: 100\n')
    f.write('        nz: 400\n')
    f.write('        LithologyVoxetFileStub: "./Litho_Voxet/LithoVoxet.vo"\n')
    f.write('    }\n')
    f.write('}\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('#--------------------------Save As Model------------------------\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('\n')
    f.write('GeomodellerTask {\n')
    f.write('    SaveProjectAs {\n')
    f.write('        filename: "./Models_Final/Models_UWA.xml"\n')
    f.write('    }\n')
    f.write('}\n')

    f.close()
