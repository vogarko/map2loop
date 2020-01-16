from map2loop import m2l_topology
import networkx as nx
import random
import numpy as np
import pandas as pd
import os
from LoopStructural import GeologicalModel
from LoopStructural.visualisation import LavaVuModelViewer
from scipy.interpolate import Rbf
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import lavavu
from pyamg import solve
import gempy as gp
from gempy import plot

##########################################################################
# Save out and compile taskfile needed to generate geomodeller model using the geomodellerbatch engine
#
# loop2geomodeller(test_data_path,tmp_path,output_path,save_faults,compute_etc)
# Args:
# test_data_path root directory of test data
# tmp_path directory of temporary outputs
# output_path directory of outputs
# ave_faults flag for saving faults or not
# compute_etc flag for actual calculations or just project output
#
# Creates geomodeller taskfile files from varous map2loop outputs
##########################################################################
def loop2geomodeller(test_data_path,tmp_path,output_path,dtm_file,bbox,save_faults,compute_etc):
    f=open(test_data_path+'m2l.taskfile','w')
    f.write('#---------------------------------------------------------------\n')
    f.write('#-----------------------Project Header-----------------------\n')
    f.write('#---------------------------------------------------------------\n')
    f.write('name: "UWA_Intrepid"\n')
    f.write('description: "Automate_batch_Model"\n')
    f.write('    GeomodellerTask {\n')
    f.write('    CreateProject {\n')
    f.write('        name: "Hamersley"\n')
    f.write('        author: "Mark"\n')
    f.write('        date: "23/10/2019  0: 0: 0"\n')
    f.write('        projection { map_projection: "GDA94 / MGA50"}\n')
    f.write('        version: "2.0"\n')
    f.write('        units: meters\n')
    f.write('        precision: 1.0\n')
    f.write('        Extents {\n')
    f.write('            xmin: '+str(bbox[0])+'\n')
    f.write('            ymin: '+str(bbox[1])+'\n')
    f.write('            zmin: -3000\n')
    f.write('            xmax: '+str(bbox[2])+'\n')
    f.write('            ymax: '+str(bbox[3])+'\n')
    f.write('            zmax: 1200\n')
    f.write('        }\n')
    f.write('        deflection2d: 0.001\n')
    f.write('        deflection3d: 0.001\n')
    f.write('        discretisation: 10.0\n')
    f.write('        referenceTop: false\n')
    f.write('        CustomDTM {\n')
    f.write('            Extents {\n')
    f.write('            xmin: '+str(bbox[0])+'\n')
    f.write('            ymin: '+str(bbox[1])+'\n')
    f.write('            xmax: '+str(bbox[2])+'\n')
    f.write('            ymax: '+str(bbox[3])+'\n')
    f.write('            }\n')
    f.write('            name: "Topography"\n')
    f.write('            filename {\n')
    f.write('                Grid_Name: "'+dtm_file+'"\n')
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
                if(ano['dip'] == -999):
                    ostr='                  dip: '+str(random.randint(60,90))+'\n'
                else:    
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
    f.close()
    

    if(compute_etc):
        f=open(test_data_path+'m2l_compute.taskfile','w')
        f.write('#---------------------------------------------------------------\n')
        f.write('#----------------------------Load Model----------------------\n')
        f.write('#---------------------------------------------------------------\n')
        f.write('GeomodellerTask {\n')
        f.write('    OpenProjectNoGUI {\n')
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
        f.write('            node: "All" \n')
        f.write('        }\n')
        f.write('        SectionList {\n')
        f.write('            node: "All"\n')
        f.write('        }\n')
        f.write('        FaultList {\n')
        f.write('            node: "All"\n')
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
        f.write('        nx: 25\n')
        f.write('        ny: 25\n')
        f.write('        nz: 40\n')
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
        f.write('GeomodellerTask {\n')
        f.write('    CloseProjectNoGUI {\n')
        f.write('    }\n')

        f.close()



def solve_pyamg(A,B):
    return solve(A,B,verb=False,tol=1e-8)

##########################################################################
# Import outputs from map2loop to LoopStructural and view with Lavavu
#
# loop2LoopStructural(thickness_file,orientation_file,contacts_file,bbox)
# Args:
# thickness_file path of fornation thickness file
# orientation_file path of orientations file
# contacts_file path of contacts file
# bbox model bounding box
#
# Calculates model and displays in LavaVu wthin notebook
##########################################################################
def loop2LoopStructural(thickness_file,orientation_file,contacts_file,bbox):
    df = pd.read_csv(thickness_file)
    thickness = {}
    for f in df['formation'].unique():
        thickness[f] = np.mean(df[df['formation']==f]['thickness'])

    #display(thickness)
    order = ['P__TKa_xs_k','P__TKo_stq','P__TKk_sf','P__TK_s',
    'A_HAu_xsl_ci', 'A_HAd_kd', 'A_HAm_cib', 'A_FOj_xs_b',
    'A_FO_xo_a', 'A_FO_od', 'A_FOu_bbo',
    'A_FOp_bs', 'A_FOo_bbo', 'A_FOh_xs_f', 'A_FOr_b']
    
    strat_val = {}
    val = 0
    for o in order:
        if o in thickness:
            strat_val[o] = val
            val+=thickness[o]

    #display(strat_val)    
    
    orientations = pd.read_csv(orientation_file)
    contacts = pd.read_csv(contacts_file) 
    
    contacts['val'] = np.nan 

    for o in strat_val:
        contacts.loc[contacts['formation']==o,'val'] = strat_val[o]
    data = pd.concat([orientations,contacts],sort=False)
    data['type'] = np.nan
    for o in order:
        data.loc[data['formation']==o,'type'] = 's0'
    data     
    
    boundary_points = np.zeros((2,3))
    boundary_points[0,0] = bbox[0] 
    boundary_points[0,1] = bbox[1] 
    boundary_points[0,2] = -20000 
    boundary_points[1,0] = bbox[2] 
    boundary_points[1,1] = bbox[3] 
    boundary_points[1,2] = 1200
    
    model = GeologicalModel(boundary_points[0,:],boundary_points[1,:])
    model.set_model_data(data)
    strati = model.create_and_add_foliation('s0', #identifier in data frame
                                                        interpolatortype="FDI", #which interpolator to use
                                                        nelements=400000, # how many tetras/voxels
                                                        buffer=0.1, # how much to extend nterpolation around box
                                                        solver='external',
                                                        external=solve_pyamg
                                                       )   
    viewer = LavaVuModelViewer()
    viewer.add_data(strati['feature'])
    viewer.add_isosurface(strati['feature'],
    #                       nslices=10,
                          slices= strat_val.values(),
    #                     voxet={'bounding_box':boundary_points,'nsteps':(100,100,50)},
                          paint_with=strati['feature'],
                          cmap='tab20'

                         )
    viewer.add_scalar_field(model.bounding_box,(100,100,100),
                              'scalar',
    #                             norm=True,
                             paint_with=strati['feature'],
                             cmap='tab20')
    viewer.set_viewer_rotation([-53.8190803527832, -17.1993350982666, -2.1576387882232666])
    #viewer.save("fdi_surfaces.png")
    viewer.interactive()
    
    
##########################################################################
# Import outputs from map2loop to gempy and view with pyvtk
# loop2gempy(test_data_name,tmp_path,vtk_pth,orientations_file,contacts_file,groups_file,dtm_reproj_file,bbox,model_base, model_top,vtk)
# Args:
# test_data_name root name of project
# tmp_path path of temp files directory
# vtk_pth path of vtk output directory
# orientations_file path of orientations file
# contacts_file path of contacts file
# groups_file path of groups file
# dtm_reproj_file path of dtm file
# bbox model bounding box
# model_base z value ofbase of model 
# model_top z value of top of model
# vtk flag as to wether to save out model to vtk
#
# Calculates model and displays in external vtk viewer
##########################################################################
def loop2gempy(test_data_name,tmp_path,vtk_pth,orientations_file,contacts_file,groups_file,dtm_reproj_file,bbox,model_base, model_top,vtk):
    geo_model = gp.create_model(test_data_name) 

    gp.init_data(geo_model, extent=[bbox[0], bbox[2], bbox[1], bbox[3], model_base, model_top],
        resolution = (50,50,50), 
          path_o = orientations_file,
          path_i = contacts_file, default_values=True); 
    
    # Show example lithological points    
    #gp.get_data(geo_model, 'surface_points').head() 
    
    # Show example orientations
    #gp.get_data(geo_model, 'orientations').head()
    
    # Plot some of this data
    #gp.plot.plot_data(geo_model, direction='z')
    
    # Load reprojected topgraphy to model
    
    fp = dtm_reproj_file
    #print(fp)
    geo_model.set_topography(source='gdal',filepath=fp)



    contents=np.genfromtxt(groups_file,delimiter=',',dtype='U25')
    ngroups=len(contents)

    faults = gp.Faults()
    series = gp.Series(faults)
    #series.df

    #display(ngroups,contents)
    groups=[]

    for i in range (0,ngroups):
        groups.append(contents[i].replace("\n",""))
        series.add_series(contents[i].replace("\n",""))
        print(contents[i].replace("\n",""))

    series.delete_series('Default series')

    #series
 
    # Load surfaces and assign to series
    surfaces = gp.Surfaces(series)

    print(ngroups,groups)
    for i in range(0,ngroups):
        contents=np.genfromtxt(tmp_path+groups[i]+'.csv',delimiter=',',dtype='U25')
        nformations=len(contents.shape)

        if(nformations==1):
            for j in range (1,len(contents)):
                surfaces.add_surface(str(contents[j]).replace("\n",""))
                d={groups[i]:str(contents[j]).replace("\n","")}
                surfaces.map_series({groups[i]:(str(contents[j]).replace("\n",""))}) #working but no gps       
        else:
            #print('lc',len(contents[0]))
            for j in range (1,len(contents[0])):
                surfaces.add_surface(str(contents[0][j]).replace("\n",""))
                d={groups[i]:str(contents[0][j]).replace("\n","")}
                surfaces.map_series({groups[i]:(str(contents[0][j]).replace("\n",""))}) #working but no gps


    #surfaces
    
    # Set Interpolation Data
    id_only_one_bool = geo_model.surface_points.df['id'].value_counts() == 1
    id_only_one = id_only_one_bool.index[id_only_one_bool]
    single_vals = geo_model.surface_points.df[geo_model.surface_points.df['id'].isin(id_only_one)]
    for idx, vals in single_vals.iterrows():
        geo_model.add_surface_points(vals['X'], vals['Y'], vals['Z'], vals['surface'])

    geo_model.update_structure() 
    
    gp.set_interpolation_data(geo_model,
                              compile_theano=True,
                              theano_optimizer='fast_compile',
                              verbose=[])   
    
    # Provide summary data on model
    
    #geo_model.additional_data.structure_data   
    
    #Calculate Model
    gp.compute_model(geo_model)
    
    # Extract surfaces to visualize in 3D renderers
    #gp.plot.plot_section(geo_model, 49, direction='z', show_data=False)
    
    ver , sim = gp.get_surfaces(geo_model)    
    
    import winsound
    duration = 700  # milliseconds
    freq = 1100  # Hz
    winsound.Beep(freq, duration)
    winsound.Beep(freq, duration)
    winsound.Beep(freq, duration)    
    
    #Visualise Model
    gp.plot.plot_3D(geo_model, render_data=False)
    
    #Save model as vtk
    if(vtk):
        gp.plot.export_to_vtk(geo_model, path=vtk_path, name=test_data_name+'.vtk', voxels=False, block=None, surfaces=True)    