#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2020/5/2 15:17
# @Author  : TangYong
# @Email   : tangyonge@yonyou.com
# @File    : config.py
# @Software: PyCharm
import  os
import pymysql

base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/','\\')
dynamic_file_path = os.path.join(base_dir, 'media', 'dynamic_file').replace('/','\\')

#用例执行机信息
case_exe_dev_info = {
    'host':'192.168.1.9',
    'user':'root',
    'pwd':'tangyong',
    'port':22
}

localhost = 'http://192.168.1.4:9000'
mem_cache = '127.0.0.1:11211'

#项目存放路径
project_root_path = r'/usr/src/autotest'

#用例构建文件
case_build_path = r'/usr/src/autotest/bin/product_build.py'


#gitlab host
gitlab_host = 'git clone git@github.com:ty578812638/autotest.git'

#mysql 连接串
mysql_conn = {
        "host": '192.168.1.8',
        "port": 3306,
        "user": 'root',
        "passwd": 'TangYong@123',
        "db": 'atp',
        "charset": 'utf8'
}


#用户状态
user_status = {
    '0':'有效',
    '1':'失效'
}


#统计各个系统用例执行结果
all_sys_dict ={
    'AF':{
        'passed':[],
        'failed': [],
        'error': [],
        'path':'/afSys',
    },
     'AC':{
        'passed':[],
        'failed': [],
        'error': [],
         'path': '/acSys',

    },
    'TD':{
        'passed':[],
        'failed': [],
        'error': [],
        'path': '/tdSys',
    },
    'TP':{
        'passed':[],
        'failed': [],
        'error': [],
        'path': '/tpSys',
    },
    'CODE':{
        'passed':[],
        'failed': [],
        'error': [],
        'path': '/codeSys',
    },
}


#系统菜单
sys_menu_dict ={
    'AF':'/afSys',
     'AC':'/acSys',
    'TD':'/tdSys',
    'TP': '/tpSys',
    'CODE': '/codeSys',
}



#初始密码
init_pwd = '123456'

#超时时间
timeout = 1800


#邮件配置信息
mail_info = {
    'connect':{
        'host':'mail.yonyou.com',
        'port':25
    },
    'login':{
        'username':'tangyonge',
        'passwd':'jy170530.'
    },
    'sender':'tangyonge@yonyou.com',
}
# mail_info = {
#     'connect':{
#         'host':'smtp.163.com',
#         'port':25
#     },
#     'login':{
#         'username':'tyongjob@163.com',
#         'passwd':'jy170530'
#     },
#     'sender':'tyongjob@163.com',
# }




#导出字段(和数据库字段需对应上)
case_fields = ['系统名称','版本编号','用例名称','用例编号','测场景','预期结果','实际结果','测试者','测试结果','测试时间']


