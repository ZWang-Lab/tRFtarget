# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 22:13:00 2019

@author: hill103
"""

'''
Using Flask and Bootstrap to construct the python-based website
Using Flask-Bootstrap package to implement Bootstrap
Using Flask-WTF to conveniently integrate WTForms
Version 3: 使用MySQL数据库
'''


from flask import Flask, render_template, request, send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, RadioField, StringField, BooleanField
from wtforms.validators import DataRequired
import peewee as pw
import json
import os
import pandas as pd


#####################数据库相关##################################################
# 数据库名称定义为全局变量
global MYSQLDB
MYSQLDB = pw.MySQLDatabase('trftarget', user='root', password='12345678',
                           host='127.0.0.1', port=3306, autoconnect=False)

# 定义MySQL data types
class UnTinyIntField(pw.IntegerField):
    # Range 0-255
    field_type = 'TINYINT UNSIGNED'

class UnMediumIntField(pw.IntegerField):
    # Range 0-16777215
    field_type = 'MEDIUMINT UNSIGNED'

class MediumTextField(pw.TextField):
    # Range 16,777,215 characters - 16 MB
    field_type = 'MEDIUMTEXT'
    
# peewee FixedCharField对应MySQL char类型，长度范围0-255，可设置max_length参数
# peewee CharField对应MySQL varchar类型，长度范围0-65535
# peewee TextField对应MySQL text类型，长度范围65,535 characters - 64 KB
# 更长字符串需要用text类型
class MYSQLBaseModel(pw.Model):
    # 定义columns
    # 注意RNAhybrid表格中还存在p value列
    # 注意：所有ENST和ENSG_ID都统一成长度20(尽管Human不是)
    # 只要不是新建tables，与原来的table structure有差别也没问题
    tRF_ID = pw.FixedCharField(max_length=32)
    ENST_ID = pw.FixedCharField(max_length=20)
    MFE = pw.FloatField()
    Max_Hit_Len = UnTinyIntField()
    Area = pw.FixedCharField(max_length=4)
    Demo = pw.TextField()
    ENSG_ID = pw.FixedCharField(max_length=20)
    Gene_Symbol = pw.CharField(null=True)
    Trans_Type = pw.CharField(null=True)
    Trans_Name = pw.CharField(null=True)
    # 改动的columns
    Start_Target = UnMediumIntField()
    End_Target = UnMediumIntField()
    Start_tRF = UnTinyIntField()
    End_tRF = UnTinyIntField()
    SubseqDP = pw.CharField()
    HybridDP = pw.CharField()
    Max_Hit_DP = pw.CharField()
    # 新增的columns
    Tool = pw.FixedCharField(max_length=20)
    Gene_Evi = pw.CharField(null=True, max_length=8192)
    Site_Evi = pw.CharField(null=True, max_length=8192)
    
    # 所用数据库为MYSQLDB
    class Meta:
        database = MYSQLDB # MYSQLDB为所定义的数据库变量

# 定义数据库中的表格模型
# 1.Human
class tRF_Binding_RNAhybrid(MYSQLBaseModel):
    pass

class tRF_Binding_IntaRNA(MYSQLBaseModel):
    pass

class tRF_Binding_Consensus(MYSQLBaseModel):
    pass

# 2.Mouse
class Mouse_tRF_Binding_RNAhybrid(MYSQLBaseModel):
    pass

class Mouse_tRF_Binding_IntaRNA(MYSQLBaseModel):
    pass

class Mouse_tRF_Binding_Consensus(MYSQLBaseModel):
    pass

# 3.Drosophila
class Drosophila_tRF_Binding_RNAhybrid(MYSQLBaseModel):
    pass

class Drosophila_tRF_Binding_IntaRNA(MYSQLBaseModel):
    pass

class Drosophila_tRF_Binding_Consensus(MYSQLBaseModel):
    pass

# 4.Elegans
class Elegans_tRF_Binding_RNAhybrid(MYSQLBaseModel):
    pass

class Elegans_tRF_Binding_IntaRNA(MYSQLBaseModel):
    pass

class Elegans_tRF_Binding_Consensus(MYSQLBaseModel):
    pass

# 5.Pombe
class Pombe_tRF_Binding_RNAhybrid(MYSQLBaseModel):
    pass

class Pombe_tRF_Binding_IntaRNA(MYSQLBaseModel):
    pass

class Pombe_tRF_Binding_Consensus(MYSQLBaseModel):
    pass

# 6.Sphaeroides
class Sphaeroides_tRF_Binding_RNAhybrid(MYSQLBaseModel):
    pass

class Sphaeroides_tRF_Binding_IntaRNA(MYSQLBaseModel):
    pass

class Sphaeroides_tRF_Binding_Consensus(MYSQLBaseModel):
    pass

# 7.Xenopus
class Xenopus_tRF_Binding_RNAhybrid(MYSQLBaseModel):
    pass

class Xenopus_tRF_Binding_IntaRNA(MYSQLBaseModel):
    pass

class Xenopus_tRF_Binding_Consensus(MYSQLBaseModel):
    pass

# 8.Zebrafish
class Zebrafish_tRF_Binding_RNAhybrid(MYSQLBaseModel):
    pass

class Zebrafish_tRF_Binding_IntaRNA(MYSQLBaseModel):
    pass

class Zebrafish_tRF_Binding_Consensus(MYSQLBaseModel):
    pass

###############查询数据用函数#####################################################
def doSearch(search_organism, search_table, search_type, search_item, mfe_th, len_th, regions):
    '''根据搜索类型，执行相应数据库查询
    mfe_th和len_th为能量和匹配长度阈值
    '''
    
    
    # 确定物种
    if search_organism == 'human':
        if search_table == 'RNAhybrid':
            # 查询RNAhybrid结果
            table = tRF_Binding_RNAhybrid
        elif search_table == 'IntaRNA':
            # 查询IntaRNA结果
            table = tRF_Binding_IntaRNA
        elif search_table == 'Consensus':
            # 查询Consensus结果
            table = tRF_Binding_Consensus
    
    elif search_organism == 'mouse':
        if search_table == 'RNAhybrid':
            # 查询RNAhybrid结果
            table = Mouse_tRF_Binding_RNAhybrid
        elif search_table == 'IntaRNA':
            # 查询IntaRNA结果
            table = Mouse_tRF_Binding_IntaRNA
        elif search_table == 'Consensus':
            # 查询Consensus结果
            table = Mouse_tRF_Binding_Consensus
            
    elif search_organism == 'drosophila':
        if search_table == 'RNAhybrid':
            # 查询RNAhybrid结果
            table = Drosophila_tRF_Binding_RNAhybrid
        elif search_table == 'IntaRNA':
            # 查询IntaRNA结果
            table = Drosophila_tRF_Binding_IntaRNA
        elif search_table == 'Consensus':
            # 查询Consensus结果
            table = Drosophila_tRF_Binding_Consensus
    
    elif search_organism == 'c.elegans':
        if search_table == 'RNAhybrid':
            # 查询RNAhybrid结果
            table = Elegans_tRF_Binding_RNAhybrid
        elif search_table == 'IntaRNA':
            # 查询IntaRNA结果
            table = Elegans_tRF_Binding_IntaRNA
        elif search_table == 'Consensus':
            # 查询Consensus结果
            table = Elegans_tRF_Binding_Consensus
    
    elif search_organism == 's.pombe':
        if search_table == 'RNAhybrid':
            # 查询RNAhybrid结果
            table = Pombe_tRF_Binding_RNAhybrid
        elif search_table == 'IntaRNA':
            # 查询IntaRNA结果
            table = Pombe_tRF_Binding_IntaRNA
        elif search_table == 'Consensus':
            # 查询Consensus结果
            table = Pombe_tRF_Binding_Consensus
    
    elif search_organism == 'r.sphaeroides':
        if search_table == 'RNAhybrid':
            # 查询RNAhybrid结果
            table = Sphaeroides_tRF_Binding_RNAhybrid
        elif search_table == 'IntaRNA':
            # 查询IntaRNA结果
            table = Sphaeroides_tRF_Binding_IntaRNA
        elif search_table == 'Consensus':
            # 查询Consensus结果
            table = Sphaeroides_tRF_Binding_Consensus
    
    elif search_organism == 'Xenopus-tropicalis':
        if search_table == 'RNAhybrid':
            # 查询RNAhybrid结果
            table = Xenopus_tRF_Binding_RNAhybrid
        elif search_table == 'IntaRNA':
            # 查询IntaRNA结果
            table = Xenopus_tRF_Binding_IntaRNA
        elif search_table == 'Consensus':
            # 查询Consensus结果
            table = Xenopus_tRF_Binding_Consensus
    
    elif search_organism == 'Zebra_fish_Zv9':
        if search_table == 'RNAhybrid':
            # 查询RNAhybrid结果
            table = Zebrafish_tRF_Binding_RNAhybrid
        elif search_table == 'IntaRNA':
            # 查询IntaRNA结果
            table = Zebrafish_tRF_Binding_IntaRNA
        elif search_table == 'Consensus':
            # 查询Consensus结果
            table = Zebrafish_tRF_Binding_Consensus
            
    else:
        raise Exception('Currently unsupported organisms!')
    
    
    # human gene id: ENSGXXX, transcript id: ENSTXXX
    # mouse gene id: ENSMUSGXXX, transcript id: ENSMUSTXXX
    # drosophila gene id: FBgnXXX, transcript id: FBtrXXX, no transcript name
    # elegans gene id: WBGeneXXX, transcript id: no pattern, no transcript name
    # pombe gene id: {'SPAC', 'SPAP', 'SPBC', 'SPBP', 'SPCC', 'SPCP', 'SPMI', 'SPMT'},
    #       trainscript id: add number after the gene id, no transcript name
    # sphaeroides gene id: RsphXXX, transcript id: ABPXXX, no gene name, no transcript name
    # xenopus gene id: ENSXETGXXX, transcript id: ENSXETTXXX
    # zebrafish gene id: ENSDARGXXX, transcript id: ENSDARTXXX
    if search_type == 'trf':
        # 根据tRF ID来查询数据库
        search_field = table.tRF_ID

    elif search_type == 'gene':
        # 根据gene ensembl ID或symbol查询数据库
        
        if search_organism == 'human':
            if search_item.startswith('ENSG'):
                # 按gene ensembl ID查询
                search_field = table.ENSG_ID
            else:
                # 按gene symbol查询
                search_field = table.Gene_Symbol
                
        elif search_organism == 'mouse':
            if search_item.startswith('ENSMUSG'):
                # 按gene ensembl ID查询
                search_field = table.ENSG_ID
            else:
                # 按gene symbol查询
                search_field = table.Gene_Symbol
            
        elif search_organism == 'drosophila':
            if search_item.startswith('FBgn'):
                # 按gene ensembl ID查询
                search_field = table.ENSG_ID
            else:
                # 按gene symbol查询
                search_field = table.Gene_Symbol
    
        elif search_organism == 'c.elegans':
            if search_item.startswith('WBGene'):
                # 按gene ensembl ID查询
                search_field = table.ENSG_ID
            else:
                # 按gene symbol查询
                search_field = table.Gene_Symbol
    
        elif search_organism == 's.pombe':
            if search_item[:4] in set(['SPAC', 'SPAP', 'SPBC', 'SPBP', 'SPCC',
                                   'SPCP', 'SPMI', 'SPMT']):
                # 按gene ensembl ID查询
                search_field = table.ENSG_ID
            else:
                # 按gene symbol查询
                search_field = table.Gene_Symbol
    
        elif search_organism == 'r.sphaeroides':
            # no gene symbol
            search_field = table.ENSG_ID
    
        elif search_organism == 'Xenopus-tropicalis':
            if search_item.startswith('ENSXETG'):
                # 按gene ensembl ID查询
                search_field = table.ENSG_ID
            else:
                # 按gene symbol查询
                search_field = table.Gene_Symbol
    
        elif search_organism == 'Zebra_fish_Zv9':
            if search_item.startswith('ENSDARG'):
                # 按gene ensembl ID查询
                search_field = table.ENSG_ID
            else:
                # 按gene symbol查询
                search_field = table.Gene_Symbol
                
        else:
            raise Exception('Currently unsupported organisms!')

    elif search_type == 'transcript':
        # 根据transcript ensembl ID或name查询数据库
        
        if search_organism == 'human':
            if search_item.startswith('ENST'):
                # 按transcript ensembl ID查询
                search_field = table.ENST_ID
            else:
                # 按transcript name查询
                search_field = table.Trans_Name
                
        elif search_organism == 'mouse':
            if search_item.startswith('ENSMUST'):
                # 按transcript ensembl ID查询
                search_field = table.ENST_ID
            else:
                # 按transcript name查询
                search_field = table.Trans_Name
    
        elif search_organism == 'Xenopus-tropicalis':
            if search_item.startswith('ENSXETT'):
                # 按transcript ensembl ID查询
                search_field = table.ENST_ID
            else:
                # 按transcript name查询
                search_field = table.Trans_Name
    
        elif search_organism == 'Zebra_fish_Zv9':
            if search_item.startswith('ENSDART'):
                # 按transcript ensembl ID查询
                search_field = table.ENST_ID
            else:
                # 按transcript name查询
                search_field = table.Trans_Name
                
        else:
            # other organisms have no transcript name
            search_field = table.ENST_ID
        
    else:
        raise Exception('Invalid search field!')
    
    
    # limit number of entries
    if search_type == 'trf':
        num = 5000
    else:
        num = 50000
        
    # rnahybrid or intarna results
    if not search_table == 'Consensus':
    
        return list(table.select(table.tRF_ID,
                                 table.ENST_ID,
                                 table.Trans_Name,
                                 table.ENSG_ID,
                                 table.Gene_Symbol,
                                 table.Tool,
                                 table.MFE,
                                 table.Area,
                                 table.Max_Hit_Len,
                                 table.Demo,
                                 table.Gene_Evi,
                                 table.Site_Evi)
                         .where(search_field==search_item,
                                 table.MFE<=mfe_th,
                                 table.Max_Hit_Len>=len_th,
                                 table.Area.in_(regions))
                         .order_by(table.MFE, table.Max_Hit_Len.desc())
                         .limit(num)
                         .tuples())
    else:
        # result half rnahybrid + half intarna
        return (list(table.select(table.tRF_ID,
                                  table.ENST_ID,
                                  table.Trans_Name,
                                  table.ENSG_ID,
                                  table.Gene_Symbol,
                                  table.Tool,
                                  table.MFE,
                                  table.Area,
                                  table.Max_Hit_Len,
                                  table.Demo,
                                  table.Gene_Evi,
                                  table.Site_Evi)
                          .where(search_field==search_item,
                                 table.MFE<=mfe_th,
                                 table.Max_Hit_Len>=len_th,
                                 table.Tool=='RNAhybrid',
                                 table.Area.in_(regions))
                          .order_by(table.MFE, table.Max_Hit_Len.desc())
                          .limit(int(num/2))
                          .tuples())
                +
                list(table.select(table.tRF_ID,
                                  table.ENST_ID,
                                  table.Trans_Name,
                                  table.ENSG_ID,
                                  table.Gene_Symbol,
                                  table.Tool,
                                  table.MFE,
                                  table.Area,
                                  table.Max_Hit_Len,
                                  table.Demo,
                                  table.Gene_Evi,
                                  table.Site_Evi)
                          .where(search_field==search_item,
                                 table.MFE<=mfe_th,
                                 table.Max_Hit_Len>=len_th,
                                 table.Tool=='IntaRNA',
                                 table.Area.in_(regions))
                          .order_by(table.MFE, table.Max_Hit_Len.desc())
                          .limit(int(num/2))
                          .tuples()))

#####################网页相关####################################################
# 载入experimental evidence文件
evidences = pd.read_csv(r'./static/tRF-target List.csv',
                        dtype = {'Site_Level': str, 'Gene_Level': str,
                                 'Functionality Study Refs': str})


def transform(string):
    '''replace nan with None
    '''
    if pd.isnull(string):
        return None
    else:
        return string

    
# 转成list
global EVI_LIST
EVI_LIST = []
for i in evidences.index:
    EVI_LIST.append([evidences.at[i, 'Organism'], evidences.at[i, 'tRF_ID'],
                    transform(evidences.at[i, 'Transcript_ID']), transform(evidences.at[i, 'Transcript_Name']),
                    transform(evidences.at[i, 'Gene_ID']), transform(evidences.at[i, 'Gene_Name']),
                    transform(evidences.at[i, 'Gene_Level']), transform(evidences.at[i, 'Site_Level']),
                    transform(evidences.at[i, 'Functionality Study Refs'])])
del evidences


# 载入控件参数
global PARA
# 默认物种是human
with open('./static/json/human_trfs.json') as json_file:
    tmp_list = json.load(json_file)
    PARA = [[item, item] for item in tmp_list]
    del tmp_list

# 物种对应dict
global ORGANISM
ORGANISM = {'human': 'Human',
            'mouse': 'Mouse',
            'drosophila': 'Drosophila',
            'c.elegans': 'C. elegans',
            's.pombe': 'S. pombe',
            'r.sphaeroides': 'R. sphaeroides',
            'Xenopus-tropicalis': 'Xenopus tropicalis',
            'Zebra_fish_Zv9': 'Zebrafish'}

class Config:
    SECRET_KEY = 'hard to guess string'
    SSL_DISABLE = False
    WTF_CSRF_ENABLED = False
    DEBUG = False

class NonValidatingSelectField(SelectField):
    # Skip the pre-validation, otherwise it will raise the "Not a valid choice" error
    def pre_validate(self, form):
        pass 
        
class QueryForm(FlaskForm):
    
    search_table = RadioField('Prediction Tools',
                              choices=[('RNAhybrid', 'RNAhybrid'),
                                       ('IntaRNA', 'IntaRNA'),
                                       ('Consensus', 'Consensus Only')],
                              validators=[DataRequired()],
                              default='Consensus')
    
    search_type = RadioField('Search Ways',
                             choices=[('trf', 'tRF ID'),
                                      ('gene', 'Gene ID / Symbol (e.g. ENSG00000004059 or ARF5 for Human)'),
                                      ('transcript', 'Transcript ID / Name (e.g. ENST00000000233 or ARF5-201 for Human)')],
                             validators=[DataRequired()],
                             default='trf')
    
    search_organism = SelectField('Organism',
                                  choices=[['human', 'Human'],
                                           ['mouse', 'Mouse'],
                                           ['drosophila', 'Drosophila'],
                                           ['c.elegans', 'C. elegans'],
                                           ['s.pombe', 'S. pombe'],
                                           ['r.sphaeroides', 'R. sphaeroides'],
                                           ['Xenopus-tropicalis', 'Xenopus tropicalis'],
                                           ['Zebra_fish_Zv9', 'Zebrafish']],
                                  validators=[DataRequired()],
                                  default='human')
    
    trf = NonValidatingSelectField('', choices=PARA)
    gene = StringField()
    transcript = StringField()
    mfe_threshold = StringField(default=-10)
    len_threshold = StringField(default=8)
    mrna_num = StringField(default=2000)
    
    utr5 = BooleanField("5' UTR", default=True, false_values=('False', 'false', ''))
    cds = BooleanField("CDS", default=True, false_values=('False', 'false', ''))
    utr3 = BooleanField("3' UTR", default=True, false_values=('False', 'false', ''))

    submit = SubmitField('Search')


#####################主函数####################################################
app = Flask(__name__)
app.config.from_object(Config)
Bootstrap(app)

@app.before_request
# This function will run before every request
def _db_connect():
    # If open an already-open database, will get error 'Connection already opened'
    MYSQLDB.connect(reuse_if_open=True)

@app.teardown_request
# This function will run after a request, regardless if an exception occurs or not
def _db_close(exc):
    # Close an already-closed connection will not result in an exception
    if not MYSQLDB.is_closed():
        MYSQLDB.close()

# Extra redirect request for "/favicon.ico"
@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Other pages
@app.route('/<string:page>')
def show(page):
    return render_template('{}.html'.format(page))

# Evidence page
@app.route('/evidence')
def evidence():
    
    th_list = ['Organism', 'tRF ID', 'Transcript', 'Gene',
               'Gene Level Evidence', 'Site Level Evidence', 'Functionality/Disease Study Refs']
    return render_template('evidence.html', th_list=th_list, td_list = EVI_LIST)

# Search database
@app.route('/search', methods=['GET', 'POST'])
def search():
    
    form = QueryForm(formdata=request.form)

    th_list = ['tRF ID', 'Transcript', 'Gene', 'Prediction Algorithm',
               'Free Energy', 'Binding Region', 'Maximum Complementary Length',
               'Interaction Illustration', 'Gene Level Evidence',
               'Site Level Evidence']
    
    if request.method == 'GET':
        # set region boolean filed value as true as default does not work
        form.utr5.data = True
        form.cds.data = True
        form.utr3.data = True
    
    
    if form.validate_on_submit() and request.method == 'POST':
        search_type = form.search_type.data
        search_organism = form.search_organism.data
        
        search_regions = []
        if form.utr5.data:
            search_regions.append('UTR5')
        if form.cds.data:
            search_regions.append('CDS')
        if form.utr3.data:
            search_regions.append('UTR3')
            
        if len(search_regions) < 1:
            success = False
            for_print = 'Please select at least one binding region!'
            return render_template('search.html', form=form, success=success, for_print=for_print, display_table=False)
    
        if search_type == 'trf':
            search_item = form.trf.data
        elif search_type == 'gene':
            search_item = form.gene.data
        elif search_type == 'transcript':
            search_item = form.transcript.data

        if not search_item:
            # search item is null
            success = False
            for_print = 'Invalid search way.\nPlease select the correct search way!'
            return render_template('search.html', form=form, success=success, for_print=for_print, display_table=False)
        
        # Do search
        td_list = doSearch(search_organism, form.search_table.data,
                                search_type, search_item,
                                float(form.mfe_threshold.data),
                                int(float(form.len_threshold.data)),
                                search_regions)
        
        # Filter infos
        filter_infos = '\nwith filter: Energy<={}, MCL>={}, and regions: {}'.format(
        form.mfe_threshold.data, form.len_threshold.data, ', '.join(search_regions))
                
        if td_list:
            # Result is not null
            success = True
            
            for_print = '{:,} {} results for {} {}: {}'.format(len(td_list),
                         form.search_table.data, ORGANISM[search_organism].upper(),
                         search_type.upper(), search_item) + filter_infos
            
            # Decide whether show gene enrichment analysis
            if search_type == 'trf':
                show_pathway = True
            else:
                show_pathway = False
                         
            return render_template('search.html', form=form, success=success,
                                   for_print=for_print, th_list=th_list,
                                   td_list = td_list, display_table=True,
                                   show_pathway = show_pathway)
        else:
            success = False
            for_print = 'No {} results for {}: {}'.format(form.search_table.data,
                            search_type.upper(), search_item) + filter_infos
            
            return render_template('search.html', form=form, success=success, for_print=for_print, display_table=False)

    return render_template('search.html', form=form, display_table=False)

if __name__ == '__main__':
    # 对应intenal IP
    app.run(host= '10.1.1.28', port=80)