from django import forms
from django.conf import settings

from multiupload.fields import MultiFileField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit

from .models import Signal_db


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
    selected_field = forms.CharField(
        widget=forms.Textarea(attrs={'readonly':'readonly','rows':6, 'cols':22, 'style':'resize:none;'})
        # label = 'Upload custom signal file <span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" title="hello <br> world"></span>'
    
    )

    # user input signal file
    signal_File = MultiFileField(
        min_num=0, 
        required=False, 
        label = '[Optional] Upload custom signal file <span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" data-original-title="File must be in the form similar to the example file. e.g.chr1_1001\t0.0\t0"></span>'
    )
    
    # region field
    REGION_CHOICES = (
        ("chromHMM", (
            ('E1', "CTCF (Insulator) [0.92%]"),
            ('E2', "Bivalent Promoter [0.79%]"),
            ('E3', "Enhancer (Poised) [3.47%]"),
            ('E4', "Enhancer (Active) [1.72%]"),
            ('E5', "Enhancer (Weak) [0.76%]"),
            ('E6', "Promoter (Transition) [0.67%]"),
            ('E7', "Promoter (Active) [0.99%]"),
            ('E8', "Promoter (Poised) [0.46%]"),
            ('E9', "Transcription Elongation [3.22%]"),
            ('E11', "Repressed Chromatin [6.37%]"),
        )),
        ("Control", (
            ('E10', "Low Signal/Repetitive Elements [40.03%]"),
            ('E12', "Heterochromatin [40.58%]"),
        )),
        ("Additional", (
            ("IRS", "IRS [0.07%]"),
            ("PRS", "PRS [0.28]"),
            ("SUE", "Superenhancer [0.09%]"),
            ("WG", "Whole Genome [100%]")
        ))
    )
    region = forms.ChoiceField(
        choices=REGION_CHOICES, 
        required=True, 
        label = 'Genomic region <span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" data-original-title="Select the genomic regions you wish to investigate"></span>'
    )
    rank_plot = forms.BooleanField(
        required=False,
        label=
            'Plot ranked correlation <span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" data-original-title="Visualise ranked correlation of the input file with other similar type of proteins.\n\n Note: This requires computing correlation against all the files in the database from the same category and thus may take a few more minutes to compute."></span>')
    interest = forms.ChoiceField(
        choices=(),
        # queryset=Signal_db.objects.none(),
        required=False,
        label="Anchor"
    )
    # category = forms.ChoiceField(
    #     choices = (),
    #     required = False
    # )
    

    #validating input
    def clean(self):
        cleaned_data = super(InputForm, self).clean()
        signal_File = cleaned_data.get('signal_File')
        selected_field = cleaned_data.get('selected_field')
        # category = cleaned_data.get('category')
        rank_plot = cleaned_data.get('rank_plot')
        if (signal_File is not None) and (not checkSignalFile(signal_File)):
            raise forms.ValidationError({'signal_File': ["Invalid file format.",]})
        if selected_field is not None: selected_field = selected_field.rstrip().split()
        if (selected_field is None) or (len(selected_field) < 2):
            raise forms.ValidationError({'selected_field': ["You need to select at least 2 signal files from the database to proceed.",]})
        
        # selected_category = Signal_db.objects.filter(fileID__in = selected_field, category = category)
        
        # if (rank_plot) and (len(list(selected_category)) < 1):
        #     raise forms.ValidationError({'category': ["You need at least 1 signal files from the database in this category to plot.",]})

    def __init__(self, *args, **kwargs):
        super(InputForm, self).__init__(*args, **kwargs)
        # self.fields['category'].choices = Signal_db.objects.all().values_list("category","category").distinct()
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                'selected_field',
                'signal_File',
                'region'
            ),
            Fieldset(
                '[Optional] Correlation ranks',
                'rank_plot',
                'interest',
                # 'category'
            ),
            Submit('submit', 'Submit', css_class='button white')
        )



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
    new_signal_File = MultiFileField(
        min_num=0, 
        required=False, 
        label = '[Optional] Upload custom signal file <span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" data-original-title="File must be in the form similar to the example file. e.g.chr1_1001\t0.0\t0"></span>'
    )

    # region field
    # region field
    REGION_CHOICES = (
        ("chromHMM", (
            ('E1', "CTCF (Insulator) [0.92%]"),
            ('E2', "Bivalent Promoter [0.79%]"),
            ('E3', "Enhancer (Poised) [3.47%]"),
            ('E4', "Enhancer (Active) [1.72%]"),
            ('E5', "Enhancer (Weak) [0.76%]"),
            ('E6', "Promoter (Transition) [0.67%]"),
            ('E7', "Promoter (Active) [0.99%]"),
            ('E8', "Promoter (Poised) [0.46%]"),
            ('E9', "Transcription Elongation [3.22%]"),
            ('E11', "Repressed Chromatin [6.37%]"),
        )),
        ("Control", (
            ('E10', "Low Signal/Repetitive Elements [40.03%]"),
            ('E12', "Heterochromatin [40.58%]"),
        )),
        ("Additional", (
            ("IRS", "IRS [0.07%]"),
            ("PRS", "PRS [0.28]"),
            ("SUE", "Superenhancer [0.09%]"),
            ("WG", "Whole Genome [100%]")
        ))
    )
    region = forms.ChoiceField(
        choices=REGION_CHOICES, 
        required=True, 
        label = 'Genomic region <span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" data-original-title="Select the genomic regions you wish to investigate"></span>'
    )

    
    rank_plot = forms.BooleanField(
        required=False,
        label=
            'Plot ranked correlation <span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" data-original-title="Visualise ranked correlation of the input file with other similar type of proteins.\n\n Note: This requires computing correlation against all the files in the database from the same category and thus may take a few more minutes to compute."></span>')
    
    interest = forms.ChoiceField(
        choices=(),
        required=False,
        label="Anchor"
    )
    category = forms.ChoiceField(
        choices = (),
        required = False
    )
    
    # pvalue = forms.FloatField(label="P-Value cut off", max_value=1, min_value=0)

    def __init__(self, *args, **kwargs):
        super(VariableInputForm, self).__init__(*args, **kwargs)
        # self.fields['category'].choices = Signal_db.objects.all().values_list("category","category").distinct()
        # self.fields['interest'].choices = 
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                'selected_field',
                'uploaded_signal_File',
                'new_signal_File',
                'region'
            ),
            Fieldset(
                '[Optional] Correlation ranks',
                'rank_plot',
                'interest',
                # 'category'
            ),
            Submit('submit', 'Submit', css_class='button white')
        )
    
    #validating input
    def clean(self):
        cleaned_data = super(VariableInputForm, self).clean()
        uploaded_signal_File = cleaned_data.get('uploaded_signal_File')
        
        selected_field = cleaned_data.get('selected_field')
        # category = cleaned_data.get('category')
        # rank_plot = cleaned_data.get('rank_plot')
        new_signal_File = cleaned_data.get('new_signal_File')
        
        if (new_signal_File is not None) and (not checkSignalFile(new_signal_File)):
            raise forms.ValidationError({'new_signal_File': ["Invalid file format.",]})
        if selected_field is not None: selected_field = selected_field.rstrip().split()
        if (selected_field is None) or (len(selected_field) < 2):
            raise forms.ValidationError({'selected_field': ["You need to select at least 2 signal files from the database to proceed.",]})
        
        # selected_category = Signal_db.objects.filter(fileID__in = selected_field, category = category)
        
        # if (rank_plot) and (len(list(selected_category)) < 1):
        #     raise forms.ValidationError({'category': ["You need at least 1 signal files from the database in this category to plot.",]})
