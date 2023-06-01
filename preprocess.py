#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 25 03:17:02 2022

@author: hill103

this script preprocess the tRF and RNA information gz files and configure the mapping dicts
"""



import pandas as pd
import os
import numpy as np



# organism covered by database, order refers RNAcentral
organism_list = ['Homo sapiens', 'Mus musculus', 'Caenorhabditis elegans', 'Danio rerio', 'Drosophila melanogaster', 'Rattus norvegicus', 'Rhodobacter sphaeroides', 'Schizosaccharomyces pombe', 'Xenopus tropicalis']


# nested mapping dicts
mapping_str2int = {}
mapping_int2str = {}
mapping_std2id = {}
mapping_id2std = {}


# checkboxes defined for tRF type and their mapping ints
# mapping from boolean field names to ints
mapping_str2int['trf_type'] = {'trf_1':1, 'trf_3':3, 'trf_5':5, 'trf_5u':6, 'trf_i':7, 'trf_5half':8, 'trf_3half':9}
# mapping from ints to displayed strings
mapping_int2str['trf_type'] = {1:'tRF-1 / tsRNA', 3:'tRF-3', 5:'tRF-5', 6:"5'U tRF", 7:'i-tRF', 8:"5' tRH / tiR", 9:"3' tRH / tiR"}


# checkboxes defined for tRF source and their mapping ints
# mapping from boolean field names to ints
mapping_str2int['trf_source'] = {'trfdb':1, 'tsrna':2, 'tsrfun':3, 'tsrbase':5, 'tatdb':6, 'mintbase':4, 'trfexp':7, 'oncotrf':8}
# mapping from ints to displayed strings
mapping_int2str['trf_source'] = {1:"tRFdb", 2:"tsRNA study", 3:"tsRFun", 5:"tsRBase", 6:"tatDB", 4:"MINTbase v2.0", 7:"tRFexplorer", 8:"OncotRF"}


# checkboxes defined for RNA type and their mapping ints
# mapping from boolean field names to ints
mapping_str2int['rna_type'] = {'protein_rna':1, 'r_rna':2, 'lnc_rna':3}
# mapping from ints to displayed strings
mapping_int2str['rna_type'] = {1:"protein_coding", 2:"rRNA", 3:"lncRNA"}


# checkboxes defined for Binding Site Region and their mapping ints
# mapping from boolean field names to ints
mapping_str2int['binding_region'] = {'utr3':1, 'cds':2, 'utr5':3, '/':4}
# mapping from ints to displayed strings
mapping_int2str['binding_region'] = {1:"3' UTR", 2:"CDS", 3:"5' UTR", 4:"/"}


# a function to check valid options for 'trf_type', 'trf_source', 'rna_type', 'binding_region'
def check_options(str_field, option_str):
    # str_field is one of 'trf_type', 'trf_source', 'rna_type', 'binding_region'
    # option_str is string from the url which contains the option integers (also may include some invalid strings)
    # option_str can also be empty string (this arg equals empty) or None (url do not have this arg)
    
    if option_str is None:
        return None
    
    output = []
    for one_str in option_str.split(','):
        try:
            this_opt = int(one_str)
            if this_opt in mapping_int2str[str_field]:
                output.append(this_opt)
        except:
            pass
    return output


# generate dataframes for Browse by gene
def add_df_gene(df):
    # input df is the RNA info dataframe of one Organism
    # already exclue entries without gene ID
    # only contains 4 columns: 'rna_id', 'gene_id', 'gene_name', 'num_rna_type'
    # note that groupby will automatically excluded any NaN or NaT values in the grouping key (https://pandas.pydata.org/pandas-docs/stable/user_guide/groupby.html#groupby-missing). So in df missing 'gene_name' has already been changed to empty string
    df.drop_duplicates(inplace=True)
    
    # collapse RNAs from the same gene ID and gene Name, and count the number of transcripts
    count_df = df.groupby(['gene_id', 'gene_name']).size().reset_index(name='count')
   
    # record the detailed RNA type for genes
    type_df = df.groupby(['gene_id', 'gene_name', 'num_rna_type']).size().reset_index(name='count')
    # concatenate RNA type and frequency
    type_df['rna_types'] = type_df['num_rna_type'].astype(int).astype(str) + ':' + type_df['count'].astype(str)
    # collapse RNA types from the same gene ID
    type_df = type_df[['gene_id','gene_name','rna_types']].groupby(['gene_id','gene_name'], as_index = False).agg({'rna_types': ';'.join})
    
    # combine them
    return pd.merge(count_df, type_df, on=['gene_id', 'gene_name'], validate='one_to_one')[['gene_id', 'gene_name', 'count', 'rna_types']]


# generate mapping between integers and strings (tRF IDs etc)
def get_mapping(df):
    # first column is integers, second column is strings
    # return dicts, first one is integer-to-string, second one is string-to-integer
    return df.set_index(df.columns[0])[df.columns[1]].to_dict(), df.set_index(df.columns[1])[df.columns[0]].to_dict()


# read information gz files for all organisms
info_dict = {}

# initialize mappings of ID and Name for all organisms
mapping_int2str['trf_id'] = {}
mapping_str2int['trf_id'] = {}
mapping_int2str['rna_id'] = {}
mapping_str2int['rna_id'] = {}
mapping_int2str['gene_id'] = {}
mapping_str2int['gene_id'] = {}
mapping_int2str['rna_name'] = {}
mapping_str2int['rna_name'] = {}
mapping_int2str['gene_name'] = {}
mapping_str2int['gene_name'] = {}


for this_organism in organism_list:
    
    info_dict[this_organism] = {}
    
    prefix = this_organism.replace(' ', '_')
    
    info_dict[this_organism]['trf'] = pd.read_csv(os.path.join(r'./static/gz', prefix+'_tRF_info.csv.gz'), compression='gzip', usecols=['organism', 'num_id', 'trf_id', 'num_type', 'seq', 'seq_len', 'num_source', 'std_trf_id'])
    
    # Note that gene name can be nan, which will be recognized as missing value by default
    info_dict[this_organism]['rna'] = pd.read_csv(os.path.join(r'./static/gz', prefix+'_targets_info.csv.gz'), compression='gzip', usecols=['organism', 'num_rna_id', 'rna_id', 'num_gene_id', 'gene_id', 'num_rna_name', 'rna_name', 'num_gene_name', 'gene_name', 'seq_len', 'num_rna_type'], keep_default_na=False, na_values='')
    
    # mappings
    mapping_int2str['trf_id'][this_organism], mapping_str2int['trf_id'][this_organism] = get_mapping(info_dict[this_organism]['trf'][['num_id', 'trf_id']].dropna().drop_duplicates())
    mapping_int2str['rna_id'][this_organism], mapping_str2int['rna_id'][this_organism] = get_mapping(info_dict[this_organism]['rna'][['num_rna_id', 'rna_id']].dropna().drop_duplicates())
    mapping_int2str['gene_id'][this_organism], mapping_str2int['gene_id'][this_organism] = get_mapping(info_dict[this_organism]['rna'][['num_gene_id', 'gene_id']].dropna().drop_duplicates())
    mapping_int2str['rna_name'][this_organism], mapping_str2int['rna_name'][this_organism] = get_mapping(info_dict[this_organism]['rna'][['num_rna_name', 'rna_name']].dropna().drop_duplicates())
    mapping_int2str['gene_name'][this_organism], mapping_str2int['gene_name'][this_organism] = get_mapping(info_dict[this_organism]['rna'][['num_gene_name', 'gene_name']].dropna().drop_duplicates())
    
    # mappings for standardized tRF ID
    mapping_id2std[this_organism] = {}
    mapping_std2id[this_organism] = {}
    tmp_df = info_dict[this_organism]['trf'][['trf_id', 'std_trf_id']].dropna().drop_duplicates()
    for i in tmp_df.index:
        mapping_id2std[this_organism][tmp_df.at[i, 'trf_id']] = tmp_df.at[i, 'std_trf_id']
        if tmp_df.at[i, 'std_trf_id'] in mapping_std2id[this_organism]:
            mapping_std2id[this_organism][tmp_df.at[i, 'std_trf_id']] = mapping_std2id[this_organism][tmp_df.at[i, 'std_trf_id']] + ',' + tmp_df.at[i, 'trf_id']
        else:
            mapping_std2id[this_organism][tmp_df.at[i, 'std_trf_id']] = tmp_df.at[i, 'trf_id']
    
    '''
    # save gzipped json files
    # but gzip json file denied by many browsers
    import json
    import gzip
    
    # must specify text mode by 't'
    with open(prefix+'_tRF_IDs.json', 'wt') as f:
        json.dump(sorted(info_dict[this_organism]['trf']['trf_id'].dropna().drop_duplicates().tolist()), f)
    with open(prefix+'_RNA_Names.json', 'wt') as f:
        json.dump(sorted(info_dict[this_organism]['rna']['rna_name'].dropna().drop_duplicates().tolist()), f)
    with open(prefix+'_Gene_Names.json', 'wt') as f:
        json.dump(sorted(info_dict[this_organism]['rna']['gene_name'].dropna().drop_duplicates().tolist()), f)
    '''
    
    # finally replace nan to empty string for HTML pages
    info_dict[this_organism]['rna'][['rna_name','gene_id','gene_name']] = info_dict[this_organism]['rna'][['rna_name','gene_id','gene_name']].fillna('')
    info_dict[this_organism]['trf']['std_trf_id'] = info_dict[this_organism]['trf']['std_trf_id'].fillna('')
    
    # generate dataframes for result from Browse by gene
    # exclue entries without gene ID, or exclude entries with num_gene_id as np.nan
    # change missing 'gene_name' to empty string, otherwise in groupby entries with 'gene_id' but no 'gene_name' will be excluded
    info_dict[this_organism]['browse_gene'] = add_df_gene(info_dict[this_organism]['rna'].loc[info_dict[this_organism]['rna']['num_gene_id'].notnull(), ['rna_id', 'gene_id', 'gene_name', 'num_rna_type']])
    
    
    
# read CSVs for experimental evidences
articles = pd.read_excel(r'./static/csv/Articles.xlsx', usecols=['Article_ID', 'PMID', 'Title', 'Experiment_Level', 'Journal', 'Year'])
# Filter rows where the column 'Experiment_Level' has a value of 'Gene_level' or 'Site_level'
articles = articles[articles['Experiment_Level'].isin(['Gene-level', 'Site-level'])]

# Note that gene name can be nan, which will be recognized as missing value by default
gene_evidences = pd.read_excel(os.path.join(r'./static/csv/Gene_level_evidences.xlsx'), usecols=['Gene_Evidence_ID', 'Organism', 'tRF_ID', 'tRF_ID_std', 'tRF_Seq', 'tRF_Source', 'Gene_ID', 'Gene_Name', 'Article_ID', 'Tissue', 'Disease', 'Cellosaurus_ID', 'Direction', 'Technique', 'Need_Update'], keep_default_na=False, na_values='', dtype={'Need_update': bool})
gene_evidences = gene_evidences.merge(articles, on='Article_ID', how='left', validate='many_to_one')

# use only the first standardized tRF ID
for i in gene_evidences.index:
    if gene_evidences.at[i, 'tRF_ID_std'] is not np.nan:
        gene_evidences.at[i, 'tRF_ID_std'] = gene_evidences.at[i, 'tRF_ID_std'].split(';')[0].strip()

# finally replace nan to empty string for HTML pages
gene_evidences.fillna('', inplace=True)