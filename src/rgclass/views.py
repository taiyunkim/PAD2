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
# from .function import
from .models import Signal_db

from .reg import reg_mats

from copy import deepcopy
from pybedtools import BedTool as bt
from scipy.cluster.hierarchy import dendrogram, linkage
import scipy.spatial.distance as ssd


import re
import os
import math

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
    table = Signal_db.objects.all().values('fileID')
    context = {
        'form': form,
        'table': table,
        'page': "PADv2"
    }
    request.session.save()
    if form.is_valid():
        signalfile_names = []

        cleaned_data = form.cleaned_data
        if 'signal_File' in request.FILES:
            signalfile_list = request.FILES.getlist('signal_File')
            # createsignalToBedFile(signalfile_list, str(request.session.session_key), cleaned_data.get('gene_database'))
            for name in signalfile_list:
                signalfile_names.append(name.name)
        region = cleaned_data.get('region')
        signal_name_strings = cleaned_data.get('selected_field')
        signal_database_id = signal_name_strings.rstrip().split()
        # gene_database_name = cleaned_data.get('gene_database')

        signal_database_names = Signal_db.objects.filter(fileID__in = signal_database_id).values_list('fileID', 'filename')
        tmp = signal_database_names.values_list('filename', flat = True)
        tmp_names = signal_database_names.values_list('fileID', flat = True)
        signal_database_names = list(tmp)
        signal_database_id = list(tmp_names)

        request.session['region'] = region
        request.session['signal_database_names'] = signal_database_names
        # request.session['gene_database'] = gene_database_name
        request.session['signalfile_names'] = signalfile_names
        request.session['signal_database_id'] = signal_database_id
        # request.session['heatmap'] = cleaned_data.get('heatmap')

        return redirect('/result')
    return render(request, 'tfClassify.html', context)




# === tfClassifyResult ===
def rgClassifyResult(request):
    # cutoff value from post
    region = request.session['region']
    # pvalue = float(request.session['pvalue'])

    signal_database_names = request.session['signal_database_names']
    # gene_database_name = request.session['gene_database']
    signalfile_names = request.session['signalfile_names']
    signal_database_id = request.session['signal_database_id']
    # heatmap = request.session['heatmap']

    signalfile_choices = tuple([(x, x) for x in signalfile_names])
    form = VariableInputForm(
        request.POST or None,
        request.FILES or None,
        initial = {
            'region': region,
            'selected_field': '\n'.join(signal_database_id),
            'uploaded_signal_File': signalfile_names,
            # 'pvalue': pvalue,
        }
    )
    # leave previous choices at field
    form.fields['uploaded_signal_File'].choices = signalfile_choices

    if form.is_valid():
        cleaned_data = form.cleaned_data
        region = cleaned_data.get('region')
        # pvalue = cleaned_data.get('pvalue')
        new_signal_File = request.FILES.getlist('new_signal_File')
        signalfile_names = request.POST.getlist('uploaded_signal_File')

        for name in new_signal_File:
            signalfile_names.append(name.name)

        region = cleaned_data.get('region')
        signal_name_strings = cleaned_data.get('selected_field')
        signal_database_id = signal_name_strings.rstrip().split()
        # gene_database_name = cleaned_data.get('gene_database')

        signal_database_names = Signal_db.objects.filter(fileID__in = signal_database_id).values_list('fileID', 'filename')
        tmp = signal_database_names.values_list('filename', flat = True)
        tmp_names = signal_database_names.values_list('fileID', flat = True)
        signal_database_names = list(tmp)
        signal_database_id = list(tmp_names)


        request.session['region'] = region
        request.session['signal_database_names'] = signal_database_names
        # request.session['gene_database'] = gene_database_name
        request.session['signalfile_names'] = signalfile_names
        request.session['signal_database_id'] = signal_database_id
        # request.session['heatmap'] = cleaned_data.get('heatmap')

        return redirect('/result')




    # THIS IS WHERE USER INPUT signal FILE IS SEPARATED TO PROXIMAL AND DISTAL
    fname = signalfile_names
    user_uploaded_filename = signalfile_names
    # for name in signalfile_names:
    #     full_path = os.path.join(settings.MEDIA_ROOT, 'users_signal_files', str(request.session.session_key), str(gene_database_name), '')
    #     # grab the original file
    #     with open(full_path+name, 'rb') as orig_file:
    #         prox_file = open(full_path+name+'_proximal_'+str(cutoff), 'w')
    #         dist_file = open(full_path+name+'_distal_'+str(cutoff), 'w')
    #         for line in orig_file.readlines():
    #             gene_dist = re.search('\d+\s\n', line)
    #             if int(gene_dist.group(0)) <= int(cutoff):
    #                 prox_file.writelines(line)
    #             else:
    #                 dist_file.writelines(line)
    #         prox_file.close()
    #         dist_file.close()
    #     orig_file.close()

    fname = fname + signal_database_names
    # fname.sort()
    matrix_size = len(fname)

    path = os.path.join(settings.MEDIA_ROOT, 'signal_file_db', region)
    user_path = os.path.join(settings.MEDIA_ROOT, 'users_signal_files', str(request.session.session_key))

    start_time = time.time()
    reg_matrix = reg_mats(fname, user_uploaded_filename, matrix_size, region, user_path)

    regional_dist_vector = ssd.squareform(reg_matrix)
    regional_linkage_matrix = linkage(regional_dist_vector, "single", 'euclidean')
    # regional_dendrogram = dendrogram(regional_linkage_matrix, labels=fname)
    regional_dendrogram = dendrogram(regional_linkage_matrix, labels=signal_database_id)

    f_order = regional_dendrogram['ivl']
    ordered_reg_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]

    # find the index of ordered item in the original matrix
    # use the index found and get the value from the original matrix and get the value and insert to new matrix
    for i, f_name1 in enumerate(f_order):
        # index1 = fname.index(f_name1)
        index1 = signal_database_id.index(f_name1)
        for j, f_name2 in enumerate(f_order):
            # index2 = fname.index(f_name2)
            index2 = signal_database_id.index(f_name2)

            ordered_reg_matrix[i][j] = 1-reg_matrix.values[index1][index2]



    proc_time = time.time()-start_time
    json_data = json.dumps(
        {
            # 'reg_matrix': reg_matrix.values.tolist(),
            'reg_matrix': ordered_reg_matrix,
            # 'app': "reg",
            'r_filename': f_order,
            # 'd_filename': fna,
            'matrix_size': matrix_size,
            # 'proximal_matrix': ordered_proximal_matrix,
            # 'proximal_pval_matrix': ordered_proximal_pval_matrix,
            'regional_dendrogram': regional_dendrogram,
            # 'distal_matrix': ordered_distal_matrix,
            # 'distal_pval_matrix': ordered_distal_pval_matrix,
            # 'distal_dendrogram': distal_dendrogram,
            # 'proxdist_fc_limit': [proximal_fc_limit, distal_fc_limit],
            # 'proc_time': proc_time
        }
    )
    table = Signal_db.objects.all().values('fileID')

    context = {
        'form': form,
        'table': table,
        'signalfile_names': signalfile_names,
        'json_data': json_data,
        # 'proximal_dendrogram': proximal_dendrogram,
        # 'distal_dendrogram': distal_dendrogram,
        'app': "reg",
        'matrix': True,
        'page': "PADv2"
    }

    return render(request, 'tfClassify.html', context)
