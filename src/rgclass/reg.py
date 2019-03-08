
from django.conf import settings

from .models import Signal_db
# from .function import createPeakToBedFile, calculateJaccardPval, calculateJaccardFC, getPrecomputedJaccardValuePerFile
# from .function import calculatePearsonCor


import os
import math
import pandas as pd
import re


def reg_mats(fname, user_uploaded_filename, matrix_size, region, user_path):
    # reg_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
    # reg_dist_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]

    rpkm = pd.DataFrame()
    # Go through each signal files and combine all RPKM into a 2d matrix_size
    chr_index = 0
    rpkm_index = 4
    for i in range(len(fname)):
        # If the name is from the database
        name = fname[i]
        # cur = pd.DataFrame(columns = ['chromosome', name])
        if name not in user_uploaded_filename:
            f_path = os.path.join(settings.MEDIA_ROOT, 'signal_file_db', region)

            curFile = pd.read_csv(f_path+'/'+region+'_'+name, sep = "\t", header = None)
            # column name is rpkm value
            curFile.columns = ['chromosome', 'start', 'end', 'count', name]
            cur = curFile[['chromosome', name]]
            # data = pd.read_csv('output_list.txt', sep=" ", header=None)
            # data.columns = ["a", "b", "c", "etc."]

            # with open (f_path+'/'+region+'_'+name, 'r') as f:
            #     curFile = f.readlines()
            #
            # # We assume that the format is as follows:
            # # chr start end count rpkm
            # for row in range(len(curFile)):
            #     tmp = re.split(r'\s+', curFile[row].strip())
            #     cur.loc[row] = [tmp[chr_index], tmp[rpkm_index]]

            cur = cur.sort_values(by='chromosome', ascending = True)
            rpkm = pd.concat([rpkm, cur[name]], axis = 1)

    # Calculate pearson correlation (distance matrix).
    cor_matrix = 1 - rpkm.corr(method = "pearson")



        # else: # file which user uploaded


    # for i in range(matrix_size):
    #     file_one_user_uploaded = True
    #     # if fname[i] not in user_uploaded_filename:
    #     #     full_filename_i = Peaks_db.objects.get(fileID=fname[i])
    #     #     full_filename_i = full_filename_i.origFile + '_' + reg + '_' + str(cutoff)
    #     #     f1 = Peaks_db_file.objects.filter(filename=full_filename_i).values('path')
    #     #     f1 = os.path.join(f1[0]['path'], full_filename_i)
    #     #     file_one_user_uploaded = False
    #     # else:
    #     ######################################################
    #     full_filename_i = region + '_' + fname[i]
    #
    #     f1 = os.path.join(user_path, full_filename_i)
    #     #####################################################3
    #     # if not file_one_user_uploaded:
    #     #     jaccard_indices = getPrecomputedJaccardValuePerFile(full_filename_i)
    #
    #     for j in range(matrix_size):
    #         file_two_user_uploaded = True
    #         # if fname[j] not in user_uploaded_filename:
    #         #     full_filename_j = Peaks_db.objects.get(fileID=fname[j])
    #         #     full_filename_j = full_filename_j.origFile + '_' + reg + '_' + str(cutoff)
    #         #
    #         #     f2 = Peaks_db_file.objects.filter(filename=full_filename_j).values('path')
    #         #     f2 = os.path.join(f2[0]['path'], full_filename_j)
    #         #     file_two_user_uploaded = False
    #         # else:
    #         ######################################################
    #         full_filename_j = region + '_' + fname[j]
    #
    #         f2 = os.path.join(user_path, full_filename_j)
    #         ######################################################
    #
    #         if i == j:
    #             reg_matrix[i][j] = calculatePearsonCor(1, reg)
    #             break
    #         elif file_one_user_uploaded:
    #             f1 = os.path.join(user_path, reg + '_' + fname[i])
    #         elif file_two_user_uploaded:
    #             f2 = os.path.join(user_path, reg + '_' + fname[j])
    #
    #         if file_one_user_uploaded or file_two_user_uploaded:
    #             # use jaccard index
    #             file1 = bt(f1)
    #             file2 = bt(f2)
    #             result = file1.jaccard(file2) # This is where the jaccard is calculated
    #             jaccard_index = result['jaccard']
    #         else:
    #             jaccard_index = jaccard_indices[full_filename_j]
    #
    #         if math.isnan(jaccard_index) or jaccard_index < 0:
    #             reg_matrix[i][j] = 0
    #             reg_matrix[j][i] = 0
    #
    #             reg_pval_matrix[i][j] = 1
    #             reg_pval_matrix[j][i] = 1
    #
    #             reg_dist_matrix[i][j] = 1
    #             reg_dist_matrix[j][i] = 1
    #         else:
    #             jaccard_fc = calculateJaccardFC(jaccard_index, reg)
    #             reg_matrix[i][j] = jaccard_fc
    #             reg_matrix[j][i] = jaccard_fc
    #
    #             jaccard_pval = calculateJaccardPval(jaccard_index, reg)
    #             reg_pval_matrix[i][j] = jaccard_pval
    #             reg_pval_matrix[j][i] = jaccard_pval
    #
    #             reg_dist_matrix[i][j] = 1-jaccard_index
    #             reg_dist_matrix[j][i] = 1-jaccard_index
    #
    #         if jaccard_fc > reg_fc_limit[-1]:
    #             reg_fc_limit[-1] = jaccard_fc
    #         elif jaccard_fc < reg_fc_limit[0]:
    #             reg_fc_limit[0] = jaccard_fc


    # return reg_matrix, reg_dist_matrix
    return cor_matrix
