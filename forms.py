#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 04:24:44 2022

@author: hill103

this script defines forms used in search and browse page
"""



from preprocess import organism_list
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, RadioField, StringField, BooleanField, TextAreaField
from wtforms.validators import InputRequired

# flask_wtf.file.FileField (https://flask-wtf.readthedocs.io/en/1.0.x/form/#file-uploads) differs from wtforms.fields.FileField(https://wtforms.readthedocs.io/en/3.0.x/fields/#wtforms.fields.FileField)
# flask Uploading Files instructions https://flask.palletsprojects.com/en/2.2.x/patterns/fileuploads/
# Dropzone can handles the file upload process itself, so no need to set up a Flask-WTF form specifically for file uploads
# from flask_wtf.file import FileField, FileRequired
# remember the principle called “never trust user input”, always use this function to secure a filename before storing it directly on the filesystem
# from werkzeug.utils import secure_filename



class form_browse_tRF(FlaskForm):
    '''forms used in Browse by tRF page
    '''
    
    # a select form for organism
    search_organism = SelectField('Organism',
                                  choices=[[x, x] for x in organism_list],
                                  validators=[InputRequired()],
                                  default=organism_list[0])
    
    # multiple checkbox for tRF type
    trf_1 = BooleanField("tRF-1 / tsRNA", default=True, false_values=('False', 'false', ''))
    trf_3 = BooleanField("tRF-3", default=True, false_values=('False', 'false', ''))
    trf_5 = BooleanField("tRF-5", default=True, false_values=('False', 'false', ''))
    trf_5u = BooleanField("5'U tRF", default=True, false_values=('False', 'false', ''))
    trf_i = BooleanField("i-tRF", default=True, false_values=('False', 'false', ''))
    trf_5half = BooleanField("5' tRH / tiR", default=True, false_values=('False', 'false', ''))
    trf_3half = BooleanField("3' tRH / tiR", default=True, false_values=('False', 'false', ''))
    
    # multiple checkbox for tRF source
    trfdb = BooleanField("tRFdb", default=True, false_values=('False', 'false', ''))
    tsrna = BooleanField("tsRNA study", default=True, false_values=('False', 'false', ''))
    tsrfun = BooleanField("tsRFun", default=True, false_values=('False', 'false', ''))
    tsrbase = BooleanField("tsRBase", default=True, false_values=('False', 'false', ''))
    tatdb = BooleanField("tatDB", default=True, false_values=('False', 'false', ''))
    mintbase = BooleanField("MINTbase v2.0", default=True, false_values=('False', 'false', ''))
    trfexp = BooleanField("tRFexplorer", default=True, false_values=('False', 'false', ''))
    oncotrf = BooleanField("OncotRF", default=True, false_values=('False', 'false', ''))
    
    # a button to submit request
    submit = SubmitField('Browse')
    
    
class form_browse_RNA(FlaskForm):
    '''forms used in Browse by RNA page
    '''
    
    # a select form for organism
    search_organism = SelectField('Organism',
                                  choices=[[x, x] for x in organism_list],
                                  validators=[InputRequired()],
                                  default=organism_list[0])
    
    # multiple checkbox for RNA type
    protein_rna = BooleanField("protein_coding", default=True, false_values=('False', 'false', ''))
    r_rna = BooleanField("rRNA", default=True, false_values=('False', 'false', ''))
    lnc_rna = BooleanField("lncRNA", default=True, false_values=('False', 'false', ''))
    
    # a button to submit request
    submit = SubmitField('Browse')


class form_browse_Gene(FlaskForm):
    '''forms used in Browse by Gene page
    '''
    
    # a select form for organism
    search_organism = SelectField('Organism',
                                  choices=[[x, x] for x in organism_list],
                                  validators=[InputRequired()],
                                  default=organism_list[0])
    
    # a button to submit request
    submit = SubmitField('Browse')


class form_search_tRF(FlaskForm):
    '''forms used in Search by tRF page
    '''
    
    # a select form for organism
    search_organism = SelectField('Organism',
                                  choices=[[x, x] for x in organism_list],
                                  validators=[InputRequired()],
                                  default=organism_list[0])
    
    # a radio form for prediction tool
    search_tool = RadioField('Prediction Tools',
                              choices=[('RNAhybrid', 'RNAhybrid'),
                                       ('IntaRNA', 'IntaRNA'),
                                       ('Consensus', 'Consensus Only')],
                              validators=[InputRequired()],
                              default='Consensus')
    
    # a text form for RNA ID
    # empty checking already conducted in front-end, BTW empty input can also be handled
    trf = StringField()
    
    # multiple checkbox for RNA type
    protein_rna = BooleanField("protein_coding", default=True, false_values=('False', 'false', ''))
    r_rna = BooleanField("rRNA", default=True, false_values=('False', 'false', ''))
    lnc_rna = BooleanField("lncRNA", default=True, false_values=('False', 'false', ''))
    
    # multiple checkbox for binding region 
    utr5 = BooleanField("5' UTR", default=True, false_values=('False', 'false', ''))
    cds = BooleanField("CDS", default=True, false_values=('False', 'false', ''))
    utr3 = BooleanField("3' UTR", default=True, false_values=('False', 'false', ''))
    
    # a checkbox for whether restrict to binding sites with experimental evidence only
    exp_only = BooleanField("Only show binding sites with Experimental Evidence", default=False, false_values=('False', 'false', ''))
    
    # a text form for threshold of free energy
    fe_threshold = StringField(default=-10)
    
    # a text form for threshold of MCL
    mcl_threshold = StringField(default=6)
    
    # a button to submit request
    submit = SubmitField('Search')
    
    
class form_search_RNA(FlaskForm):
    '''forms used in Search by RNA page
    '''
    
    # a select form for organism
    search_organism = SelectField('Organism',
                                  choices=[[x, x] for x in organism_list],
                                  validators=[InputRequired()],
                                  default=organism_list[0])
    
    # a radio form for prediction tool
    search_tool = RadioField('Prediction Tools',
                              choices=[('RNAhybrid', 'RNAhybrid'),
                                       ('IntaRNA', 'IntaRNA'),
                                       ('Consensus', 'Consensus Only')],
                              validators=[InputRequired()],
                              default='Consensus')
    
    # a text form for RNA ID
    # empty checking already conducted in front-end, BTW empty input can also be handled
    transcript = StringField()
    
    # multiple checkbox for tRF type
    trf_1 = BooleanField("tRF-1 / tsRNA", default=True, false_values=('False', 'false', ''))
    trf_3 = BooleanField("tRF-3", default=True, false_values=('False', 'false', ''))
    trf_5 = BooleanField("tRF-5", default=True, false_values=('False', 'false', ''))
    trf_5u = BooleanField("5'U tRF", default=True, false_values=('False', 'false', ''))
    trf_i = BooleanField("i-tRF", default=True, false_values=('False', 'false', ''))
    trf_5half = BooleanField("5' tRH / tiR", default=True, false_values=('False', 'false', ''))
    trf_3half = BooleanField("3' tRH / tiR", default=True, false_values=('False', 'false', ''))
    
    # multiple checkbox for tRF source
    trfdb = BooleanField("tRFdb", default=True, false_values=('False', 'false', ''))
    tsrna = BooleanField("tsRNA study", default=True, false_values=('False', 'false', ''))
    tsrfun = BooleanField("tsRFun", default=True, false_values=('False', 'false', ''))
    tsrbase = BooleanField("tsRBase", default=True, false_values=('False', 'false', ''))
    tatdb = BooleanField("tatDB", default=True, false_values=('False', 'false', ''))
    mintbase = BooleanField("MINTbase v2.0", default=True, false_values=('False', 'false', ''))
    trfexp = BooleanField("tRFexplorer", default=True, false_values=('False', 'false', ''))
    oncotrf = BooleanField("OncotRF", default=True, false_values=('False', 'false', ''))
    
    # multiple checkbox for binding region 
    utr5 = BooleanField("5' UTR", default=True, false_values=('False', 'false', ''))
    cds = BooleanField("CDS", default=True, false_values=('False', 'false', ''))
    utr3 = BooleanField("3' UTR", default=True, false_values=('False', 'false', ''))
    
    # a checkbox for whether restrict to binding sites with experimental evidence only
    exp_only = BooleanField("Only show binding sites with Experimental Evidence", default=False, false_values=('False', 'false', ''))
    
    # a text form for threshold of free energy
    fe_threshold = StringField(default=-10)
    
    # a text form for threshold of MCL
    mcl_threshold = StringField(default=6)
    
    # a button to submit request
    submit = SubmitField('Search')


class form_search_Gene(FlaskForm):
    '''forms used in Search by Gene page
    '''
    
    # a select form for organism
    search_organism = SelectField('Organism',
                                  choices=[[x, x] for x in organism_list],
                                  validators=[InputRequired()],
                                  default=organism_list[0])
    
    # a radio form for prediction tool
    search_tool = RadioField('Prediction Tools',
                              choices=[('RNAhybrid', 'RNAhybrid'),
                                       ('IntaRNA', 'IntaRNA'),
                                       ('Consensus', 'Consensus Only')],
                              validators=[InputRequired()],
                              default='Consensus')
    
    # a text form for Gene ID
    # empty checking already conducted in front-end, BTW empty input can also be handled
    gene = StringField()
    
    # multiple checkbox for tRF type
    trf_1 = BooleanField("tRF-1 / tsRNA", default=True, false_values=('False', 'false', ''))
    trf_3 = BooleanField("tRF-3", default=True, false_values=('False', 'false', ''))
    trf_5 = BooleanField("tRF-5", default=True, false_values=('False', 'false', ''))
    trf_5u = BooleanField("5'U tRF", default=True, false_values=('False', 'false', ''))
    trf_i = BooleanField("i-tRF", default=True, false_values=('False', 'false', ''))
    trf_5half = BooleanField("5' tRH / tiR", default=True, false_values=('False', 'false', ''))
    trf_3half = BooleanField("3' tRH / tiR", default=True, false_values=('False', 'false', ''))
    
    # multiple checkbox for tRF source
    trfdb = BooleanField("tRFdb", default=True, false_values=('False', 'false', ''))
    tsrna = BooleanField("tsRNA study", default=True, false_values=('False', 'false', ''))
    tsrfun = BooleanField("tsRFun", default=True, false_values=('False', 'false', ''))
    tsrbase = BooleanField("tsRBase", default=True, false_values=('False', 'false', ''))
    tatdb = BooleanField("tatDB", default=True, false_values=('False', 'false', ''))
    mintbase = BooleanField("MINTbase v2.0", default=True, false_values=('False', 'false', ''))
    trfexp = BooleanField("tRFexplorer", default=True, false_values=('False', 'false', ''))
    oncotrf = BooleanField("OncotRF", default=True, false_values=('False', 'false', ''))
    
    # multiple checkbox for binding region 
    utr5 = BooleanField("5' UTR", default=True, false_values=('False', 'false', ''))
    cds = BooleanField("CDS", default=True, false_values=('False', 'false', ''))
    utr3 = BooleanField("3' UTR", default=True, false_values=('False', 'false', ''))
    
    # a checkbox for whether restrict to binding sites with experimental evidence only
    exp_only = BooleanField("Only show binding sites with Experimental Evidence", default=False, false_values=('False', 'false', ''))
    
    # a text form for threshold of free energy
    fe_threshold = StringField(default=-10)
    
    # a text form for threshold of MCL
    mcl_threshold = StringField(default=6)
    
    # a button to submit request
    submit = SubmitField('Search')


class form_online_Targets(FlaskForm):
    '''forms used in online Targets page
    note here we DO NOT need validators
    '''
    # a radio form for switch paste and upload for query small RNA sequences
    query_switch = RadioField('query RNA',
                              choices=[('paste', 'Paste'),
                                       ('upload', 'Upload')],
                              default='paste')
    # a radio form for switch paste and upload for target long RNA sequences
    target_switch = RadioField('target RNA',
                              choices=[('paste', 'Paste'),
                                       ('upload', 'Upload')],
                              default='paste')
    # text-area field rather than string field for query small RNA sequences
    query_input = TextAreaField()
    # text-area field rather than string field for target long RNA sequences
    target_input = TextAreaField()
    # options for tRFtarget-pipeline
    # free energy threshold for RNAhybrid
    e_rnahybrid = StringField(default=-15)
    # free energy threshold for IntaRNA
    e_intarna = StringField(default=0)
    # reported number of interaction sites on each target RNA
    suboptimal = StringField(default=1)
    # MCL threshold
    mcl = StringField(default=6)
    # email adress
    email = StringField()
    # a button to submit request
    submit = SubmitField('Start')
    
    
class form_advanced_search(FlaskForm):
    '''forms used in advanced search page
    '''
    # a select form for organism
    search_organism = SelectField('Organism',
                                  choices=[[x, x] for x in organism_list],
                                  validators=[InputRequired()],
                                  default=organism_list[0])
    
    # a radio form for prediction tool
    search_tool = RadioField('Prediction Tools',
                              choices=[('RNAhybrid', 'RNAhybrid'),
                                       ('IntaRNA', 'IntaRNA'),
                                       ('Consensus', 'Consensus Only')],
                              validators=[InputRequired()],
                              default='Consensus')
    
    # a select form for switching RNA and gene
    search_target = SelectField('Search Target',
                               choices=[('RNA', 'RNA'),
                                        ('Gene', 'Gene')],
                               validators=[InputRequired()],
                               default='RNA')
    
    # a text form for RNA ID or Gene ID
    # empty checking already conducted in front-end, BTW empty input can also be handled
    target = StringField()
    
    # a text form for RNA ID
    # empty checking already conducted in front-end, BTW empty input can also be handled
    trf = StringField()
    
    # multiple checkbox for binding region 
    utr5 = BooleanField("5' UTR", default=True, false_values=('False', 'false', ''))
    cds = BooleanField("CDS", default=True, false_values=('False', 'false', ''))
    utr3 = BooleanField("3' UTR", default=True, false_values=('False', 'false', ''))
    
    # a checkbox for whether restrict to binding sites with experimental evidence only
    exp_only = BooleanField("Only show binding sites with Experimental Evidence", default=False, false_values=('False', 'false', ''))
    
    # a text form for threshold of free energy
    fe_threshold = StringField(default=-10)
    
    # a text form for threshold of MCL
    mcl_threshold = StringField(default=6)
    
    # a button to submit request
    submit = SubmitField('Search')