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
from wtforms import SelectField, SubmitField, RadioField, StringField
from wtforms.validators import DataRequired
import peewee as pw
import json
import os


#####################数据库相关##################################################
# 数据库名称定义为全局变量
global MYSQLDB
MYSQLDB = pw.MySQLDatabase('trftarget', user='root', password='12345678',
                           host='127.0.0.1', port=3306, autoconnect=False)

class MYSQLBaseModel(pw.Model):
    # 所用数据库为MYSQLDB
    class Meta:
        database = MYSQLDB # MYSQLDB为所定义的数据库变量

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

# 定义数据库中的表格模型
class tRF_Binding_RNAhybrid(MYSQLBaseModel):
    tRF_ID = pw.FixedCharField(max_length=32)
    ENST_ID = pw.FixedCharField(max_length=16)
    MFE = pw.FloatField()
    P_Val = pw.FloatField()
    Max_Hit_Len = UnTinyIntField()
    Area = pw.FixedCharField(max_length=4)
    Demo = pw.TextField()
    ENSG_ID = pw.FixedCharField(max_length=16)
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

class tRF_Binding_IntaRNA(MYSQLBaseModel):
    tRF_ID = pw.FixedCharField(max_length=32)
    ENST_ID = pw.FixedCharField(max_length=16)
    MFE = pw.FloatField()
    Max_Hit_Len = UnTinyIntField()
    Area = pw.FixedCharField(max_length=4)
    Demo = pw.TextField()
    ENSG_ID = pw.FixedCharField(max_length=16)
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


###############查询数据用函数#####################################################
def doSearch(search_table, search_type, search_item, mfe_th, len_th):
    '''根据搜索类型，执行相应数据库查询
    mfe_th和len_th为能量和匹配长度阈值
    '''
    
    if search_table == 'RNAhybrid':
        # 查询RNAhybrid结果
        table = tRF_Binding_RNAhybrid
    elif search_table == 'IntaRNA':
        # 查询IntaRNA结果
        table = tRF_Binding_IntaRNA
    
    if search_type == 'trf':
        # 根据tRF ID来查询数据库
        search_field = table.tRF_ID

    elif search_type == 'gene':
        # 根据gene ensembl ID或symbol查询数据库
        if search_item.startswith('ENSG'):
            # 按gene ensembl ID查询
            search_field = table.ENSG_ID
        else:
            # 按gene symbol查询
            search_field = table.Gene_Symbol

    elif search_type == 'transcript':
        # 根据transcript ensembl ID或name查询数据库
        if search_item.startswith('ENST'):
            # 按transcript ensembl ID查询
            search_field = table.ENST_ID
        else:
            # 按transcript name查询
            search_field = table.Trans_Name
    
    return (table.select(table.tRF_ID,
                         table.ENST_ID,
                         table.Trans_Name,
                         table.ENSG_ID,
                         table.Gene_Symbol,
                         table.MFE,
                         table.Area,
                         table.Max_Hit_Len,
                         table.Demo)
                        .where(search_field==search_item,
                               table.MFE<=mfe_th,
                               table.Max_Hit_Len>=len_th)
                        .limit(2000)
                        .tuples())

#####################网页相关####################################################
# 载入控件参数
global PARA
with open('./static/para_for_trf.json') as json_file:
    PARA = json.load(json_file)

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
                                       ('IntaRNA', 'IntaRNA')],
                              validators=[DataRequired()],
                              default='RNAhybrid')
    
    search_type = RadioField('Search Ways',
                             choices=[('trf', 'tRF ID'),
                                      ('gene', 'Gene Ensembl ID / Symbol (e.g. ENSG00000004059 or ARF5)'),
                                      ('transcript', 'Transcript Ensembl ID / Name (e.g. ENST00000000233 or ARF5-201)')],
                             validators=[DataRequired()],
                             default='trf')
    
    trf = NonValidatingSelectField('', choices=PARA)
    gene = StringField()
    transcript = StringField()
    mfe_threshold = StringField(default=-25)
    len_threshold = StringField(default=8)
    
    submit = SubmitField('Search')


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

# Search database
@app.route('/search', methods=['GET', 'POST'])
def search():
    
    form = QueryForm(formdata=request.form)
    
    th_list = ['tRF ID', 'Transcript', 'Gene',
               'Free Energy', 'Interaction Area', 'Maximum Complementary Length',
               'Interaction Illustration']

    if form.validate_on_submit() and request.method == 'POST':
        search_type = form.search_type.data
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
        td_list = list(doSearch(form.search_table.data, search_type, search_item,
                          float(form.mfe_threshold.data),
                          int(form.len_threshold.data)))
        
        # Filter infos
        filter_infos = '\nwith filter: Energy<={:d} and MCL>={:d}'.format(
        int(form.mfe_threshold.data), int(form.len_threshold.data))
                
        if td_list:
            # Result is not null
            success = True
            
            for_print = '{:,} {} results for {}: {}'.format(len(td_list),
                         form.search_table.data, search_type.upper(), search_item) + filter_infos
            
            return render_template('search.html', form=form, success=success,
                                   for_print=for_print, th_list=th_list,
                                   td_list = td_list, display_table=True)
        else:
            success = False
            for_print = 'No {} results for {}: {}'.format(form.search_table.data,
                            search_type.upper(), search_item) + filter_infos
            
            return render_template('search.html', form=form, success=success, for_print=for_print, display_table=False)

    return render_template('search.html', form=form, display_table=False)

if __name__ == '__main__':
    # 对应intenal IP
    app.run(host= '10.1.1.28', port=80)