#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 02:13:05 2022

@author: hill103

this script defines data tables in MySQL database
"""



import peewee as pw
from operator import attrgetter, and_
from functools import reduce



# number of binding site records displayed in result page
n_result = 5e4


MYSQLDB = pw.MySQLDatabase('trftarget', user='root', password='12345678',
                           host='127.0.0.1', port=3306, autoconnect=False)


# 定义MySQL data types (ref http://docs.peewee-orm.com/en/latest/peewee/models.html?highlight=table%20generation#field-types-table)
class UnTinyIntField(pw.IntegerField):
    # Range 0-255
    field_type = 'TINYINT UNSIGNED'
    
class UnSmallIntField(pw.IntegerField):
    # Range 0-65535
    field_type = 'SMALLINT UNSIGNED'

class UnMediumIntField(pw.IntegerField):
    # Range 0-16777215
    field_type = 'MEDIUMINT UNSIGNED'

class myVarBinaryField(pw.Field):
    # Range 0-1024
    field_type = 'VARBINARY(1024)'


# peewee CharField对应MySQL varchar(255)类型，corresponding to max 255 bytes so 255 chars! max value can up to 65535 bytes (the maximum row size which is shared among all columns)
# Note that if strict SQL mode is not enabled and you assign a value to a CHAR or VARCHAR column that exceeds the column's maximum length, the value is truncated to fit and a warning is generated
class MySQLBaseModel(pw.Model):
    # 定义columns
    trf_id = UnSmallIntField()
    trf_type = UnTinyIntField()
    trf_source = UnTinyIntField()
    rna_id = UnMediumIntField()
    rna_name = UnMediumIntField(null=True)
    rna_type = UnTinyIntField()
    area = UnTinyIntField()
    gene_id = UnMediumIntField(null=True)
    gene_name = UnMediumIntField(null=True)
    mfe = pw.FloatField()
    mcl = UnTinyIntField()
    # update: now we compress the string of interaction illustration
    # demo = pw.CharField(max_length=2048)
    demo_bin = myVarBinaryField()
    consensus = UnTinyIntField()
    gene_evi = pw.CharField(max_length=1024, null=True)
    site_evi = pw.CharField(max_length=1024, null=True)
    has_gene_evi = UnTinyIntField()
    has_site_evi = UnTinyIntField()
    
    # 所用数据库为MYSQLDB
    class Meta:
        database = MYSQLDB # MYSQLDB为所定义的数据库变量


# 定义数据库中的表格模型
class mus_musculus_rnahybrid(MySQLBaseModel):
    pass

class mus_musculus_intarna(MySQLBaseModel):
    pass

class drosophila_melanogaster_rnahybrid(MySQLBaseModel):
    pass

class drosophila_melanogaster_intarna(MySQLBaseModel):
    pass

class danio_rerio_rnahybrid(MySQLBaseModel):
    pass

class danio_rerio_intarna(MySQLBaseModel):
    pass

class caenorhabditis_elegans_rnahybrid(MySQLBaseModel):
    pass

class caenorhabditis_elegans_intarna(MySQLBaseModel):
    pass

class xenopus_tropicalis_rnahybrid(MySQLBaseModel):
    pass

class xenopus_tropicalis_intarna(MySQLBaseModel):
    pass

class rhodobacter_sphaeroides_rnahybrid(MySQLBaseModel):
    pass

class rhodobacter_sphaeroides_intarna(MySQLBaseModel):
    pass

class schizosaccharomyces_pombe_rnahybrid(MySQLBaseModel):
    pass

class schizosaccharomyces_pombe_intarna(MySQLBaseModel):
    pass

class rattus_norvegicus_rnahybrid(MySQLBaseModel):
    pass

class rattus_norvegicus_intarna(MySQLBaseModel):
    pass

class homo_sapiens_rnahybrid(MySQLBaseModel):
    pass

class homo_sapiens_intarna(MySQLBaseModel):
    pass


# define the nested dict of data tables for using in main function
datatable_dict = {'Mus musculus': {'RNAhybrid': mus_musculus_rnahybrid, 'IntaRNA': mus_musculus_intarna},
                  'Drosophila melanogaster': {'RNAhybrid': drosophila_melanogaster_rnahybrid, 'IntaRNA': drosophila_melanogaster_intarna},
                  'Danio rerio': {'RNAhybrid': danio_rerio_rnahybrid, 'IntaRNA': danio_rerio_intarna},
                  'Caenorhabditis elegans': {'RNAhybrid': caenorhabditis_elegans_rnahybrid, 'IntaRNA': caenorhabditis_elegans_intarna},
                  'Xenopus tropicalis': {'RNAhybrid': xenopus_tropicalis_rnahybrid, 'IntaRNA': xenopus_tropicalis_intarna},
                  'Rhodobacter sphaeroides': {'RNAhybrid': rhodobacter_sphaeroides_rnahybrid, 'IntaRNA': rhodobacter_sphaeroides_intarna},
                  'Schizosaccharomyces pombe': {'RNAhybrid': schizosaccharomyces_pombe_rnahybrid, 'IntaRNA': schizosaccharomyces_pombe_intarna},
                  'Rattus norvegicus': {'RNAhybrid': rattus_norvegicus_rnahybrid, 'IntaRNA': rattus_norvegicus_intarna},
                  'Homo sapiens': {'RNAhybrid': homo_sapiens_rnahybrid, 'IntaRNA': homo_sapiens_intarna}}


# peewee query returns an iterator
# For simple queries you can see further speed improvements by returning rows as dictionaries, namedtuples or tuples.
# Don’t forget to append the iterator() method call to also reduce memory consumption
def doBasicSearch(arg_dict, search_way, tool, num, add_consensus, count_only=False):
    '''generate peewee commands to perform MysQL database search
    search_way is one of 'trf_id', 'rna_id', 'rna_name', 'gene_id', 'gene_name'
    tool is either 'RNAhybrid' or 'IntaRNA'
    num is decided in outter function, for Consensus predictions, return num/2 RNAhybrid + num/2 IntaRNA predictions
    note search item for trf_id is a list or int
    '''
    
    table = datatable_dict[arg_dict['organism']][tool]
    
    clauses = []
    
    # add search conditions based on the order of table index
    if search_way == 'trf_id':
        if isinstance(arg_dict['trf_id'], list):
            if len(arg_dict['trf_id']) > 1:
                clauses.append(table.trf_id.in_(arg_dict['trf_id']))
            else:
                clauses.append(table.trf_id == arg_dict['trf_id'])
        else:
            clauses.append(table.trf_id == arg_dict['trf_id'])
    else:
        clauses.append(attrgetter(search_way)(table) == arg_dict[search_way])
    
    clauses.append(table.mfe <= arg_dict['fe_threshold'])
    clauses.append(table.mcl >= arg_dict['mcl_threshold'])
    
    if add_consensus:
        clauses.append(table.consensus == 1)
    else:
        clauses.append(table.consensus <= 1)
    
    # different filtering for different search way
    if search_way == 'trf_id':
        clauses.append(table.rna_type.in_(arg_dict['rna_type']))
    else:
        clauses.append(table.trf_type.in_(arg_dict['trf_type']))
        clauses.append(table.trf_source.in_(arg_dict['trf_source']))
        
    clauses.append(table.area.in_(arg_dict['binding_region']))
    
    if arg_dict['evidence_only']:
        clauses.append((table.has_gene_evi == 1) | (table.has_site_evi == 1))
    
    
    if count_only:
        # just count the number of retrieved entries
        return (table.select()
                     .where(reduce(and_, clauses))
                     .order_by(table.mfe, table.mcl.desc())
                     .limit(num)
                     .count()
               )
    else:
        return (table.select(table.trf_id,
                             table.rna_id,
                             table.rna_name,
                             table.gene_id,
                             table.gene_name,
                             table.demo_bin,
                             table.mfe,
                             table.mcl,
                             table.trf_type,
                             table.trf_source,
                             table.rna_type,
                             table.area,
                             table.has_gene_evi,
                             table.has_site_evi)
                     .where(reduce(and_, clauses))
                     .order_by(table.mfe, table.mcl.desc())
                     .limit(num)
                     .tuples()
               )


def doSearch(arg_dict, search_way):
    '''considering Consensus predictions, call doBasicSearch function to perform search
    '''
    
    if arg_dict['tool'] == 'Consensus':
        return (doBasicSearch(arg_dict, search_way, 'RNAhybrid', int(n_result/2), True),
                doBasicSearch(arg_dict, search_way, 'IntaRNA', int(n_result/2), True))
    else:
        return doBasicSearch(arg_dict, search_way, arg_dict['tool'], int(n_result), False)
    
    
    
# since count elements in a iterator will consume it, we need another query to get the count
def countSearch(arg_dict, search_way):
    '''considering Consensus predictions, call doBasicSearch function to perform search
    '''
    
    if arg_dict['tool'] == 'Consensus':
        return (doBasicSearch(arg_dict, search_way, 'RNAhybrid', int(n_result/2), True, True),
                doBasicSearch(arg_dict, search_way, 'IntaRNA', int(n_result/2), True, True))
    else:
        return doBasicSearch(arg_dict, search_way, arg_dict['tool'], int(n_result), False, True)



# addtional functions for Advanced Search
def doBasicSearchAdv(arg_dict, search_ways, tool, num, add_consensus, count_only=False):
    '''generate peewee commands to perform MysQL database search
    search_ways is two fields from 'trf_id', 'rna_id', 'rna_name', 'gene_id', 'gene_name'
    tool is either 'RNAhybrid' or 'IntaRNA'
    num is decided in outter function, for Consensus predictions, return num/2 RNAhybrid + num/2 IntaRNA predictions
    '''
    
    table = datatable_dict[arg_dict['organism']][tool]
    
    # determine the 2nd search field
    for s in search_ways:
        if s != 'trf_id':
            search_way = s
            break
    
    clauses = []
    
    # add search conditions based on the order of table index
    # note we use the index for RNA or Gene, and add trf_id to the last one in conditions
    clauses.append(attrgetter(search_way)(table) == arg_dict[search_way])
    clauses.append(table.mfe <= arg_dict['fe_threshold'])
    clauses.append(table.mcl >= arg_dict['mcl_threshold'])
    
    if add_consensus:
        clauses.append(table.consensus == 1)
    else:
        clauses.append(table.consensus <= 1)

    clauses.append(table.area.in_(arg_dict['binding_region']))
    
    if arg_dict['evidence_only']:
        clauses.append((table.has_gene_evi == 1) | (table.has_site_evi == 1))
    
    if isinstance(arg_dict['trf_id'], list):
        if len(arg_dict['trf_id']) > 1:
            clauses.append(table.trf_id.in_(arg_dict['trf_id']))
        else:
            clauses.append(table.trf_id == arg_dict['trf_id'])
    else:
        clauses.append(table.trf_id == arg_dict['trf_id'])
    
    
    if count_only:
        # just count the number of retrieved entries
        return (table.select()
                     .where(reduce(and_, clauses))
                     .order_by(table.mfe, table.mcl.desc())
                     .limit(num)
                     .count()
               )
    else:
        return (table.select(table.trf_id,
                             table.rna_id,
                             table.rna_name,
                             table.gene_id,
                             table.gene_name,
                             table.demo_bin,
                             table.mfe,
                             table.mcl,
                             table.trf_type,
                             table.trf_source,
                             table.rna_type,
                             table.area,
                             table.has_gene_evi,
                             table.has_site_evi)
                     .where(reduce(and_, clauses))
                     .order_by(table.mfe, table.mcl.desc())
                     .limit(num)
                     .tuples()
               )
    
    
def doSearchAdv(arg_dict, search_ways):
    '''considering Consensus predictions, call doBasicSearchAdv function to perform search
    '''
    
    if arg_dict['tool'] == 'Consensus':
        return (doBasicSearchAdv(arg_dict, search_ways, 'RNAhybrid', int(n_result/2), True),
                doBasicSearchAdv(arg_dict, search_ways, 'IntaRNA', int(n_result/2), True))
    else:
        return doBasicSearchAdv(arg_dict, search_ways, arg_dict['tool'], int(n_result), False)


def countSearchAdv(arg_dict, search_ways):
    '''considering Consensus predictions, call doBasicSearch function to perform search
    '''
    
    if arg_dict['tool'] == 'Consensus':
        return (doBasicSearchAdv(arg_dict, search_ways, 'RNAhybrid', int(n_result/2), True, True),
                doBasicSearchAdv(arg_dict, search_ways, 'IntaRNA', int(n_result/2), True, True))
    else:
        return doBasicSearchAdv(arg_dict, search_ways, arg_dict['tool'], int(n_result), False, True)