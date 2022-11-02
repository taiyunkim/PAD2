"""
All the views for our rgclass app.
Currently there are 2 views:

1. **rgClassifyForm** - The main initial page(home) for rgclass. (jump to section in [[views.py#rgClassifyForm]] )
2. **rgClassifyResult** - The result page after form has been submitted. (jump to section in [[views.py#rgClassifyResult]] )
"""

import matplotlib
import time

matplotlib.use('Agg')

# from django.http import HttpResponse
# from django.template import loader


from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect

from django.forms import widgets

from .forms import InputForm, VariableInputForm
from .function import createPeakToBedFile
# from .function import
from rgclass.models import Signal_db
from .models import Signal_state_db_info

from .reg import reg_mats

from copy import deepcopy
from pybedtools import BedTool as bt
from scipy.cluster.hierarchy import dendrogram, linkage
import scipy.spatial.distance as ssd


import re
import os
import math
import copy
import csv

import json
import numpy as np
import pandas as pd

def rgClassifyForm(request):
    form = InputForm(
        request.POST or None,
        request.FILES or None,
        initial = {
#             'selected_field': """368.Wdr5.CCE
        }
    )
    # table = Signal_db.objects.all().values('fileID', 'filename')
    table = Signal_db.objects.all().values('fileID', 'filename')
    context = {
        'form': form,
        'table': table,
        'page': "newPAD"
    }
    request.session.save()
    if form.is_valid():
        signalfile_names = []
        cleaned_data = form.cleaned_data
        if 'signal_File' in request.FILES:
            signalfile_list = request.FILES.getlist('signal_File')
            createPeakToBedFile(signalfile_list, str(request.session.session_key))
            for name in signalfile_list:
                signalfile_names.append(name.name)

        region = cleaned_data.get('region')
        signal_name_strings = cleaned_data.get('selected_field')
        signal_database_id = signal_name_strings.rstrip().split()
        
        signal_database_names = Signal_db.objects.filter(fileID__in = signal_database_id).values_list('fileID', 'filename')
        tmp = signal_database_names.values_list('filename', flat = True)
        tmp_names = signal_database_names.values_list('fileID', flat = True)
        signal_database_names = list(tmp)
        signal_database_id = list(tmp_names)

        request.session['region'] = region
        request.session['signal_database_names'] = signal_database_names
        request.session['signalfile_names'] = signalfile_names
        request.session['signal_database_id'] = signal_database_id
        
        return redirect('/result')
    return render(request, 'tfClassify.html', context)




# === tfClassifyResult ===
def rgClassifyResult(request):
    region = request.session['region']
    
    signal_database_names = request.session['signal_database_names']
    signalfile_names = request.session['signalfile_names']
    signal_database_id = request.session['signal_database_id']
    
    signalfile_choices = tuple([(x, x) for x in signalfile_names])
    form = VariableInputForm(
        request.POST or None,
        request.FILES or None,
        initial = {
            'region': region,
            'selected_field': '\n'.join(signal_database_id),
            'uploaded_signal_File': signalfile_names,
        }
    )
    # leave previous choices at field
    form.fields['uploaded_signal_File'].choices = signalfile_choices

    if form.is_valid():
        cleaned_data = form.cleaned_data
        region = cleaned_data.get('region')
        new_signal_File = request.FILES.getlist('new_signal_File')
        signalfile_names = request.POST.getlist('uploaded_signal_File')

        createPeakToBedFile(new_signal_File, str(request.session.session_key))
        for name in new_signal_File:
            signalfile_names.append(name.name)

        # region = cleaned_data.get('region')
        signal_name_strings = cleaned_data.get('selected_field')
        signal_database_id = signal_name_strings.rstrip().split()
        
        signal_database_names = Signal_db.objects.filter(fileID__in = signal_database_id).values_list('fileID', 'filename')
        tmp = signal_database_names.values_list('filename', flat = True)
        tmp_names = signal_database_names.values_list('fileID', flat = True)
        signal_database_names = list(tmp)
        signal_database_id = list(tmp_names)


        request.session['region'] = region
        request.session['signal_database_names'] = signal_database_names
        request.session['signalfile_names'] = signalfile_names
        request.session['signal_database_id'] = signal_database_id


        region = cleaned_data.get('region')
        signal_name_strings = cleaned_data.get('selected_field')
        signal_database_id = signal_name_strings.rstrip().split()
        
        
        return redirect('/result')

    # THIS IS WHERE USER INPUT signal is opened from specific region of interest
    fname = signalfile_names
    
    fname = fname + signal_database_names
    f_label_names = signalfile_names + signal_database_id
    # fname.sort()
    matrix_size = len(fname)

    path = os.path.join(settings.MEDIA_ROOT, 'signal_state_file_db', region)
    user_path = os.path.join(settings.MEDIA_ROOT, 'PAD2', 'users_signal_files', str(request.session.session_key))

    start_time = time.time()
    reg_matrix = reg_mats(fname, signalfile_names, matrix_size, region, user_path)

    regional_dist_vector = ssd.squareform(reg_matrix)
    regional_linkage_matrix = linkage(regional_dist_vector, "single", 'euclidean')
    regional_dendrogram = dendrogram(regional_linkage_matrix, labels=f_label_names)
    
    f_order = regional_dendrogram['ivl']
    f_order_new = copy.deepcopy(regional_dendrogram['ivl'])
    ordered_reg_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
    # find the index of ordered item in the original matrix
    # use the index found and get the value from the original matrix and get the value and insert to new matrix
    signal_coverage_value = Signal_state_db_info.objects.filter(fileID__in = f_order, region = region).values_list('fileID', 'value')
    
    for i, f_name1 in enumerate(f_order):
        index1 = f_label_names.index(f_name1)

        for j, f_name2 in enumerate(f_order):
            index2 = f_label_names.index(f_name2)

            ordered_reg_matrix[i][j] = str(round(1-reg_matrix.values[index1][index2], 3))
            # ordered_reg_matrix[i][j] = 1-reg_matrix.values[index1][index2]
            
        
        # Fold change of user input data
        if (f_order_new[i] in signalfile_names):
            with open(user_path+'/output/mapped/'+f_order_new[i]+'_fc_dat.csv') as f:
                coverage = 0
                for r in csv.reader(f):
                    if r[0] == region and r[2] == f_order_new[i]:
                        coverage = float(r[1])
            f_order_new[i] = f_order_new[i] + ' (' + str(round(coverage, 3)) + ')'
        else:
            f_order_new[i] = f_order_new[i] + ' (' + str(round(list(signal_coverage_value.filter(fileID = f_order_new[i]).values_list('value', flat = True))[0], 3)) + ')'
        # f_order_new[i] = f_order_new[i]
        
    proc_time = time.time()-start_time
    json_data = json.dumps(
        {
            'reg_matrix': ordered_reg_matrix,
            'r_filename': f_order_new,
            'matrix_size': matrix_size,
            'regional_dendrogram': regional_dendrogram,
            
        }
    )
    table = Signal_db.objects.all().values('fileID', 'filename')

    context = {
        'form': form,
        'table': table,
        'signalfile_names': signalfile_names,
        'json_data': json_data,
        'app': "reg",
        'region': region,
        'matrix': True,
        'page': "newPAD"
    }

    return render(request, 'tfClassify.html', context)
