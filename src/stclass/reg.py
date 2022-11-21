
from django.conf import settings

from rgclass.models import Signal_db
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
            f_path = os.path.join(settings.MEDIA_ROOT, 'signal_state_file_db', region)

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
        else:
            f_path = os.path.join(user_path, 'output', 'mapped', region)
            
            try:
                curFile = pd.read_csv(f_path+'/'+region+'_'+name, sep = "\t", header = None)
                curFile.columns = ['chromosome', 'start', 'end', 'count', name]
                cur = curFile[['chromosome', name]]
                cur = cur.sort_values(by='chromosome', ascending = True)
                rpkm = pd.concat([rpkm, cur[name]], axis = 1)
            except pd.errors.EmptyDataError:
                # curFile = pd.DataFrame(columns = ['chromosome', 'start', 'end', 'count', name])
                next
            
            # curFile.columns = ['chromosome', 'start', 'end', 'count', name]
            # cur = curFile[['chromosome', name]]
            # cur = cur.sort_values(by='chromosome', ascending = True)
            # rpkm = pd.concat([rpkm, cur[name]], axis = 1)
    # Calculate pearson correlation (distance matrix).
    cor_matrix = 1 - rpkm.corr(method = "pearson")


    return cor_matrix
