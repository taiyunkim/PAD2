from django.conf import settings

from django_ajax.decorators import ajax

from .models import Signal_db
# from .function import createPeakToBedFile, calculateJaccardPval, calculateJaccardFC, getPrecomputedJaccardValuePerFile
# from .function import calculatePearsonCor


import os
import math
import pandas as pd
import re

@ajax
def rank_scatter(request, selected_file = None):
    print(selected_file)
    

