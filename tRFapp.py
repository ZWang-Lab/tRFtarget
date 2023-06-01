#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 21:24:07 2022

@author: hill103

tRFtarget web server back-end main function
  * Using Flask and Bootstrap to construct the python-based website
  * Using Flask-Bootstrap package to implement Bootstrap
  * Using Flask-WTF to conveniently integrate WTForms
"""



from flask import Flask, render_template, request, send_from_directory, redirect, url_for, abort, jsonify
from flask_bootstrap import Bootstrap5
import os
from preprocess import mapping_str2int, mapping_int2str, info_dict, check_options, gene_evidences, mapping_std2id, mapping_id2std
from forms import form_browse_tRF, form_browse_RNA, form_browse_Gene, form_search_tRF, form_search_RNA, form_search_Gene, form_online_Targets, form_advanced_search
from jobs import cache_folder, q, generateNewJobID, addNewJob, checkFASTA, saveFASTA, oneJob, checkEmail, getJobQueueStatus, getJobStatus, report_success, report_failure
from datatables import doSearch, countSearch, doSearchAdv, countSearchAdv, MYSQLDB
from operator import attrgetter
import base64



# --------------------Redis database related ---------------------------------#

from redis_fun import getVariable, incrVariable



# --------------------Flask related ------------------------------------------#
app = Flask(__name__)
app.config.update({'SECRET_KEY': os.environ.get("FLASK_APP_KEY"), 'DEBUG': False, 'SSL_DISABLE': False, 'WTF_CSRF_ENABLED': True})
Bootstrap5(app)

# actually we do not need to connect database on every request since some requests do not need to retrieve database
'''
@app.before_request
# This function will run before every request
def _db_connect():
    # If open an already-open database, will get error 'Connection already opened'
    MYSQLDB.connect(reuse_if_open=True)
'''
def openDatabase():
    MYSQLDB.connect(reuse_if_open=True)

# but we DO need to check whether the database connection is closed before request finish
@app.teardown_request
# This function will run after a request, regardless if an exception occurs or not
def _db_close(exc):
    # Close an already-closed connection will not result in an exception
    if not MYSQLDB.is_closed():
        MYSQLDB.close()


# Extra redirect request for "/favicon.ico"
@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')



# Home page
@app.route('/')
def index():
    return render_template('index.html', n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='home')



# Browse pages
# Browse by tRF
@app.route('/browse_trf', methods=['GET', 'POST'])
def browse_tRF():
    
    form = form_browse_tRF(formdata=request.form)
    
    if request.method == 'GET':
        # set all boolean filled value as true as default does not work
        for s in mapping_str2int['trf_type'].keys():
            attrgetter(s)(form).data = True
        for s in mapping_str2int['trf_source'].keys():
            attrgetter(s)(form).data = True
            
        return render_template('browse_trf.html', form=form, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    # browser button pressed
    if form.validate_on_submit() and request.method == 'POST':

        search_organism = form.search_organism.data
        
        search_trf_type = []
        for s in mapping_str2int['trf_type'].keys():
            if attrgetter(s)(form).data:
                search_trf_type.append(str(mapping_str2int['trf_type'][s]))
        
        search_trf_source = []
        for s in mapping_str2int['trf_source'].keys():
            if attrgetter(s)(form).data:
                search_trf_source.append(str(mapping_str2int['trf_source'][s]))
        
        # redirect to summary tRF page to show the result table
        return redirect(url_for('summary_tRF', organism=search_organism, trf_type=','.join(search_trf_type), trf_source=','.join(search_trf_source)))


# Browse by RNA
@app.route('/browse_rna', methods=['GET', 'POST'])
def browse_RNA():
    
    form = form_browse_RNA(formdata=request.form)
    
    if request.method == 'GET':
        # set all boolean filled value as true as default does not work
        for s in mapping_str2int['rna_type'].keys():
            attrgetter(s)(form).data = True
            
        return render_template('browse_rna.html', form=form, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    # browser button pressed
    if form.validate_on_submit() and request.method == 'POST':
        
        search_organism = form.search_organism.data
        
        search_rna_type = []
        for s in mapping_str2int['rna_type'].keys():
            if attrgetter(s)(form).data:
                search_rna_type.append(str(mapping_str2int['rna_type'][s]))
        
        # redirect to summary RNA page to show the result table
        return redirect(url_for('summary_RNA', organism=search_organism, rna_type=','.join(search_rna_type)))


# Browse by Gene
@app.route('/browse_gene', methods=['GET', 'POST'])
def browse_Gene():
    
    form = form_browse_Gene(formdata=request.form)
    
    if request.method == 'GET':
        return render_template('browse_gene.html', form=form, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    # browser button pressed
    if form.validate_on_submit() and request.method == 'POST':
        
        search_organism = form.search_organism.data
        
        # redirect to summary Gene page to show the result table
        return redirect(url_for('summary_Gene', organism=search_organism))



# Result pages from browse
# Show result of browse by tRF
@app.route('/summary_trf')
def summary_tRF():
    
    # data retrieving count plus 1, by putting it here to also record the hits from direct url accessing
    incrVariable('n_search')
    
    # parse the query arguments
    arg_dict = {'Organism': request.args.get('organism'), 'tRF Type': request.args.get('trf_type'), 'tRF Source':request.args.get('trf_source')}
    
    # check Organism name in case user input invalid Oranism in url access rather than clicking in Browse page
    if arg_dict['Organism'] is None:
        return render_template('summary_trf.html', success=False, for_print='Please specify Organism correctly!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    if not arg_dict['Organism'] in info_dict:
        this_organism = arg_dict['Organism']
        return render_template('summary_trf.html', success=False, for_print=f'Can not find Organism "{this_organism}" in tRFtarget. Please browse again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    # parse argument string into list of ints
    arg_dict['tRF Type'] = check_options('trf_type', arg_dict['tRF Type'])
    arg_dict['tRF Source'] = check_options('trf_source', arg_dict['tRF Source'])
    
    # check empty string (this arg equals empty) or None (url do not have this arg)
    for k, v in arg_dict.items():
        if v is None or len(v)==0:
            return render_template('summary_trf.html', success=False, for_print=f'Please select at least one {k}!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    
    # retrieve from tRF info dataframe
    this_df = info_dict[arg_dict['Organism']]['trf']
    this_df = this_df.loc[(this_df['num_type'].isin(arg_dict['tRF Type'])) & (this_df['num_source'].isin(arg_dict['tRF Source'])), :]
    
    # message printed above the result table
    for_print = f"{this_df.shape[0]:,} <i>{arg_dict['Organism']}</i> tRFs \nwith filters: tRF Type&#8712{{{','.join([mapping_int2str['trf_type'][x] for x in arg_dict['tRF Type']])}}}; tRF Source&#8712{{{','.join([mapping_int2str['trf_source'][x] for x in arg_dict['tRF Source']])}}}"
    
    if this_df.shape[0] == 0:
        return render_template('summary_trf.html', success=False, for_print=for_print, display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    # change dataframe to list of lists for front-end, column order is tRF ID, standardized tRF ID, tRF Type, tRF Source, tRF Sequence, Sequence Length
    # all post-processing are carried out in front-end
    this_df = this_df.loc[:, ['trf_id', 'std_trf_id', 'num_type', 'num_source', 'seq', 'seq_len']]
    return render_template('summary_trf.html', success=True, for_print=for_print, display_table=True, organism=arg_dict['Organism'], data=this_df.values.tolist(), n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')


# Show result of browse by RNA
@app.route('/summary_rna')
def summary_RNA():
    
    # data retrieving count plus 1, by putting it here to also record the hits from direct url accessing
    incrVariable('n_search')
    
    # parse the query arguments
    arg_dict = {'Organism': request.args.get('organism'), 'RNA Type': request.args.get('rna_type')}
    
    # check Organism name in case user input invalid Oranism in url access rather than clicking in Browse page
    if arg_dict['Organism'] is None:
        return render_template('summary_rna.html', success=False, for_print='Please specify Organism correctly!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    if not arg_dict['Organism'] in info_dict:
        this_organism = arg_dict['Organism']
        return render_template('summary_rna.html', success=False, for_print=f'Can not find Organism "{this_organism}" in tRFtarget. Please browse again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    # parse argument string into list of ints
    arg_dict['RNA Type'] = check_options('rna_type', arg_dict['RNA Type'])
    
    # check empty string (this arg equals empty) or None (url do not have this arg)
    for k, v in arg_dict.items():
        if v is None or len(v)==0:
            return render_template('summary_rna.html', success=False, for_print=f'Please select at least one {k}!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    
    # retrieve from RNA info dataframe
    this_df = info_dict[arg_dict['Organism']]['rna']
    this_df = this_df.loc[this_df['num_rna_type'].isin(arg_dict['RNA Type']), :]
    
    # message printed above the result table
    for_print = f"{this_df.shape[0]:,} <i>{arg_dict['Organism']}</i> RNAs \nwith filters: RNA Type&#8712{{{','.join([mapping_int2str['rna_type'][x] for x in arg_dict['RNA Type']])}}}"
    
    if this_df.shape[0] == 0:
        return render_template('summary_rna.html', success=False, for_print=for_print, display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    # change dataframe to list of lists for front-end, column order is RNA ID, RNA Name, RNA Type, Gene ID, Gene Name, Sequence Length
    # all post-processing are carried out in front-end
    this_df = this_df.loc[:, ['rna_id', 'rna_name', 'num_rna_type', 'gene_id', 'gene_name', 'seq_len']]
    return render_template('summary_rna.html', success=True, for_print=for_print, display_table=True, organism=arg_dict['Organism'], data=this_df.values.tolist(), n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')


# Show result of browse by Gene
@app.route('/summary_gene')
def summary_Gene():
    
    # data retrieving count plus 1, by putting it here to also record the hits from direct url accessing
    incrVariable('n_search')
    
    # parse the query arguments
    arg_dict = {'Organism': request.args.get('organism')}
    
    # check Organism name in case user input invalid Oranism in url access rather than clicking in Browse page
    if arg_dict['Organism'] is None:
        return render_template('summary_gene.html', success=False, for_print='Please specify Organism correctly!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')
    
    if not arg_dict['Organism'] in info_dict:
        this_organism = arg_dict['Organism']
        return render_template('summary_gene.html', success=False, for_print=f'Can not find Organism "{this_organism}" in tRFtarget. Please browse again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')

    # message printed above the result table
    for_print = f"{info_dict[arg_dict['Organism']]['browse_gene'].shape[0]:,} <i>{arg_dict['Organism']}</i> Genes"
    
    # it can't be empty dataframe since no filters here
    # change dataframe to list of lists for front-end, column order is Gene ID, Gene Name, Count, RNA Types
    # all post-processing are carried out in front-end
    return render_template('summary_gene.html', success=True, for_print=for_print, display_table=True, organism=arg_dict['Organism'], data=info_dict[arg_dict['Organism']]['browse_gene'].values.tolist(), n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='browse')


# Search pages
# Search by tRF
@app.route('/search_trf', methods=['GET', 'POST'])
def search_tRF():
    
    form = form_search_tRF(formdata=request.form)
    
    if request.method == 'GET':
        # set all boolean filled value as true as default does not work
        for s in mapping_str2int['rna_type'].keys():
            attrgetter(s)(form).data = True
        for s in mapping_str2int['binding_region'].keys():
            if s != '/':
                attrgetter(s)(form).data = True
            
        return render_template('search_trf.html', form=form, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    
    # Search button pressed
    if form.validate_on_submit() and request.method == 'POST':
        
        search_organism = form.search_organism.data
        
        trf_string = form.trf.data
        
        # tRF only has ID no Name
        if (not trf_string in mapping_str2int['trf_id'][search_organism]) and (not trf_string in mapping_std2id[search_organism]):
            # data retrieving count plus 1
            incrVariable('n_search')
            return render_template('show_target.html', success=False, for_print=f'Found 0 <i>{search_organism}</i> tRF in tRFtarget with a ID as "{trf_string}". Please search again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
        
        search_rna_type = []
        for s in mapping_str2int['rna_type'].keys():
            if attrgetter(s)(form).data:
                search_rna_type.append(str(mapping_str2int['rna_type'][s]))
        
        tool = form.search_tool.data
        
        binding_region = []
        for s in mapping_str2int['binding_region'].keys():
            if s != '/':
                if attrgetter(s)(form).data:
                    binding_region.append(str(mapping_str2int['binding_region'][s]))
        # always add 4:/ for lncRNA and rRNA
        if not '4' in binding_region:
            binding_region.append('4')
        
        fe_threshold = str(form.fe_threshold.data)
        mcl_threshold = str(form.mcl_threshold.data)
       
        if form.exp_only.data:
            evidence_only = True
        else:
            evidence_only = False
        
        # redirect to Show Target page to show the result table
        return redirect(url_for('show_Target', trf_id=trf_string, organism=search_organism, tool=tool, rna_type=','.join(search_rna_type), binding_region=','.join(binding_region), fe_threshold=fe_threshold, mcl_threshold=mcl_threshold, evidence_only=evidence_only))


# Search by RNA
@app.route('/search_rna', methods=['GET', 'POST'])
def search_RNA():
    
    form = form_search_RNA(formdata=request.form)
    
    if request.method == 'GET':
        # set all boolean filled value as true as default does not work
        for s in mapping_str2int['trf_type'].keys():
            attrgetter(s)(form).data = True
        for s in mapping_str2int['trf_source'].keys():
            attrgetter(s)(form).data = True
        for s in mapping_str2int['binding_region'].keys():
            if s != '/':
                attrgetter(s)(form).data = True
            
        return render_template('search_rna.html', form=form, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    
    # Search button pressed
    if form.validate_on_submit() and request.method == 'POST':
        
        search_organism = form.search_organism.data
        
        transcript_string = form.transcript.data
        
        # determine it's a ID or Name
        if transcript_string in mapping_str2int['rna_id'][search_organism]:
            search_field = 'rna_id'
        elif transcript_string in mapping_str2int['rna_name'][search_organism]:
            search_field = 'rna_name'
        else:
            # neither ID nor Name
            # data retrieving count plus 1
            incrVariable('n_search')
            return render_template('show_target.html', success=False, for_print=f'Found 0 <i>{search_organism}</i> RNA in tRFtarget with a ID or Name as "{transcript_string}". Please search again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
        
        search_trf_type = []
        for s in mapping_str2int['trf_type'].keys():
            if attrgetter(s)(form).data:
                search_trf_type.append(str(mapping_str2int['trf_type'][s]))
        
        search_trf_source = []
        for s in mapping_str2int['trf_source'].keys():
            if attrgetter(s)(form).data:
                search_trf_source.append(str(mapping_str2int['trf_source'][s]))
        
        tool = form.search_tool.data
        
        binding_region = []
        for s in mapping_str2int['binding_region'].keys():
            if s != '/':
                if attrgetter(s)(form).data:
                    binding_region.append(str(mapping_str2int['binding_region'][s]))
        # always add 4:/ for lncRNA and rRNA
        if not '4' in binding_region:
            binding_region.append('4')
        
        fe_threshold = str(form.fe_threshold.data)
        mcl_threshold = str(form.mcl_threshold.data)
       
        if form.exp_only.data:
            evidence_only = True
        else:
            evidence_only = False
        
        # redirect to Show Target page to show the result table
        return redirect(url_for('show_Target',  **{search_field: transcript_string}, organism=search_organism, tool=tool, trf_type=','.join(search_trf_type), trf_source=','.join(search_trf_source), binding_region=','.join(binding_region), fe_threshold=fe_threshold, mcl_threshold=mcl_threshold, evidence_only=evidence_only))


# Search by Gene
@app.route('/search_gene', methods=['GET', 'POST'])
def search_Gene():
    
    form = form_search_Gene(formdata=request.form)
    
    if request.method == 'GET':
        # set all boolean filled value as true as default does not work
        for s in mapping_str2int['trf_type'].keys():
            attrgetter(s)(form).data = True
        for s in mapping_str2int['trf_source'].keys():
            attrgetter(s)(form).data = True
        for s in mapping_str2int['binding_region'].keys():
            if s != '/':
                attrgetter(s)(form).data = True
            
        return render_template('search_gene.html', form=form, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    
    # Search button pressed
    if form.validate_on_submit() and request.method == 'POST':
        
        search_organism = form.search_organism.data
        
        gene_string = form.gene.data
        
        # determine it's a ID or Name
        if gene_string in mapping_str2int['gene_id'][search_organism]:
            search_field = 'gene_id'
        elif gene_string in mapping_str2int['gene_name'][search_organism]:
            search_field = 'gene_name'
        else:
            # neither ID nor Name
            # data retrieving count plus 1
            incrVariable('n_search')
            return render_template('show_target.html', success=False, for_print=f'Found 0 <i>{search_organism}</i> Gene in tRFtarget with a ID or Name as "{gene_string}". Please search again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
        
        search_trf_type = []
        for s in mapping_str2int['trf_type'].keys():
            if attrgetter(s)(form).data:
                search_trf_type.append(str(mapping_str2int['trf_type'][s]))
        
        search_trf_source = []
        for s in mapping_str2int['trf_source'].keys():
            if attrgetter(s)(form).data:
                search_trf_source.append(str(mapping_str2int['trf_source'][s]))
        
        tool = form.search_tool.data
        
        binding_region = []
        for s in mapping_str2int['binding_region'].keys():
            if s != '/':
                if attrgetter(s)(form).data:
                    binding_region.append(str(mapping_str2int['binding_region'][s]))
        # always add 4:/ for lncRNA and rRNA
        if not '4' in binding_region:
            binding_region.append('4')
        
        fe_threshold = str(form.fe_threshold.data)
        mcl_threshold = str(form.mcl_threshold.data)
       
        if form.exp_only.data:
            evidence_only = True
        else:
            evidence_only = False
        
        # redirect to Show Target page to show the result table
        return redirect(url_for('show_Target',  **{search_field: gene_string}, organism=search_organism, tool=tool, trf_type=','.join(search_trf_type), trf_source=','.join(search_trf_source), binding_region=','.join(binding_region), fe_threshold=fe_threshold, mcl_threshold=mcl_threshold, evidence_only=evidence_only))


# Advanced search page
@app.route('/advanced_search', methods=['GET', 'POST'])
def search_Advanced():
    
    form = form_advanced_search(formdata=request.form)
    
    if request.method == 'GET':
        # set all boolean filled value as true as default does not work
        for s in mapping_str2int['binding_region'].keys():
            if s != '/':
                attrgetter(s)(form).data = True
            
        return render_template('advanced_search.html', form=form, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    
    # Search button pressed
    if form.validate_on_submit() and request.method == 'POST':
        
        search_organism = form.search_organism.data
        
        trf_string = form.trf.data
        # tRF only has ID no Name
        if (not trf_string in mapping_str2int['trf_id'][search_organism]) and (not trf_string in mapping_std2id[search_organism]):
            # data retrieving count plus 1
            incrVariable('n_search')
            return render_template('show_target.html', success=False, for_print=f'Found 0 <i>{search_organism}</i> tRF in tRFtarget with a ID as "{trf_string}". Please search again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
        
        target_string = form.target.data
        # determine search by RNA or gene
        if form.search_target.data == 'RNA':
            # determine it's a RNA ID or Name
            if target_string in mapping_str2int['rna_id'][search_organism]:
                search_field = 'rna_id'
            elif target_string in mapping_str2int['rna_name'][search_organism]:
                search_field = 'rna_name'
            else:
                # neither ID nor Name
                # data retrieving count plus 1
                incrVariable('n_search')
                return render_template('show_target.html', success=False, for_print=f'Found 0 <i>{search_organism}</i> RNA in tRFtarget with a ID or Name as "{target_string}". Please search again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
        
        elif form.search_target.data == 'Gene':
            # determine it's a ID or Name
            if target_string in mapping_str2int['gene_id'][search_organism]:
                search_field = 'gene_id'
            elif target_string in mapping_str2int['gene_name'][search_organism]:
                search_field = 'gene_name'
            else:
                # neither ID nor Name
                # data retrieving count plus 1
                incrVariable('n_search')
                return render_template('show_target.html', success=False, for_print=f'Found 0 <i>{search_organism}</i> Gene in tRFtarget with a ID or Name as "{target_string}". Please search again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
            
        tool = form.search_tool.data
        
        binding_region = []
        for s in mapping_str2int['binding_region'].keys():
            if s != '/':
                if attrgetter(s)(form).data:
                    binding_region.append(str(mapping_str2int['binding_region'][s]))
        # always add 4:/ for lncRNA and rRNA
        if not '4' in binding_region:
            binding_region.append('4')
        
        fe_threshold = str(form.fe_threshold.data)
        mcl_threshold = str(form.mcl_threshold.data)
       
        if form.exp_only.data:
            evidence_only = True
        else:
            evidence_only = False
            
        # redirect to Show Target page to show the result table
        return redirect(url_for('show_Target',  trf_id=trf_string, **{search_field: target_string}, organism=search_organism, tool=tool, binding_region=','.join(binding_region), fe_threshold=fe_threshold, mcl_threshold=mcl_threshold, evidence_only=evidence_only))



# A function to postprocess MySQL database retrieving result
def postprocess(row, organism, tool):
    # note that peewee query result is an iterator
    # here the input is just one row/entry from the iterator
    # the format of row is a tuple, and column order: trf_id, rna_id, rna_name, gene_id, gene_name, demo (binarized), mfe, mcl, trf_type, trf_source, rna_type, area, has_gene_evi, has_site_evi
    # all columns are integers, IDs and Names need to change back to string, other integers will be changed back in front-end
    # note that when post-processing entries in iterator, we still need to keep the database connection open, as the real data is still in database. We need to wait to close database after finishing this post-processing
    # update: add standardized tRF ID, note some tRFs do not have matched standardized ID
    
    output = []
    
    output.append(mapping_int2str['trf_id'][organism][row[0]])
    
    output.append(mapping_id2std[organism].get(output[0], ''))
    
    output.append(mapping_int2str['rna_id'][organism][row[1]])
    
    if row[2] is None:
        output.append('')
    else:
        output.append(mapping_int2str['rna_name'][organism][row[2]])
    
    if row[3] is None:
        output.append('')
    else:
        output.append(mapping_int2str['gene_id'][organism][row[3]])
    
    if row[4] is None:
        output.append('')
    else:
        output.append(mapping_int2str['gene_name'][organism][row[4]])
    
    # update: now this is compressed binarized strings, change it to Base64 coding for transfer
    output.append(base64.b64encode(row[5]).decode())
    
    output.append(row[6])
    output.append(row[7])
    
    # insert the prediction tool
    output.append(tool)
    
    output.append(row[8])
    output.append(row[9])
    output.append(row[10])
    output.append(row[11])
    output.append(row[12])
    output.append(row[13])

    return output



# Page showing database retrieving results
@app.route('/show_target')
def show_Target():
    
    # data retrieving count plus 1, by putting it here to also record the hits from direct url accessing
    incrVariable('n_search')
    
    # parse the query arguments
    arg_dict = request.args.to_dict(flat=True)
    
    for_print_strings = {'organism': 'Organism',
                         'tool': 'Prediction Tool',
                         'rna_type': 'RNA Type',
                         'trf_type': 'tRF Type',
                         'trf_source': 'tRF Source',
                         'binding_region': 'Binding Region',
                         'fe_threshold': 'FE Threshold',
                         'mcl_threshold': 'MCL Threshold',
                         'evidence_only': 'Evidence Only',
                         'trf_id': 'tRF',
                         'rna_id': 'RNA',
                         'rna_name': 'RNA',
                         'gene_id': 'Gene',
                         'gene_name': 'Gene'}
    
    # first determine search way: by tRF, by RNA ID, by RNA Name, by Gene ID, or by Gene Name
    search_ways = []
    if 'trf_id' in arg_dict:
        search_ways.append('trf_id')
    if 'rna_id' in arg_dict:
        search_ways.append('rna_id')
    if 'rna_name' in arg_dict:
        search_ways.append('rna_name')
    if 'gene_id' in arg_dict:
        search_ways.append('gene_id')
    if 'gene_name' in arg_dict:
        search_ways.append('gene_name')
    
    if len(search_ways)==0 or len(search_ways)>=3:
        # no key search field or too many
        return render_template('show_target.html', success=False, for_print='Invalid search way of tRFtarget! Please Search by tRF/RNA/Gene, or use Advanced Search for one tRF and one target RNA/Gene!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    elif len(search_ways) == 2:
        # 2 key search fields should be one tRF and one RNA or Gene
        if not 'trf_id' in search_ways:
            return render_template('show_target.html', success=False, for_print='Invalid search way of tRFtarget! Please Search by tRF/RNA/Gene, or use Advanced Search for one tRF and one target RNA/Gene!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    
    # then check Organism
    if 'organism' not in arg_dict:
        arg_dict['organism'] = 'Homo sapiens'
    
    if not arg_dict['organism'] in info_dict:
        this_organism = arg_dict['organism']
        return render_template('show_target.html', success=False, for_print=f'Can not find Organism "{this_organism}" in tRFtarget. Please search again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    
    # a quick search to make sure search key word has been recorded in tRFtarget, we check it before in search pages, but users may submit query directly from url, so another round of checking here is needed
    id_or_name = {'trf_id': 'ID',
                  'rna_id': 'ID',
                  'rna_name': 'Name',
                  'gene_id': 'Name',
                  'gene_name': 'Name'}
    for search_way in search_ways:
        if (not arg_dict[search_way] in mapping_str2int[search_way][arg_dict['organism']]) and (not arg_dict[search_way] in mapping_std2id[arg_dict['organism']]):
            return render_template('show_target.html', success=False, for_print=f'Found 0 <i>{arg_dict["organism"]}</i> {for_print_strings[search_way]} in tRFtarget with a {id_or_name[search_way]} as "{arg_dict[search_way]}". Please search again!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    
    # then generate the default args for each search way
    if len(search_ways) == 1:
        if search_ways[0] == 'trf_id':
            default_arg_dict = {'organism': 'Homo sapiens', 'tool': 'Consensus', 'rna_type': '1,2,3', 'binding_region': '1,2,3,4', 'fe_threshold': -10, 'mcl_threshold': 6, 'evidence_only': 'False'}
        else:
            default_arg_dict = {'organism': 'Homo sapiens', 'tool': 'Consensus', 'trf_type': '1,3,5,6,7,8,9', 'trf_source': '1,2,3,5', 'binding_region': '1,2,3,4', 'fe_threshold': -10, 'mcl_threshold': 6, 'evidence_only': 'False'}
    else:
        default_arg_dict = {'organism': 'Homo sapiens', 'tool': 'Consensus', 'binding_region': '1,2,3,4', 'fe_threshold': -10, 'mcl_threshold': 6, 'evidence_only': 'False'}
    
    # combine user specified args with default ones
    for k,v in default_arg_dict.items():
        if k not in arg_dict:
            arg_dict[k] = v
            
    # parse argument string into list of ints
    for s in ['trf_type', 'trf_source', 'rna_type', 'binding_region']:
        if s in arg_dict:
            arg_dict[s] = check_options(s, arg_dict[s])
    
    # parse prediction tool
    if arg_dict['tool'].casefold() == 'Consensus'.casefold():
        arg_dict['tool'] = 'Consensus'
    elif arg_dict['tool'].casefold() == 'RNAhybrid'.casefold():
        arg_dict['tool'] = 'RNAhybrid'
    elif arg_dict['tool'].casefold() == 'IntaRNA'.casefold():
        arg_dict['tool'] = 'IntaRNA'
    else:
        arg_dict['tool'] = 'Consensus'
    
    # parse True or False for Evidence Only
    if arg_dict['evidence_only'].casefold() == 'true'.casefold():
        arg_dict['evidence_only'] = True
    elif arg_dict['evidence_only'].casefold() == 'false'.casefold():
        arg_dict['evidence_only'] = False
    else:
        arg_dict['evidence_only'] = False
        
    # parse numbers for thresholds
    try:
        arg_dict['fe_threshold'] = float(arg_dict['fe_threshold'])
    except:
        arg_dict['fe_threshold'] = -10
    
    try:
        arg_dict['mcl_threshold'] = int(float(arg_dict['mcl_threshold']))
    except:
        arg_dict['mcl_threshold'] = 6
        
    # check empty string (this arg equals empty) or None (url do not have this arg)
    for k, v in arg_dict.items():
        if v is None or ((isinstance(v, str) or isinstance(v, list)) and len(v)==0):
            return render_template('show_target.html', success=False, for_print=f'Please select at least one {for_print_strings[k]}!', display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    
    # change the ID or Name to corresponding int
    # also record the original string for print
    org_trf_str = ''
    org_target_str = ''
    for search_way in search_ways:
        if search_way == 'trf_id':
            # whether it's a tRF ID or standardized tRF ID
            org_trf_str = arg_dict[search_way]
            if arg_dict[search_way] in mapping_std2id[arg_dict['organism']]:
                # a standardized tRF ID may map to multiple tRFs
                arg_dict[search_way] = [mapping_str2int[search_way][arg_dict['organism']][x] for x in mapping_std2id[arg_dict['organism']][arg_dict[search_way]].split(',')]
            else:
                arg_dict[search_way] = mapping_str2int[search_way][arg_dict['organism']][arg_dict[search_way]]
        else:
            org_target_str = arg_dict[search_way]
            arg_dict[search_way] = mapping_str2int[search_way][arg_dict['organism']][arg_dict[search_way]]
    
    
    # start to search in database
    openDatabase()
    
    # first to see how many records will be returned
    if len(search_ways) == 1:
        if arg_dict['tool'] == 'Consensus':
            rnahybrid_count, intarna_count = countSearch(arg_dict, search_ways[0])
            total_count = rnahybrid_count + intarna_count
        else:
            total_count = countSearch(arg_dict, search_ways[0])
    else:
        if arg_dict['tool'] == 'Consensus':
            rnahybrid_count, intarna_count = countSearchAdv(arg_dict, search_ways)
            total_count = rnahybrid_count + intarna_count
        else:
            total_count = countSearchAdv(arg_dict, search_ways)
        
    # message printed above the result table
    if len(search_ways) == 1:
        search_way = search_ways[0]
        if search_way == 'trf_id':
            for_print = f'{total_count:,} {arg_dict["tool"]} binding sites for <i>{arg_dict["organism"]}</i> tRF "{org_trf_str}" \nwith filters: RNA Type&#8712{{{",".join([mapping_int2str["rna_type"][x] for x in arg_dict["rna_type"]])}}}; Binding Region&#8712{{{",".join([mapping_int2str["binding_region"][x] for x in arg_dict["binding_region"]])}}}; Free Energy&#8804;{arg_dict["fe_threshold"]}; MCL&#8805;{arg_dict["mcl_threshold"]}; Evidence Only {arg_dict["evidence_only"]}'
        
        elif search_way == 'rna_id' or search_way == 'rna_name':
            for_print = f'{total_count:,} {arg_dict["tool"]} binding sites for <i>{arg_dict["organism"]}</i> RNA "{org_target_str}" \nwith filters: tRF Type&#8712{{{",".join([mapping_int2str["trf_type"][x] for x in arg_dict["trf_type"]])}}}; tRF Source&#8712{{{",".join([mapping_int2str["trf_source"][x] for x in arg_dict["trf_source"]])}}}; Binding Region&#8712{{{",".join([mapping_int2str["binding_region"][x] for x in arg_dict["binding_region"]])}}}; Free Energy&#8804;{arg_dict["fe_threshold"]}; MCL&#8805;{arg_dict["mcl_threshold"]}; Evidence Only {arg_dict["evidence_only"]}'
        
        elif search_way == 'gene_id' or search_way == 'gene_name':
            for_print = f'{total_count:,} {arg_dict["tool"]} binding sites for <i>{arg_dict["organism"]}</i> Gene "{org_target_str}" \nwith filters: tRF Type&#8712{{{",".join([mapping_int2str["trf_type"][x] for x in arg_dict["trf_type"]])}}}; tRF Source&#8712{{{",".join([mapping_int2str["trf_source"][x] for x in arg_dict["trf_source"]])}}}; Binding Region&#8712{{{",".join([mapping_int2str["binding_region"][x] for x in arg_dict["binding_region"]])}}}; Free Energy&#8804;{arg_dict["fe_threshold"]}; MCL&#8805;{arg_dict["mcl_threshold"]}; Evidence Only {arg_dict["evidence_only"]}'
    
    else:
        # determine the 2nd search field
        for s in search_ways:
            if s != 'trf_id':
                search_way = s
                break
        if search_way == 'gene_id' or search_way == 'gene_name':
            this_print_str = 'Gene'
        elif search_way == 'rna_id' or search_way == 'rna_name':
            this_print_str = 'RNA'
        for_print = f'{total_count:,} {arg_dict["tool"]} binding sites for <i>{arg_dict["organism"]}</i> tRF "{org_trf_str}" and {this_print_str} "{org_target_str}" \nwith filters: Binding Region&#8712{{{",".join([mapping_int2str["binding_region"][x] for x in arg_dict["binding_region"]])}}}; Free Energy&#8804;{arg_dict["fe_threshold"]}; MCL&#8805;{arg_dict["mcl_threshold"]}; Evidence Only {arg_dict["evidence_only"]}'
    
    if total_count == 0:
        return render_template('show_target.html', success=False, for_print=for_print, display_table=False, display_pathway=False, organism=arg_dict['organism'], n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    
    # Decide whether show gene enrichment analysis
    display_pathway=False
    if len(search_ways) == 1:
        if search_ways[0] == 'trf_id':
            display_pathway=True

    
    # get search result
    if len(search_ways) == 1:
        if arg_dict['tool'] == 'Consensus':
            rnahybrid_result, intarna_result = doSearch(arg_dict, search_ways[0])
        else:
            result = doSearch(arg_dict, search_ways[0])
    else:
        if arg_dict['tool'] == 'Consensus':
            rnahybrid_result, intarna_result = doSearchAdv(arg_dict, search_ways)
        else:
            result = doSearchAdv(arg_dict, search_ways)
    
    # send result to front-end (0: RNAhybrid; 1:IntaRNA)
    tool_mapping = {'RNAhybrid': 0, 'IntaRNA': 1}
    if arg_dict['tool'] == 'Consensus':
        return render_template('show_target.html', success=True, for_print=for_print, display_table=True, display_pathway=display_pathway, organism=arg_dict['organism'], data=[postprocess(row, arg_dict['organism'], 0) for row in rnahybrid_result.iterator()] + [postprocess(row, arg_dict['organism'], 1) for row in intarna_result.iterator()], n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')
    else:
        return render_template('show_target.html', success=True, for_print=for_print, display_table=True, display_pathway=display_pathway, organism=arg_dict['organism'], data=[postprocess(row, arg_dict['organism'], tool_mapping[arg_dict['tool']]) for row in result.iterator()], n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='search')



# Online Targets page
@app.route('/online_targets', methods=['GET', 'POST'])
def online_Targets():
    
    form = form_online_Targets(formdata=request.form)
    
    if request.method == 'GET':
        # set all boolean filled value as true as default does not work
        return render_template('online_targets.html', form=form, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='online')
    
    # Search button pressed
    if form.validate_on_submit() and request.method == 'POST':
        
        incrVariable('n_online')
        
        # parse the arguments form custom FormData via AJAX using request.form and request.files
        arg_dict = request.form.to_dict(flat=True)
        
        # check tRF sequences
        trf_seq = checkFASTA(request.files['query_content'].read(), arg_dict['query_sha256'])
        if trf_seq is None:
            # 200 OK
            return jsonify({"error_message": "SHA-256 checksum of tRF sequences mismatch. Transmission errors may occur. Please try again."}), 200
        
        # check target RNA sequences
        target_seq = checkFASTA(request.files['target_content'].read(), arg_dict['target_sha256'])
        if target_seq is None:
            # 200 OK
            return jsonify({"error_message": "SHA-256 checksum of target RNA sequences mismatch. Transmission errors may occur. Please try again."}), 200
        
        # checking passed. A valida job submitted
        this_job_id = generateNewJobID()
        addNewJob(this_job_id)
        saveFASTA(trf_seq, this_job_id, 'tRFs.fasta')
        saveFASTA(target_seq, this_job_id, 'targets.fasta')
        # cmd for running tRFtarget-pipeline, in this VM, NO sudo privileges needed
        # note redirect standard output and standard error to the same file, since tqdm redirects progress bar to sys.stderr (https://stackoverflow.com/a/75580782/13752320)
        # The --rm flag removes the container once it's finished running
        cmd = f'docker run --rm -v {os.path.join(cache_folder, this_job_id)}:/data az7jh2/trftarget:0.3.2 tRFtarget -q tRFs.fasta -t targets.fasta -n 50 --e_rnahybrid {arg_dict["e_rnahybrid"]} --e_intarna {arg_dict["e_intarna"]} -b {arg_dict["suboptimal"]} -s {arg_dict["mcl"]} > {os.path.join(cache_folder, this_job_id, "job.log")} 2>&1'
        
        # manually specify this job’s job_id
        # job_timeout: specifies the maximum runtime of the job before it’s interrupted and marked as failed, default 180 s
        # failure_ttl specifies how long (in seconds) failed jobs are kept (defaults to 1 year)
        # ttl specifies the maximum queued time (in seconds) of the job before it’s discarded. This argument defaults to None (infinite TTL)
        q.enqueue(oneJob, args=(this_job_id, cmd, checkEmail(arg_dict['email']), ), job_id=this_job_id, on_success=report_success, on_failure=report_failure, job_timeout='350h', failure_ttl=500)
        
        # if use redirect, the html content will be directly captured by the ajax callback, which is used for handling response. So just return the url, and redirect to the url in frontend
        return jsonify({'url': url_for('get_online_result', job_id=this_job_id)}), 200


# Retrieve one Job status
@app.route('/online_result/<job_id>')
def get_online_result(job_id):
    job_status, message = getJobStatus(job_id)
    return render_template('online_result.html', n_search=getVariable('n_search'), n_online=getVariable('n_online'), job_status=job_status, message=message, job_id=job_id, active_page='online')


# Since the results of online service are stored in a publicly accessible folder (not in Flask static folder), we need to create a new route to to serve file
@app.route('/download/<job_id>')
def download_file(job_id):
    try:
        return send_from_directory(os.path.join(cache_folder, job_id), job_id+".tar.gz", as_attachment=True)
    except FileNotFoundError:
        abort(404)


# A private page to retrieve Job Queue status
@app.route('/job_queue')
def show_queue():
    count_dict = getJobQueueStatus()
    n_total = 0
    for k, v in count_dict.items():
        n_total += v
    return render_template('job_queue.html', n_search=getVariable('n_search'), n_online=getVariable('n_online'), n_total=n_total, count=count_dict, active_page='online')



# Experimental Evidence page
# Site-level evidence


# Gene-level evidence
@app.route('/gene_evidence')
def show_gene_evidence():
    
    # data retrieving count plus 1, by putting it here to also record the hits from direct url accessing
    incrVariable('n_search')
    
    # parse the query arguments
    arg_dict = request.args.to_dict(flat=True)
    
    if len(arg_dict) == 0:
        # show all evidences
        # the column order is 'Gene_Evidence_ID', 'Organism', 'tRF_ID', 'tRF_ID_std', 'tRF_Seq', 'Gene_ID', 'Gene_Name', 'Tissue', 'Direction', 'Technique', 'Title', 'Journal', 'Year', 'PMID', 'tRF_Source'
        return render_template('gene_evidence.html', success=True, for_print=f'{gene_evidences.shape[0]:,} gene-level experimental evidences', display_table=True, data=gene_evidences[['Gene_Evidence_ID', 'Organism', 'tRF_ID', 'tRF_ID_std', 'tRF_Seq', 'Gene_ID', 'Gene_Name', 'Tissue', 'Disease', 'Direction', 'Technique', 'Title', 'Journal', 'Year', 'PMID', 'tRF_Source', 'Cellosaurus_ID']].values.tolist(), n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='evidence')
    
    else:
        # get trf_id, gene_id and organism
        # note for gene-level evidence, we use standardized tRF ID
        query_strings = []
        for_print_parts = []
        
        # check tRF
        if 'trf_id' in arg_dict:
            this_trf = arg_dict['trf_id']
            query_strings.append(f'(tRF_ID_std=="{this_trf}" | tRF_ID=="{this_trf}")')
            for_print_parts.append(f'tRF "{this_trf}"')
        
        # check Gene
        if 'gene_id' in arg_dict:
            this_gene_id = arg_dict['gene_id']
            query_strings.append(f'(Gene_ID=="{this_gene_id}")')
            for_print_parts.append(f'gene "{this_gene_id}"')
        
        if ('gene_name' in arg_dict) and ('gene_id' not in arg_dict):
            this_gene_name = arg_dict['gene_name']
            query_strings.append(f'(Gene_Name=="{this_gene_name}")')
            for_print_parts.append(f'gene "{this_gene_name}"')
        
        # check Organism
        if 'organism' not in arg_dict:
            this_organism = 'Homo sapiens'
        else:
            this_organism = arg_dict['organism']
        
        query_strings.append(f'(Organism=="{this_organism}")')
        
        # filter rows
        for_send = gene_evidences[['Gene_Evidence_ID', 'Organism', 'tRF_ID', 'tRF_ID_std', 'tRF_Seq', 'Gene_ID', 'Gene_Name', 'Tissue', 'Disease', 'Direction', 'Technique', 'Title', 'Journal', 'Year', 'PMID', 'tRF_Source', 'Cellosaurus_ID']].query('&'.join(query_strings))
        
        # combine strings to the message for print
        for_print = f'{for_send.shape[0]:,} gene-level experimental evidences'
        if len(for_print_parts) > 0:
            for_print += f'\nfor <i>{this_organism}</i> '
            for_print += ' and '.join(for_print_parts)
        
        if for_send.shape[0] == 0:
            return render_template('gene_evidence.html', success=False, for_print=for_print, display_table=False, n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='evidence')
        
        else:
            return render_template('gene_evidence.html', success=True, for_print=for_print, display_table=True, data=for_send.values.tolist(), n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='evidence')



# Method page
@app.route('/method')
def method():
    return render_template('method.html', n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='method')



# Statistics page
@app.route('/statistics')
def statistics():
    return render_template('statistics.html', n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='statistics')



# Help page
@app.route('/help')
def helps():
    return render_template('help.html', n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='help')



# Team page
@app.route('/team')
def team():
    return render_template('team.html', n_search=getVariable('n_search'), n_online=getVariable('n_online'), active_page='team')



if __name__ == '__main__':
    # use intenal IP
    app.run(host= '10.0.107.211', port=80)