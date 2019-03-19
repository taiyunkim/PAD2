
from .models import Peaks_db_file, Peaks_db
from .function import createPeakToBedFile, calculateJaccardPval, calculateJaccardFC, getPrecomputedJaccardValuePerFile

import os
import math

from pybedtools import BedTool as bt



def pos_mats(fname, user_uploaded_filename, matrix_size, cutoff, user_path, pos = "proximal"):
    pos_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
    pos_pval_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
    pos_dist_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]


    pos_fc_limit = [float("inf"), float("-inf")]
    for i in range(matrix_size):
        file_one_user_uploaded = True
        if fname[i] not in user_uploaded_filename:
            full_filename_i = Peaks_db.objects.get(fileID=fname[i])
            full_filename_i = full_filename_i.origFile + '_' + pos + '_' + str(cutoff)
            f1 = Peaks_db_file.objects.filter(filename=full_filename_i).values('path')
            f1 = os.path.join(f1[0]['path'], full_filename_i)
            file_one_user_uploaded = False
        else:
            full_filename_i = fname[i] + '_' + pos + '_' + str(cutoff)

            f1 = os.path.join(user_path, full_filename_i)

        if not file_one_user_uploaded:
            jaccard_indices = getPrecomputedJaccardValuePerFile(full_filename_i)

        for j in range(matrix_size):
            file_two_user_uploaded = True
            if fname[j] not in user_uploaded_filename:
                full_filename_j = Peaks_db.objects.get(fileID=fname[j])
                full_filename_j = full_filename_j.origFile + '_' + pos + '_' + str(cutoff)

                f2 = Peaks_db_file.objects.filter(filename=full_filename_j).values('path')
                f2 = os.path.join(f2[0]['path'], full_filename_j)
                file_two_user_uploaded = False
            else:
                full_filename_j = fname[j] + '_' + pos + '_' + str(cutoff)

                f2 = os.path.join(user_path, full_filename_j)
            if i == j:
                pos_matrix[i][j] = calculateJaccardFC(1, pos)
                pos_pval_matrix[i][j] = 0
                pos_dist_matrix[i][j] = 0
                break
            elif file_one_user_uploaded:
                f1 = os.path.join(user_path, fname[i]+'_' + pos + '_'+str(cutoff))
            elif file_two_user_uploaded:
                f2 = os.path.join(user_path, fname[j]+'_' + pos + '_'+str(cutoff))

            if file_one_user_uploaded or file_two_user_uploaded:
                # use jaccard index
                file1 = bt(f1)
                file2 = bt(f2)
                result = file1.jaccard(file2) # This is where the jaccard is calculated
                jaccard_index = result['jaccard']
            else:
                jaccard_index = jaccard_indices[full_filename_j]

            if math.isnan(jaccard_index) or jaccard_index < 0:
                pos_matrix[i][j] = 0
                pos_matrix[j][i] = 0

                pos_pval_matrix[i][j] = 1
                pos_pval_matrix[j][i] = 1

                pos_dist_matrix[i][j] = 1
                pos_dist_matrix[j][i] = 1
            else:
                jaccard_fc = calculateJaccardFC(jaccard_index, pos)
                pos_matrix[i][j] = jaccard_fc
                pos_matrix[j][i] = jaccard_fc

                jaccard_pval = calculateJaccardPval(jaccard_index, pos)
                pos_pval_matrix[i][j] = jaccard_pval
                pos_pval_matrix[j][i] = jaccard_pval

                pos_dist_matrix[i][j] = 1-jaccard_index
                pos_dist_matrix[j][i] = 1-jaccard_index

            if jaccard_fc > pos_fc_limit[-1]:
                pos_fc_limit[-1] = jaccard_fc
            elif jaccard_fc < pos_fc_limit[0]:
                pos_fc_limit[0] = jaccard_fc


    return pos_matrix, pos_pval_matrix, pos_dist_matrix, pos_fc_limit
