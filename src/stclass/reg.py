
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
            
            if region == 'WG':
                
                curFile = pd.DataFrame(columns=['chromosome', 'start', 'end', 'count', name])
                # load all the files and concatenate all
                region_list = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12', 'IRS', 'SUE', 'PRS']
                for r in region_list:
                    f_path = os.path.join(settings.MEDIA_ROOT, 'signal_state_file_db', r)
                    f = pd.read_csv(f_path+'/'+r+'_'+name, sep="\t",header = None)
                    f.columns = ['chromosome', 'start', 'end', 'count', name]
                    curFile = pd.concat([curFile, f])
                # make sure that start and chr combo is unique
                curFile = curFile.drop_duplicates()
                # sort by chr and start
                curFile = curFile.sort_values(by=['chromosome', 'start'])
        
            else:
                f_path = os.path.join(settings.MEDIA_ROOT, 'signal_state_file_db', region)
                curFile = pd.read_csv(f_path+'/'+region+'_'+name, sep = "\t", header = None)
                # column name is rpkm value
                curFile.columns = ['chromosome', 'start', 'end', 'count', name]
        else:
            if region == "WG":
                curFile = pd.DataFrame(columns=['chromosome', 'start', 'end', 'count', name])
                # load all the files and concatenate all
                region_list = ['E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12', 'IRS', 'SUE', 'PRS']
                for r in region_list:
                    f_path = os.path.join(user_path, 'output', 'mapped', r)
                    try:
                        f = pd.read_csv(f_path+'/'+r+'_'+name, sep = "\t", header = None)
                        f.columns = ['chromosome', 'start', 'end', 'count', name]
                        curFile = pd.concat([curFile, f])
                    except pd.errors.EmptyDataError:
                        next
                # make sure that start and chr combo is unique
                curFile = curFile.drop_duplicates()
                # sort by chr and start
                curFile = curFile.sort_values(by=['chromosome', 'start'])
            else:
                f_path = os.path.join(user_path, 'output', 'mapped', region)
            
                try:
                    curFile = pd.read_csv(f_path+'/'+region+'_'+name, sep = "\t", header = None)
                    curFile.columns = ['chromosome', 'start', 'end', 'count', name]
                except pd.errors.EmptyDataError:
                    next

        # cur = curFile[['chromosome', name]]
        # cur = cur.sort_values(by='chromosome', ascending = True)
        curFile = curFile.sort_values(by=['chromosome', 'start'], ascending=True)
        
        # rpkm = rpkm.loc[~rpkm.index.duplicated(keep='first')]
        # cur = cur.loc[~cur.index.duplicated(keep='first')]
        
        # rpkm = pd.concat([rpkm, cur[name]], axis = 1)
        if rpkm.empty:
            rpkm = curFile[[name]].copy()
        else:
            rpkm.reset_index(inplace=True, drop=True)
            curFile.reset_index(inplace=True, drop=True)
            rpkm = pd.concat([rpkm, curFile[name]], axis = 1)
        
    # Calculate pearson correlation (distance matrix).
    cor_matrix = 1 - rpkm.corr(method = "pearson")


    return cor_matrix
