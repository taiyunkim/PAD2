from django import forms
from django.conf import settings

from multiupload.fields import MultiFileField

from .function import checkSignalFile

import csv
import os



# Input form for submission (in home page)
class InputForm(forms.Form):
    """
    The InputForm class is an initial form for users submission.
    A number of fields are required from user to select and upload.
    **selected_signals** - selected signals from the datatables (signals from database chosen for analysis).
    **gene_database** - name of a gene from database to be used for determining proximal and distal.
    **signal_File** - user's signal file upload field where it can be 1 or more files.
    **cut_off** - a threshold cut off to determine proximal and distal.
    **heatmap** - an option to generate heatmap axis ordering.
            (
                Independent: proximal and distal each separately show clustering.
                Follow prioximal: distal will not cluster and distal heatmap axis ordering will follow proximal heatmap axis ordering.
                Follow distal: proximal will not cluster and proximal heatmap axis ordering will follow distal heatmap axis ordering.
            )
    """

    # selected signal files from datatables
    selected_field = forms.CharField(widget=forms.Textarea(attrs={'readonly':'readonly','rows':6, 'cols':22, 'style':'resize:none;'}))

    # path = os.path.join(settings.STATIC_ROOT, 'csv', 'genenames.csv')
    # with open(path, 'r') as csvfile:
    #     reader = csv.reader(csvfile)
    #     genenames_list = list(map(tuple, reader))
    #
    # genenames_tuple = tuple(genenames_list)
    # GENENAMES_CHOICES = genenames_tuple
    # gene_database = forms.ChoiceField(choices=GENENAMES_CHOICES, required=True)

    # user input signal file
    signal_File = MultiFileField(min_num=0, required=False, label='Upload custom signal file', help_text='File must be in the form of <br /> chrNum\tstart\tend')

    # region field
    REGION_CHOICES = (
        ('E1', "Transcription Elongation"),
        ('E2', "Enhacer (poised)"),
        ('E3', "Enhancer (active)"),
        ('E4', "Enhancer (weak)"),
        ('E5', "Promoter (active)"),
        ('E6', "Promoter (transition)"),
        ('E7', "Promoter (inactive)"),
        ('E8', "Promoter (active OSN)"),
        ('E9', "Enhancer (active OSN)"),
        ('E10', "Enhancer (poised OSN)"),
        ('E11', "CTCF (Insulater)"),
        ('E12', "Bivalent Promoter"),
        ('E13', "Repressed chromatin"),
        ('E14', "Low signal/Repetitive elements"),
        ('E15', "Heterochromatin"),

    )
    region = forms.ChoiceField(choices=REGION_CHOICES, required=True, help_text="Help Text here")

    # pvalue = forms.FloatField(label="P-Value cut off", max_value=1, min_value=0)


    #validating input
    def clean(self):
        cleaned_data = super(InputForm, self).clean()
        signal_File = cleaned_data.get('signal_File')
        if (signal_File is not None) and (not checkSignalFile(signal_File)):
            raise forms.ValidationError({'signal_File': ["Invalid file format.",]})




# Input form for submission from results page
class VariableInputForm(forms.Form):
    """
    The VariableInputForm class is a form for users re-submission.
    A number of fields are required from user to select or upload.
    **selected_signals** - selected signals from the datatables (signals from database chosen for analysis).
    **new_signal_File** - (optional) user's signal file upload field where it can be 1 or more files.
    **cut_off** - a threshold cut off to determine proximal and distal.
    **heatmap** - an option to generate heatmap axis ordering.
            (
                Independent: proximal and distal each separately show clustering.
                Follow prioximal: distal will not cluster and distal heatmap axis ordering will follow proximal heatmap axis ordering.
                Follow distal: proximal will not cluster and proximal heatmap axis ordering will follow distal heatmap axis ordering.
            )
    """
    selected_field = forms.CharField(widget=forms.Textarea(attrs={'readonly':'readonly','rows':6, 'cols':22, 'style':'resize:none;'}))

    # uploaded signal files from user
    USERsignal_CHOICES = ()
    uploaded_signal_File = forms.MultipleChoiceField(choices=USERsignal_CHOICES, required=False)
    new_signal_File = MultiFileField(min_num=0, required=False, label='Upload custom signal file', help_text='File must be in the form of <br /> chrNum\tstart\tend')

    # region field
    REGION_CHOICES = (
        ('E1', "Transcription Elongation"),
        ('E2', "Enhancer (poised)"),
        ('E3', "Enhancer (active)"),
        ('E4', "Enhancer (weak)"),
        ('E5', "Promoter (active)"),
        ('E6', "Promoter (transition)"),
        ('E7', "Promoter (inactive)"),
        ('E8', "Promoter (active OSN)"),
        ('E9', "Enhancer (active OSN)"),
        ('E10', "Enhancer (poised OSN)"),
        ('E11', "CTCF (Insulator)"),
        ('E12', "Bivalent Promoter"),
        ('E13', "Repressed chromatin"),
        ('E14', "Low signal/Repetitive elements"),
        ('E15', "Heterochromatin"),

    )
    region = forms.ChoiceField(choices=REGION_CHOICES, required=True, help_text="Help Text here")

    # pvalue = forms.FloatField(label="P-Value cut off", max_value=1, min_value=0)
