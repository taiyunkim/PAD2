"""
All the views for our rgclass app.
Currently there are 2 views:

1. **rgClassifyForm** - The main initial page(home) for rgclass. (jump to section in [[views.py#rgClassifyForm]] )
2. **rgClassifyResult** - The result page after form has been submitted. (jump to section in [[views.py#rgClassifyResult]] )
"""

import matplotlib
import time

matplotlib.use('Agg')

from django.http import HttpResponse
# from django.template import loader
from wsgiref.util import FileWrapper
import mimetypes
# from django.utils.encoding import smart_str

from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect

# from django.forms import widgets

from .forms import InputForm, VariableInputForm
from .function import createPeakToBedFile
# from .function import
from .models import Signal_db
from .models import Signal_state_db_info

from .reg import reg_mats
# from .rank_scatter import rank_scatter

# from copy import deepcopy
from pybedtools import BedTool as bt
from scipy.cluster.hierarchy import dendrogram, linkage
import scipy.spatial.distance as ssd
# from django_ajax.decorators import ajax


# import re
import os
# import math
import copy
import csv

import json
# import numpy as np
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
    table = Signal_db.objects.all().values('fileID', 'filename', 'category')
    
    if (request.POST.get('interest') is not None):
        interest_choices = request.POST.get('interest')
        form.fields['interest'].choices = [(interest_choices, interest_choices)]
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
        
        signal_database_names = Signal_db.objects.filter(fileID__in = signal_database_id).values_list('fileID', 'filename', 'category')
        tmp = signal_database_names.values_list('filename', flat = True)
        tmp_names = signal_database_names.values_list('fileID', flat = True)
        signal_database_names = list(tmp)
        signal_database_id = list(tmp_names)

        request.session['region'] = region
        request.session['signal_database_names'] = signal_database_names
        request.session['signalfile_names'] = signalfile_names
        request.session['signal_database_id'] = signal_database_id

        request.session['rank_plot'] = cleaned_data.get('rank_plot')
        request.session['interest'] = cleaned_data.get('interest')
        # request.session['category'] = cleaned_data.get('category')
        
        return redirect('/result')
    return render(request, 'tfClassify.html', context)


# === tfClassifyResult ===
def rgClassifyResult(request):
    region = request.session['region']
    
    signal_database_names = request.session['signal_database_names']
    signalfile_names = request.session['signalfile_names']
    signal_database_id = request.session['signal_database_id']
    
    signalfile_choices = tuple([(x, x) for x in signalfile_names])
    
    rank_plot = request.session['rank_plot']
    interest = request.session['interest']
    
    form = VariableInputForm(
        request.POST or None,
        request.FILES or None,
        initial = {
            'region': region,
            'selected_field': '\n'.join(signal_database_id),
            'uploaded_signal_File': signalfile_names,
            'rank_plot': rank_plot,
            'interest': interest
            # 'category': category
        }
    )
    # leave previous choices at field
    form.fields['uploaded_signal_File'].choices = signalfile_choices
    
    if (request.POST.get('interest') is not None):
        interest_choices = request.POST.get('interest')
        form.fields['interest'].choices = [(interest_choices, interest_choices)]
    else:
        # signal_database_names
        # signal_database_id
        interest_choices = tuple([(x, y) for x,y in zip(signal_database_names, signal_database_id)])
        # interest_choices = tuple([(x, x) for x in interest])
        form.fields['interest'].choices = interest_choices
    
    
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
        
        signal_database_names = Signal_db.objects.filter(fileID__in = signal_database_id).values_list('fileID', 'filename', 'category')
        tmp = signal_database_names.values_list('filename', flat = True)
        tmp_names = signal_database_names.values_list('fileID', flat = True)
        
        category = Signal_db.objects.filter(filename = interest).values_list('category', flat = True)
        # category = signal_database_names.values_list('category', flat = True)
        
        signal_database_names = list(tmp)
        signal_database_id = list(tmp_names)
        # category_list = list(category)

        request.session['region'] = region
        request.session['signal_database_names'] = signal_database_names
        request.session['signalfile_names'] = signalfile_names
        request.session['signal_database_id'] = signal_database_id

        request.session['rank_plot'] = cleaned_data.get('rank_plot')
        # request.session['category'] = cleaned_data.get('category')
        request.session['interest'] = cleaned_data.get('interest')
        
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

    # path = os.path.join(settings.MEDIA_ROOT, 'signal_state_file_db', region)
    user_path = os.path.join(settings.MEDIA_ROOT, 'PAD2', 'users_signal_files', str(request.session.session_key))

    # start_time = time.time()
    category = Signal_db.objects.filter(filename = interest).values_list('category', flat = True).first()
        
    if rank_plot:
        # Replace fname with a full list of files in the category + fname
        # category_db = Signal_db.objects.filter(category = category).values_list('fileID', 'filename', 'category')
        category_db = Signal_db.objects.filter(category = category).values_list('fileID', 'filename', 'category')
        filename = category_db.values_list('filename', flat = True)
        fileID = category_db.values_list('fileID', flat = True)
        
        selected_fname = fname
        
        fname = category_db_names = list(filename)
        fname = fname + [s for s in selected_fname if s not in fname]
        matrix_size = len(fname)
        full_matrix = reg_mats(fname, signalfile_names, matrix_size, region, user_path)
        
        # For cluster analysis
        reg_matrix = full_matrix.loc[selected_fname, selected_fname]
        matrix_size = len(selected_fname)
        
        # For rank plot
        
        category_db_names = category_db_names + signalfile_names
        category_cor = full_matrix.loc[category_db_names, [interest]]
        category_cor['fileID'] = list(fileID) + signalfile_names
        # interest correlation column
        category_db_names_subset = [s for s in category_db_names if s not in interest]
        
        # category_db_names_subset = category_db_names_subset + signalfile_names
        
        
        category_cor = category_cor.loc[category_db_names_subset, [interest, 'fileID']]
        
        category_cor.sort_values(by=interest, ascending=False, inplace= True)
        highlight_name = [s for s in selected_fname if s in category_db_names]
        # highlight_name = highlight_name + signalfile_names
        
        
        filename = [s for s in category_cor.index]
        fileID = [s for s in category_cor['fileID']]
        cor = [s for s in category_cor[interest]]
        
        
    else:
        reg_matrix = reg_mats(fname, signalfile_names, matrix_size, region, user_path)
    # reg_matrix = reg_mats(fname, signalfile_names, matrix_size, region, user_path)

    
    regional_dist_vector = ssd.squareform(reg_matrix)
    regional_linkage_matrix = linkage(regional_dist_vector, "single", 'euclidean')
    
    
    if len(reg_matrix.columns) != len(f_label_names): # There is an empty file and hence not included
        new_col = reg_matrix.columns
        diff = set(fname) - set(new_col)
        f_label_names = [f_label_names[i] for i, val in enumerate(fname) if val not in diff]
        matrix_size = len(f_label_names)

    
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
        
    # proc_time = time.time()-start_time
    
    
    
    cluster_load = {
        'reg_matrix': ordered_reg_matrix,
        'r_filename': f_order_new,
        'matrix_size': matrix_size,
        'regional_dendrogram': regional_dendrogram,
        
    }
    if rank_plot:
        rank_load = {
            'highlight_name': highlight_name,
            'fileID': fileID,
            'filename': filename,
            'cor': cor,
            'interest_name': interest,
            'category': category
            # 'category_cor': category_cor.to_json(orient="columns")
        }
        cluster_load.update(rank_load)
        
    json_data = json.dumps(
        cluster_load
    )
    table = Signal_db.objects.all().values('fileID', 'filename', 'category')

    context = {
        'form': form,
        'table': table,
        'signalfile_names': signalfile_names,
        'json_data': json_data,
        'app': "reg",
        'region': region,
        'matrix': True,
        'page': "newPAD",
        'signal_database_names': signal_database_names,
        'signal_database_id': signal_database_id,
        'f_label_names': f_label_names,
        'rank_plot': rank_plot,
        'category': category,
        'interest': interest
    }

    return render(request, 'tfClassify.html', context)


def download(request, file_name):
    file_path = settings.MEDIA_ROOT +'/sample/'+ file_name
    f = open(file_path, 'rb')
    file_wrapper = FileWrapper(f)
    file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper, content_type=file_mimetype )
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename=%s' % file_name
    return response

