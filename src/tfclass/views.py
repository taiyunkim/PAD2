"""
All the views for our tfclass app.
Currently there are 2 views:

1. **tfClassifyForm** - The main initial page(home) for tfclass. (jump to section in [[views.py#tfClassifyForm]] )
2. **tfClassifyResult** - The result page after form has been submitted. (jump to section in [[views.py#tfClassifyResult]] )
"""
import matplotlib
import time

matplotlib.use('Agg')

from django.http import HttpResponse
# from django.template import loader

from wsgiref.util import FileWrapper
import mimetypes

from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect

from django.forms import widgets

from .forms import InputForm, VariableInputForm
from .function import createPeakToBedFile, calculateJaccardPval, calculateJaccardFC, getPrecomputedJaccardValuePerFile
from .models import Peaks_db_file, Peaks_db

from .pad import pos_mats
# from .region import regional

from copy import deepcopy
from pybedtools import BedTool as bt
from scipy.cluster.hierarchy import dendrogram, linkage
import scipy.spatial.distance as ssd


import re
import os
import math

import json


# === tfClassifyForm ===
def tfClassifyForm(request):
    form = InputForm(
        request.POST or None,
        request.FILES or None,
        initial = {
            'selected_field': """368.Wdr5.CCE
10.c-Myc.E14
128.KDM5A.LF2
15.CHD7.R1
9.Brg.E14Tg2a
274.Sox2.V6.5
181.Oct-04.V6.5
172.Nanog.V6.5
142.Med1.ZHBTc4
379.Ring1b.OS25
112.Ino80.J1""",
            'cut_off': 1000,
            'pvalue': 0.01,
        }
    )
    table = Peaks_db.objects.all().values('protein', 'origFile', 'fileID', 'num_peaks', 'cells', 'labs', 'year')
    context = {
        'form': form,
        'table': table,
        'page': "PADv1"
    }
    request.session.save()
    if form.is_valid():
        peakfile_names = []

        cleaned_data = form.cleaned_data
        if 'peak_File' in request.FILES:
            peakfile_list = request.FILES.getlist('peak_File')
            createPeakToBedFile(peakfile_list, str(request.session.session_key), cleaned_data.get('gene_database'))
            for name in peakfile_list:
                peakfile_names.append(name.name)
        cutoff = cleaned_data.get('cut_off')
        peak_name_strings = cleaned_data.get('selected_field')
        peak_database_names = peak_name_strings.rstrip().split()
        gene_database_name = cleaned_data.get('gene_database')

        request.session['cut_off'] = cutoff
        request.session['peak_database_names'] = peak_database_names
        request.session['gene_database_name'] = gene_database_name
        request.session['peakfile_names'] = peakfile_names
        request.session['heatmap'] = cleaned_data.get('heatmap')
        request.session['pvalue'] = cleaned_data.get('pvalue')
        return redirect('/PADv1/result')
    return render(request, 'tfClassify.html', context)



# === tfClassifyResult ===
def tfClassifyResult(request):
    # cutoff value from post
    cutoff = int(request.session['cut_off'])
    pvalue = float(request.session['pvalue'])

    peak_database_names = request.session['peak_database_names']
    gene_database_name = request.session['gene_database_name']
    peakfile_names = request.session['peakfile_names']
    heatmap = request.session['heatmap']

    peakfile_choices = tuple([(x, x) for x in peakfile_names])
    form = VariableInputForm(
        request.POST or None,
        request.FILES or None,
        initial = {
            'cut_off': cutoff,
            'selected_field': '\n'.join(peak_database_names),
            'uploaded_peak_File': peakfile_names,
            'pvalue': pvalue,
        }
    )
    # leave previous choices at field
    form.fields['uploaded_peak_File'].choices = peakfile_choices

    if form.is_valid():
        # new user input form is submitted
        cleaned_data = form.cleaned_data
        cutoff = cleaned_data.get('cut_off')
        pvalue = cleaned_data.get('pvalue')
        new_peak_File = request.FILES.getlist('new_peak_File')
        peakfile_names = request.POST.getlist('uploaded_peak_File')

        createPeakToBedFile(new_peak_File, str(request.session.session_key), gene_database_name)
        for name in new_peak_File:
            peakfile_names.append(name.name)

        request.session['cut_off'] = cutoff
        request.session['pvalue'] = pvalue

        peak_name_strings = cleaned_data.get('selected_field')
        peak_database_names = peak_name_strings.rstrip().split()

        request.session['peak_database_names'] = peak_database_names
        request.session['gene_database_name'] = gene_database_name
        request.session['peakfile_names'] = peakfile_names
        request.session['heatmap'] = cleaned_data.get('heatmap')


        # redirect to this page with different parameters
        return redirect('/PADv1/result')




    # THIS IS WHERE USER INPUT PEAK FILE IS SEPARATED TO PROXIMAL AND DISTAL
    fname = peakfile_names
    user_uploaded_filename = peakfile_names
    for name in peakfile_names:
        full_path = os.path.join(settings.MEDIA_ROOT, 'users_peak_files', str(request.session.session_key), str(gene_database_name), '')
        # grab the original file
        with open(full_path+name, 'rb') as orig_file:
            prox_file = open(full_path+name+'_proximal_'+str(cutoff), 'w')
            dist_file = open(full_path+name+'_distal_'+str(cutoff), 'w')
            for line in orig_file.readlines():
                gene_dist = re.search('\d+\s\n', line.decode('utf-8'))
                if int(gene_dist.group(0)) <= int(cutoff):
                    prox_file.writelines(line.decode('utf-8'))
                else:
                    dist_file.writelines(line.decode('utf-8'))
            prox_file.close()
            dist_file.close()
        orig_file.close()

    fname = fname + peak_database_names
    fname.sort()
    matrix_size = len(fname)

    path = os.path.join(settings.MEDIA_ROOT, 'peak_file_db', str(gene_database_name), str(cutoff))
    user_path = os.path.join(settings.MEDIA_ROOT, 'users_peak_files', str(request.session.session_key), str(gene_database_name))
    # FOR PROXIMAL
    start_time = time.time()
    proximal_matrix, proximal_pval_matrix, proximal_dist_matrix, proximal_fc_limit = pos_mats(fname, user_uploaded_filename, matrix_size, cutoff, user_path, pos = "proximal")
    # FOR DISTAL
    distal_matrix, distal_pval_matrix, distal_dist_matrix, distal_fc_limit = pos_mats(fname, user_uploaded_filename, matrix_size, cutoff, user_path, pos = "distal")

    ########
    proximal_dendrogram = {}
    distal_dendrogram = {}
    # heatmap plots styles
    if heatmap == 'Independent':
        proximal_dist_vector = ssd.squareform(proximal_dist_matrix)
        proximal_linkage_matrix = linkage(proximal_dist_vector, "single", 'euclidean')
        proximal_dendrogram = dendrogram(proximal_linkage_matrix, labels=fname)

        distal_dist_vector = ssd.squareform(distal_dist_matrix)
        distal_linkage_matrix = linkage(distal_dist_vector, "single", "euclidean")
        distal_dendrogram = dendrogram(distal_linkage_matrix, labels=fname)

        # fname = names of the files (ivl)
        f_order = proximal_dendrogram['ivl']
        # reorder the matrix by new order of the dendogram
        ordered_proximal_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
        ordered_proximal_pval_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
        # find the index of ordered item in the original matrix
        # use the index found and get the value from the original matrix and get the value and insert to new matrix
        for i, f_name1 in enumerate(f_order):
            index1 = fname.index(f_name1)
            for j, f_name2 in enumerate(f_order):
                index2 = fname.index(f_name2)

                if proximal_pval_matrix[index1][index2] <= pvalue:
                    ordered_proximal_matrix[i][j] = proximal_matrix[index1][index2]
                else:
                    ordered_proximal_matrix[i][j] = float("-inf")

                ordered_proximal_pval_matrix[i][j] = 'p-value: {:1.5f}'.format(proximal_pval_matrix[index1][index2])

        f_order = distal_dendrogram['ivl']
        ordered_distal_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
        ordered_distal_pval_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
        for i, f_name1 in enumerate(f_order):
            index1 = fname.index(f_name1)
            for j, f_name2 in enumerate(f_order):
                index2 = fname.index(f_name2)

                if distal_pval_matrix[index1][index2] <= pvalue:
                    ordered_distal_matrix[i][j] = distal_matrix[index1][index2]
                else:
                    ordered_distal_matrix[i][j] = float("-inf")

                ordered_distal_pval_matrix[i][j] = 'p-value: {:1.5f}'.format(distal_pval_matrix[index1][index2])

        p_name = proximal_dendrogram['ivl']
        p_new_ls = p_name
        d_name = distal_dendrogram['ivl']
        d_new_ls = d_name
    else:
        f_order = []
        p_new_ls = []
        d_new_ls = []
        if heatmap == 'Follow proximal':
            proximal_dist_vector = ssd.squareform(proximal_dist_matrix)
            proximal_linkage_matrix = linkage(proximal_dist_vector, "single", 'euclidean')
            proximal_dendrogram = dendrogram(proximal_linkage_matrix, labels=fname)
            distal_dendrogram = "None"
            f_order = proximal_dendrogram['ivl']
            p_name = proximal_dendrogram['ivl']
            p_new_ls = p_name
            d_new_ls = p_name
        elif heatmap == 'Follow distal':
            distal_dist_vector = ssd.squareform(distal_dist_matrix)
            distal_linkage_matrix = linkage(distal_dist_vector, "single", "euclidean")
            distal_dendrogram = dendrogram(distal_linkage_matrix, labels=fname)
            proximal_dendrogram = "None"
            f_order = distal_dendrogram['ivl']
            d_name = distal_dendrogram['ivl']
            p_new_ls = d_name
            d_new_ls = d_name
        ordered_proximal_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
        ordered_proximal_pval_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
        ordered_distal_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
        ordered_distal_pval_matrix = [[0 for x in range(matrix_size)] for x in range(matrix_size)]
        for i, f_name1 in enumerate(f_order):
            index1 = fname.index(f_name1)
            for j, f_name2 in enumerate(f_order):
                index2 = fname.index(f_name2)

                if proximal_pval_matrix[index1][index2] <= pvalue:
                    ordered_proximal_matrix[i][j] = proximal_matrix[index1][index2]
                else:
                    ordered_proximal_matrix[i][j] = float("-inf")

                if distal_pval_matrix[index1][index2] <= pvalue:
                    ordered_distal_matrix[i][j] = distal_matrix[index1][index2]
                else:
                    ordered_distal_matrix[i][j] = float("-inf")

                ordered_proximal_pval_matrix[i][j] = 'p-value: {:1.5f}'.format(proximal_pval_matrix[index1][index2])
                ordered_distal_pval_matrix[i][j] = 'p-value: {:1.5f}'.format(distal_pval_matrix[index1][index2])

    proc_time = time.time()-start_time
    json_data = json.dumps(
        {
            'p_filename': p_new_ls,
            'd_filename': d_new_ls,
            'matrix_size': matrix_size,
            'proximal_matrix': ordered_proximal_matrix,
            'proximal_pval_matrix': ordered_proximal_pval_matrix,
            'proximal_dendrogram': proximal_dendrogram,
            'distal_matrix': ordered_distal_matrix,
            'distal_pval_matrix': ordered_distal_pval_matrix,
            'distal_dendrogram': distal_dendrogram,
            'proxdist_fc_limit': [proximal_fc_limit, distal_fc_limit],
            'proc_time': proc_time
        }
    )
    table = Peaks_db.objects.all().values('protein', 'fileID', 'num_peaks', 'cells', 'labs', 'year')

    context = {
        'form': form,
        'table': table,
        'peakfile_names': peakfile_names,
        'json_data': json_data,
        'proximal_dendrogram': proximal_dendrogram,
        'distal_dendrogram': distal_dendrogram,
        'matrix': True,
        'app': "pad",
        'page': "PADv1"
    }

    return render(request, 'tfClassify.html', context)

# === tfClassifyGuide ===
def tfClassifyGuide(request):
    return render(request, 'tfGuide.html', context={'page':'instruction'})


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