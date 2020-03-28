import sys, os
from map2loop import m2l_export
import gempy as gp

input_data_dir = os.path.dirname(__file__) + '/../'


def test_loop2gempy():

    test_data_name = 'test_data3'
    output_path = input_data_dir + '../test_data3/output/'
    test_data_path = input_data_dir + '../' + test_data_name + '/'

    bbox = (500057, 7455348, 603028, 7567953)
    model_top = 1200
    model_base = -2000

    tmp_path = test_data_path + 'tmp/'
    vtk_path = test_data_path + 'vtk/'
    dtm_path = test_data_path + 'dtm/'
    dtm_reproj_file = dtm_path + 'dtm_rp.tif'

    geo_model = m2l_export.loop2gempy_pro(test_data_name, tmp_path, vtk_path, output_path + 'orientations_clean.csv',
                                          output_path + 'contacts_clean.csv', tmp_path + 'groups_clean.csv',
                                          bbox, model_base, model_top, vtk=False, dtm_reproj_file=dtm_reproj_file,
                                          verbose=False)
