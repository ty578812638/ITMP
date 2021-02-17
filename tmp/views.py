#-*- coding: utf-8 -*-
# @Time    : 2018/6/21 11:21
# @Author  : TangYong
# @File    : execute_case.py
# @Software: PyCharm


import os
import re

import json
import copy
import xlrd
import xlwt
import uuid
import asyncio
import memcache
from django.shortcuts import render, HttpResponse, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger



from tmp import public
from tmp import config

from tmp.db_server import sys_info
from tmp.db_server import case_info
from tmp.db_server import user_info
from tmp.db_server import test_report


db_sys_info = sys_info.SysInfoRepository()
db_case_info = case_info.CaseInfoRepository()
db_user_info = user_info.UserInfoRepository()
db_test_report = test_report.TestReportInfoRepository()


get_cur_time = public.GetCurrentTime()


mc = memcache.Client([config.mem_cache], debug=True)


# Create your views here.

'''******************** 认证 ********************'''
def check(mc):
    def auth(func):
        def inner(request, *args, **kwargs):
            token = request.COOKIES.get('token')
            user = request.COOKIES.get('user')

            if user is None:
                return redirect('/login')

            token_info = mc.get(user)
            if token == token_info['token'] and user == token_info['user']:
                return func(request, *args, **kwargs)
            else:
                return redirect('/login')
        return inner

    return auth



'''******************** 分页 ********************'''

class Pager:
    def __init__(self, obj_count, page_size=10):
        self.obj_count = obj_count,
        self.page_size = page_size

    def handel_page(self, page_no=1):
        pag_obj = Paginator(self.obj_count, self.page_size)

        try:
            currentPage = int(page_no)
            result_list = pag_obj.page(currentPage).object_list  # 获取当前页码的记录

            if isinstance(result_list, tuple):
                data_list = result_list[0]

            else:
                result_list = tuple(result_list)
                data_list = result_list[0]


        except PageNotAnInteger:

            # 如果用户输入的页码不是整数时,显示第1页的内容
            data_list = pag_obj.page(1).object_list

        except EmptyPage:

            # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
            data_list = pag_obj.page(pag_obj.num_pages)

        return data_list



'''******************** 展示首页公共数据 ********************'''
def show_home(user_no):

    # 获取所有系统编号
    all_sys_no_list = db_sys_info.handel_query_sys('sys_no')

    # 初始化每个系统用来统计测试结果的初始值
    # 初始化每个系统菜单和菜单路由
    sysTestResMenuPathInitVal = {}
    for sys_no in all_sys_no_list:
        for key,val in sys_no.items():
            sys_info = {
                val: {
                    'passed': [],
                    'failed': [],
                    'error': [],
                    val: '/%sSys' % (val).lower()
                }
            }
            sysTestResMenuPathInitVal.update(sys_info)


    #获取指定用户拥有的系统编号
    sys_no_list = db_user_info.get_user_sys_list(user_no)

    if not sys_no_list:
        return None

    #判断当前是否拥有所有系统菜单（用于统计首页中测试用例总数）
    elif len(sys_no_list[1])  == len(all_sys_no_list):

        #查询所有系统测试用例信息
        all_data_list = db_case_info.handel_query_case()

    else:
        #查询指定系统测试用例信息
       all_data_list = db_case_info.handel_query_case_by_sys("','".join(sys_no_list[1]))


    passed_list = []
    failed_list = []
    error_list = []
    sys_list = []

    # 统计对应系统测试结果数
    for data in all_data_list:
        for k, v in data.items():
           if k == 'test_res' :
                if v.lower() == 'passed':
                    passed_list.append(v)
                if v.lower() == 'failed':
                    failed_list.append(v)
                if v.lower() == '' or v == 'null' or v == None:
                    error_list.append(v)
           if k == 'sys_name':
                sys_list.append(v)

    statistics_all_data_dict = {
        'passed_count': len(passed_list),
        'failed_count': len(failed_list),
        'error_count': len(error_list),
        'sum_count': len(all_data_list),
        'sys_name_list': list(set(sys_list))
}

    # 分别统计单个系统测试结果数
    if  len(sys_no_list[1])  == len(all_sys_no_list):
        for key, val in  sysTestResMenuPathInitVal.items():

            test_result = db_case_info.handel_query_case(None, **{'sys_name': key})


            if  len(test_result) < 1:
               continue

            if len(test_result) >= 1:

                for tes_res in test_result:
                    for k, v in tes_res.items():
                        if k == 'test_res':
                            if v.lower() == 'passed':
                                sysTestResMenuPathInitVal[key]['passed'].append(v)

                            elif v.lower()  == 'failed':
                                sysTestResMenuPathInitVal[key]['failed'].append(v)

                            else:
                                sysTestResMenuPathInitVal[key]['error'].append(v)


        return [statistics_all_data_dict, sysTestResMenuPathInitVal,sys_no_list[0]]


    else:

       for key in sys_no_list[1]:

           if key in sysTestResMenuPathInitVal.keys():

               test_result =  db_case_info.handel_query_case(None,**{'sys_name':key})


               if len(test_result) < 1:
                   continue

               if len(test_result) >= 1:
                   for tes_res in test_result:
                       for k, v in tes_res.items():
                           if k == 'test_res':

                               if v.lower()  == 'passed':
                                   sysTestResMenuPathInitVal[key]['passed'].append(v)

                               elif v.lower()  == 'failed':
                                   sysTestResMenuPathInitVal[key]['failed'].append(v)

                               else:
                                   sysTestResMenuPathInitVal[key]['error'].append(v)



       #statistics_all_data_dict： 首页中测试用例总数
       #sysTestResMenuPathInitVal：主要用来存储对应系统测试结果数
       #,sys_no_list[0]  系统菜单权限
       print('sysTestResMenuPathInitVal:',sysTestResMenuPathInitVal)
       return [statistics_all_data_dict,sysTestResMenuPathInitVal,sys_no_list[0]]



'''******************** 展示用例列表中的默认数据 ********************'''
def show_default_case(request, sys_name,url_path, html_page):

    page = request.GET.get('page', 1)
    user_no = request.COOKIES.get('user')

    case_data_list = db_case_info.handel_query_case(None, **{'sys_name': sys_name})
    case_count = len(case_data_list)

    case_pager = Paginator(case_data_list, 10)


    try:
        cur_page = int(page)

        # 获取当前页码的所有数据
        data_list = case_pager.page(cur_page).object_list
        previous_next_page = case_pager.page(page)

        for item in data_list:
            test_res = item['test_res']
            if not test_res:
                item['test_res'] = 'Error'

            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time
            update_time = str(item['update_time'])[0:10]
            item['update_time'] = update_time

    except PageNotAnInteger:

        # 如果用户输入的页码不是整数时,显示第1页的内容
        data_list = case_pager.page(1).object_list

        for item in data_list:
            test_res = item['test_res']
            if not test_res:
                item['test_res'] = 'Error'
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time
            update_time = str(item['update_time'])[0:10]
            item['update_time'] = update_time

    except EmptyPage:

        # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
        data_list = case_pager.page(case_pager.num_pages)

        for item in data_list:
            test_res = item['test_res']
            if not test_res:
                item['test_res'] = 'Error'
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time
            update_time = str(item['update_time'])[0:10]
            item['update_time'] = update_time


    rep_html_page = render(request, html_page, locals())
    rsp_html_page = public.update_token(request, user_no, rep_html_page)
    return rsp_html_page


'''******************** 查询用例信息 ********************'''


def query_case_info(request, sys_name, url_path, html_page):
    '''
    :param request:  前端的查询请求对象
    :param sys_name:  系统名称
    :param url_path:  url路由
    :param html_page:  对象系统的html
    :return:  html对象和用例查询结果
    '''
    #获取前端的查询数据
    query_req_data = dict(request.GET)
    query_data = {}
    for k, v in query_req_data.items():
        query_data[k] = v[0].strip().lower()

    user_no = request.COOKIES.get('user')

    query_id = user_no + sys_name

    try:
        #code表示是带有查询条件的查询，非默认展示(code:search)
        search_value = query_data['code']
        del query_data['code']
        mc.set(query_id, query_data)
    except Exception:
        #此处为查询后翻页的分支，翻页时，获取上一次查询记录
        #根据上一次的查询条件再次 查询

        query_data = mc.get(query_id)
        print('异常查询query_data:', query_data)

        #获取哪些条件是没有查询条件值
        null_value_list = []
        for k, v in query_data.items():
            if v is None:
                null_value_list.append(k)

        #删除没有查询条件值得查询条件
        for key in null_value_list:
            del query_data[key]

    result_data_list = db_case_info.handel_query_case(None, **query_data)

    case_count = len(result_data_list)

    case_pager = Paginator(result_data_list, 10)

    page = request.GET.get('page', 1)
    try:
        cur_page = int(page)

        # 获取当前页码的所有数据
        data_list = case_pager.page(cur_page).object_list
        previous_next_page = case_pager.page(page)

        for item in data_list:
            test_res = item['test_res']
            if not test_res:
                item['test_res'] = 'Error'
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time
            update_time = str(item['update_time'])[0:10]
            item['update_time'] = update_time

    except PageNotAnInteger:

        # 如果用户输入的页码不是整数时,显示第1页的内容
        data_list = case_pager.page(1).object_list

        for item in data_list:
            test_res = item['test_res']
            if not test_res:
                item['test_res'] = 'Error'
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time
            update_time = str(item['update_time'])[0:10]
            item['update_time'] = update_time

    except EmptyPage:

        # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
        data_list = case_pager.page(case_pager.num_pages)

        for item in data_list:
            test_res = item['test_res']
            if not test_res:
                item['test_res'] = 'Error'
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time
            update_time = str(item['update_time'])[0:10]
            item['update_time'] = update_time

    rep_html_page = render(request, html_page, locals())
    rsp_html_page = public.update_token(request, user_no, rep_html_page)
    return rsp_html_page



#登录
def login(request):
    print("\033[0;31m%s\033[0m" % ("IP:" + request.META['REMOTE_ADDR']))

    message = ''

    if request.method == 'POST':

        user = request.POST.get('user')
        pwd = request.POST.get('pwd')

        user_info = db_user_info.handel_query_user_info(('salt'), **{'user_no': user})
        salt = user_info[0]['salt']


        get_md5_pwd = public.generate_md5_pwd(pwd, salt)
        md5_pwd = get_md5_pwd[0]
        user_info = db_user_info.handel_query_user_info(**{'user_no': user, 'pwd': md5_pwd})

        if user_info:
            status = user_info[0]['status']
            if status != '0':
                return render(request, 'login.html', {'msg': '用户状态失效'})

            token = public.generate_token(user)

            mc.set(user, {'user': user, 'token': token})

            html_page = redirect("/index")
            html_page.set_cookie('user', user, max_age=config.timeout)

            html_page.set_cookie('token', token, max_age=config.timeout)
            return html_page

        else:
            message = '用户名或密码错误'
            return render(request, 'login.html', {'msg': message})

    else:
        return render(request, 'login.html', {'msg': message})


#退出
@check(mc)
def logout(request):
  return redirect('/login')


#登录后默认index页
@check(mc)
def index(request):
    # 获取默认页面和默认状态列表(首页)

    home_url = '/homePage'
    path = "/homePage"


    user_no = request.COOKIES.get('user')
    home_data_dict = show_home(user_no)

    if home_data_dict:
        all_sys_test_case_data_dict = home_data_dict[0]
        single_sys_test_data_dict = home_data_dict[1]
        user_sys_dict =  home_data_dict[2]


        #统计单个系统测试用例数
        for key, val in single_sys_test_data_dict.items():
            single_sys_test_data_dict[key]['passed'] = (len(val['passed']))
            single_sys_test_data_dict[key]['failed'] = (len(val['failed']))
            single_sys_test_data_dict[key]['error'] = (len(val['error']))


       #获取所有菜单名称以及路径
        all_sys_menu_dict = {}
        for key, val in single_sys_test_data_dict.items():
            for k, v in val.items():
                if k == key:
                    sys_menu_dict = {k: v}
                    all_sys_menu_dict.update(sys_menu_dict)



        html_page = render(request, 'layout.html', locals())

        print('all_sys_test_case_data_dict:',all_sys_test_case_data_dict)
        print('single_sys_test_data_dict:', single_sys_test_data_dict)
        print('user_sys_dict:', user_sys_dict)
        print('all_sys_menu_dict:', all_sys_menu_dict)



        # statistics_sys_data_dict = copy.deepcopy(single_sys_test_data_dict)

    #     for key, val in statistics_sys_data_dict.items():
    #         statistics_sys_data_dict[key]['passed'] = (len(val['passed']))
    #         statistics_sys_data_dict[key]['failed'] = (len(val['failed']))
    #         statistics_sys_data_dict[key]['error'] = (len(val['error']))
    html_page = render(request, 'layout.html',locals())
    response_html = public.update_token(request, user_no, html_page)
    return html_page


#首页
@check(mc)
def home(request):
    home_url = '/homePage'
    path = "/homePage"

    user_no = request.COOKIES.get('user')

    #获取首页数据
    home_data_dict = show_home(user_no)

    if home_data_dict:

        #获取所有系统测试数据
        all_sys_test_case_data_dict = home_data_dict[0]

        #获取单个系统的测试数据
        single_sys_test_data_dict = home_data_dict[1]

        #用户锁拥有的系统编号
        user_sys_dict = home_data_dict[2]

        # 统计单个系统测试用例数
        for key, val in single_sys_test_data_dict.items():
            single_sys_test_data_dict[key]['passed'] = (len(val['passed']))
            single_sys_test_data_dict[key]['failed'] = (len(val['failed']))
            single_sys_test_data_dict[key]['error'] = (len(val['error']))

        # 获取所有菜单名称以及路径
        all_sys_menu_dict = {}
        for key, val in single_sys_test_data_dict.items():
            for k, v in val.items():
                if k == key:
                    sys_menu_dict = {k: v}
                    all_sys_menu_dict.update(sys_menu_dict)


        # statistics_sys_data_dict = copy.deepcopy(single_sys_test_data_dict)

    html_page = render(request, 'layout.html', locals())
    response_html = public.update_token(request, user_no, html_page)
    return html_page



'''******************** 系统菜单操作 ********************'''
@check(mc)
def af_sys(request):

    html_page = show_default_case(request,'af','/afSys','af_sys.html')

    return html_page


@check(mc)
def query_af_case(request):

    html_page = query_case_info(request,'AF','/queryAFCase','af_sys.html')

    return html_page






'''******************** 用户管理操作 ********************'''

@check(mc)
def user_manage(request):
    user = request.COOKIES.get('user')
    path = '/userManagePage'


    user_data_list = db_user_info.handel_query_user_info()
    user_pager = Paginator(user_data_list, 10)

    try:
        page = request.GET.get('page', 1)
        currentPage = int(page)

        # 获取当前页码的所有数据
        data_list = user_pager.page(currentPage).object_list
        previous_next_page = user_pager.page(page)

        for item in data_list:
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time

            status = item['status']
            for k, v in config.user_status.items():
                if k == str(status):
                    item['status'] = v

        none_vale_set = set()
        for i in range(len(data_list)):
            for k, v in data_list[i].items():
                if v is None:
                    none_vale_set.add(k)

        none_vale_list = list(none_vale_set)
        for none_vale in none_vale_list:
            for item in data_list:
                if item[none_vale] is None:
                    del item[none_vale]
    except PageNotAnInteger:

        # 如果用户输入的页码不是整数时,显示第1页的内容
        data_list = user_pager.page(1).object_list

        for item in data_list:
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time

            status = item['status']
            for k, v in config.user_status.items():
                if k == str(status):
                    item['status'] = v

        none_vale_set = set()
        for i in range(len(data_list)):
            for k, v in data_list[i].items():
                if v is None:
                    none_vale_set.add(k)

        none_vale_list = list(none_vale_set)
        for none_vale in none_vale_list:
            for item in data_list:
                if item[none_vale] is None:
                    del item[none_vale]


    except EmptyPage:

        # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
        data_list = user_pager.page(user_pager.num_pages)

        for item in data_list:
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time

            status = item['status']
            for k, v in config.user_status.items():
                if k == str(status):
                    item['status'] = v

        none_vale_set = set()
        for i in range(len(data_list)):
            for k, v in data_list[i].items():
                if v is None:
                    none_vale_set.add(k)

        none_vale_list = list(none_vale_set)
        for none_vale in none_vale_list:
            for item in data_list:
                if item[none_vale] is None:
                    del item[none_vale]

    req_page = render(request, 'user_manage.html', locals())
    response = public.update_token(request, user, req_page)
    return response


@check(mc)
def create_user(request):

    if request.method == 'POST':
        user_no = request.COOKIES.get('user')
        request_data = request.POST
        request_data = dict(request_data)
        print('创建用户请求数据:', request_data)

        new_user_no =  request_data.get('user_no')
        if  not new_user_no:
            return HttpResponse(json.dumps({'code': '400', 'msg': '用户编号不能为空' }, ensure_ascii=False))

        new_user_name = request_data.get('user_name')
        if not new_user_name:
            return HttpResponse(json.dumps({'code': '400', 'msg': '用户姓名不能为空'}, ensure_ascii=False))

        sys_no = request_data.get('sys_no[]')
        if not sys_no:
            return HttpResponse(json.dumps({'code': '400', 'msg': '所属系统不能为空'}, ensure_ascii=False))

        user_exist = db_user_info.handel_query_user_info(**{'user_no':new_user_no[0]})
        if  user_exist:
            return HttpResponse(json.dumps({'code': '400', 'msg': '%s 用户已存在'%new_user_no}, ensure_ascii=False))

        #给用户生成默认密码
        md5_pwd = public.generate_md5_pwd(config.init_pwd)
        user_data_dict = {
            'pwd': md5_pwd[0],
            'salt': md5_pwd[1],
            'creator': user_no,
            'create_time': get_cur_time.complete_time()
        }

        for k,v in request_data.items():
            user_data_dict[k] = v[0]

        del user_data_dict ['sys_no[]']

        #判断有多少系统编号:
        if len(sys_no) >1:
            sys_no_list = ','.join(sys_no)
        else:
            sys_no_list= sys_no[0]

        user_data_dict['sys_no'] = sys_no_list

        db_user_info.handel_crate_user(**user_data_dict)

        return HttpResponse(json.dumps({'code': '200', 'msg': '创建成功'}, ensure_ascii=False))


@check(mc)
def delete_user(request):
    if request.method == 'POST':
        user_no_str = request.POST.get('user_no_list')
        print('删除用户请求数据:', user_no_str)
        user_no_list = user_no_str.split(',')

        if user_no_list:
            for user_no in user_no_list:
                db_user_info.hand_delete_user(user_no)
            return HttpResponse(json.dumps({'code': '200', 'msg': '删除成功'}, ensure_ascii=False))

        else:
            return HttpResponse(json.dumps({'code': '400', 'msg': '用户编号不能为空'}, ensure_ascii=False))


@check(mc)
def query_user(request):
    # 增加post判断,主要用来返回项目成员
    if request.method == 'POST':
        project_member_list = getUserInfo.handel_query_user_info(('user_no', 'user_name'), **{'status': '0'})

        print('project_member_list:', project_member_list)
        return HttpResponse(json.dumps(project_member_list))

    else:
        path = "/queryUser"
        user = request.COOKIES.get('user')
        menu_list = public.get_menu_list(user)

        print('查询GET用户请求数据:', request.GET)

        get_query_data = dict(request.GET)

        # 数据格式转换
        query_data = {}
        for k, v in get_query_data.items():
            query_data[k] = v[0].strip().upper()

        try:
            search_value = query_data['code']

            del query_data['code']

            print('save_to_memcache', query_data)

            mc.set(user + 'query_user', query_data)



        except Exception:
            query_data = mc.get(user + 'query_user')

            null_value_list = []
            for k, v in query_data.items():
                if v is None:
                    null_value_list.append(k)
            for key in null_value_list:
                del query_data[key]

        is_null_value = ''
        for k, v in query_data.items():
            is_null_value += v

        if is_null_value:
            result_data_list = getUserInfo.handel_query_user_info(**query_data)

        else:
            result_data_list = getUserInfo.handel_query_user_info()

        pending_pager = Paginator(result_data_list, 10)

        try:
            page = page = request.GET.get('page', 1)
            currentPage = int(page)

            # 获取当前页码的所有数据
            data_list = pending_pager.page(currentPage).object_list
            previous_next_page = pending_pager.page(page)

            for item in data_list:
                create_time = str(item['create_time'])[0:10]
                item['create_time'] = create_time

                status = item['status']
                for k, v in config.user_status.items():
                    if k == str(status):
                        item['status'] = v

            # 删除None值
            none_vale_set = set()
            for i in range(len(data_list)):
                for k, v in data_list[i].items():
                    if v is None:
                        none_vale_set.add(k)

            none_vale_list = list(none_vale_set)
            for none_vale in none_vale_list:
                for item in data_list:
                    if item[none_vale] is None:
                        del item[none_vale]

        except PageNotAnInteger:

            # 如果用户输入的页码不是整数时,显示第1页的内容
            data_list = pending_pager.page(1).object_list

            for item in data_list:
                create_time = str(item['create_time'])[0:10]
                item['create_time'] = create_time

                status = item['status']
                for k, v in config.user_status.items():
                    if k == str(status):
                        item['status'] = v

            # 删除None值
            none_vale_set = set()
            for i in range(len(data_list)):
                for k, v in data_list[i].items():
                    if v is None:
                        none_vale_set.add(k)

            none_vale_list = list(none_vale_set)
            for none_vale in none_vale_list:
                for item in data_list:
                    if item[none_vale] is None:
                        del item[none_vale]


        except EmptyPage:

            # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
            data_list = pending_pager.page(pending_pager.num_pages)

            for item in data_list:
                create_time = str(item['create_time'])[0:10]
                item['create_time'] = create_time

                status = item['status']
                for k, v in config.user_status.items():
                    if k == str(status):
                        item['status'] = v

            none_vale_set = set()
            for i in range(len(data_list)):
                for k, v in data_list[i].items():
                    if v is None:
                        none_vale_set.add(k)

            none_vale_list = list(none_vale_set)
            for none_vale in none_vale_list:
                for item in data_list:
                    if item[none_vale] is None:
                        del item[none_vale]

        return render(request, 'user_manage.html', locals())


@check(mc)
def edit_user(request):
    get_time = public.GetCurrentTime()
    user = request.COOKIES.get('user')

    if request.method == 'GET':
        request_data = request.GET
        request_data = dict(request_data)
        print('编辑角色GET请求数据:', request_data)

        if not request_data:
            return HttpResponse(json.dumps({'code': '400', 'msg': '用户编号不能为空'}))

        user_no = request.GET.get('user_no')
        user_info = db_user_info.handel_query_user_info(**{'user_no': user_no})

        del user_info[0]['create_time']
        del user_info[0]['updater']
        del user_info[0]['update_time']
        return HttpResponse(json.dumps({'user_info': user_info}))

    elif request.method == 'POST':
        request_data = request.POST
        request_data = dict(request_data)
        print('编辑用户请求数据:', request_data)

        data_dict = {
            'updater': user,
            'update_time': get_time.complete_time()
        }
        if request_data:
                for k, v in request_data.items():
                    if  v[0]:
                        data_dict[k] = v[0]
                    else:
                        return HttpResponse(json.dumps({'code': '400', 'msg': '【%s】不能为空' % k}))

        db_user_info.hand_update_user(**data_dict)

        return HttpResponse(json.dumps({'code': '200', 'msg': '编辑成功'}))




'''******************** 系统管理操作 ********************'''
@check(mc)
#系统管理首页
def sys_manage(request):
    user_no = request.COOKIES.get('user')
    path = "/sysManage"

    page = request.GET.get('page', 1)

    get_sys_list = db_sys_info.handel_query_sys()

    pending_pager = Paginator(get_sys_list, 10)

    try:
        currentPage = int(page)

        # 获取当前页码的所有数据
        data_list = pending_pager.page(currentPage).object_list
        previous_next_page = pending_pager.page(page)



        for item in data_list:
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time


    except PageNotAnInteger:

        # 如果用户输入的页码不是整数时,显示第1页的内容
        data_list = pending_pager.page(1).object_list

        for item in data_list:
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time



    except EmptyPage:

        # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
        data_list = pending_pager.page(pending_pager.num_pages)

        for item in data_list:
            create_time = str(item['create_time'])[0:10]
            item['create_time'] = create_time


    print('data_list:',data_list)
    req_page = render(request, 'sys_manage.html', locals())
    response = public.update_token(request, user_no, req_page)
    return response

#创建系统
@check(mc)
def create_sys(request):
    if request.method == 'POST':
        user_no = request.COOKIES.get('user')

        request_data = request.POST
        request_data = dict(request_data)
        print('创建系统请求数据:', request_data)

        data_dict = {
            'creator': user_no,
            'create_time': get_cur_time.complete_time()
        }
        if request_data:
            for k, v in request_data.items():
                if not v[0]:
                    return HttpResponse(json.dumps({'code': '400', 'msg': '【%s】不能为空' % k}, ensure_ascii=False))
                data_dict[k] = v[0].upper()




        get_sys_no = db_sys_info.handel_query_sys('sys_no', **{'sys_no': data_dict['sys_no']})

        if get_sys_no:
            if get_sys_no[0]['sys_no']:
                return HttpResponse(json.dumps({'code': '400', 'msg': '【%s】已存在' % get_sys_no[0]['sys_no']}))

        db_sys_info.handel_create_sys(**data_dict)

        return HttpResponse(json.dumps({'code': '200', 'msg': '创建成功'}, ensure_ascii=False))

#删除系统
@check(mc)
def delete_sys(request):
    '''
    根据系统编号删除系统信息
    :param request:
    :return:
    '''
    if request.method == 'POST':
        sys_no_str = request.POST.get('sys_no_list')
        sys_no_list = sys_no_str.split(',')

        if sys_no_list:
            for sys_no in sys_no_list:
                db_sys_info.hand_delete_sys(sys_no)
            return HttpResponse(json.dumps({'code': '200', 'msg': '删除成功'}, ensure_ascii=False))

        else:
            return HttpResponse(json.dumps({'code': '400', 'msg': '系统编号不能为空'}, ensure_ascii=False))


#编辑系统
def edit_sys(request):
    '''
    根据系统编号编辑系统信息
    :param request:
    :return:
    '''
    get_time = public.GetCurrentTime()
    user = request.COOKIES.get('user')

    if request.method == 'GET':

        request_data = request.GET
        request_data = dict(request_data)
        print('编辑系统GET请求数据:', request_data)

        if not request_data:
            return HttpResponse(json.dumps({'code': '400', 'msg': '角色编号不能为空'}, ensure_ascii=False))

        sys_no = request.GET.get('sys_no')


        sys_info = db_sys_info.handel_query_sys('sys_no','sys_name', **{'sys_no': sys_no})



        return HttpResponse(json.dumps({'sys_info': sys_info}))

    elif request.method == 'POST':
        request_data = request.POST
        request_data = dict(request_data)
        print('request_data:',request_data)

        data_dict = {
            'updater': user,
            'update_time': get_time.complete_time(),
        }

        if request_data:
            for k, v in request_data.items():
                if not v[0]:
                    return HttpResponse(json.dumps({'code': '400', 'msg': '【%s】不能为空' % k}))
                data_dict[k] = v[0]


            db_sys_info.hand_update_sys(**data_dict)

        return HttpResponse(json.dumps({'code': '200', 'msg': '编辑成功'}))

#查询系统
@check(mc)
def query_sys(request):
    if request.method == 'GET':
        path = "/sysManage"
        user = request.COOKIES.get('user')
        menu_list = db_user_info.get_user_sys_list(user)

        print('查询GET系统    请求数据:', request.GET)

        get_query_data = dict(request.GET)

        # 数据格式转换
        query_data = {}
        for k, v in get_query_data.items():
            query_data[k] = v[0].strip().upper()

        try:

            search_value = query_data['code']
            del query_data['code']
            mc.set(user + 'query_sys', query_data)

        except Exception:
            query_data = mc.get(user + 'query_sys')

            null_value_list = []
            for k, v in query_data.items():
                if v is None:
                    null_value_list.append(k)
            for key in null_value_list:
                del query_data[key]

        is_null_value = ''
        for k, v in query_data.items():
            is_null_value += v

        if is_null_value:
            result_data_list = db_sys_info.handel_query_sys(**query_data)

        else:
            result_data_list =db_sys_info.handel_query_sys()

        pending_pager = Paginator(result_data_list, 10)

        try:
            page = page = request.GET.get('page', 1)
            currentPage = int(page)

            # 获取当前页码的所有数据
            data_list = pending_pager.page(currentPage).object_list
            previous_next_page = pending_pager.page(page)

            for item in data_list:
                create_time = str(item['create_time'])[0:10]
                item['create_time'] = create_time



        except PageNotAnInteger:

            # 如果用户输入的页码不是整数时,显示第1页的内容
            data_list = pending_pager.page(1).object_list

            for item in data_list:
                create_time = str(item['create_time'])[0:10]
                item['create_time'] = create_time



        except EmptyPage:

            # 如果用户输入的页数不在系统的页码列表中时,显示最后一页的内容
            data_list = pending_pager.page(pending_pager.num_pages)

            for item in data_list:
                create_time = str(item['create_time'])[0:10]
                item['create_time'] = create_time



        return render(request, 'sys_manage.html', locals())

    elif request.method == 'POST':
        request_data = dict(request.POST)
        print('查询POST系统请求数据:', request_data)

        query_data = {}
        if request_data:
            for k, v in request_data.items():
                query_data[k] = v[0].strip()

        sys_list = db_sys_info.handel_query_sys(**query_data)

        for item in sys_list:
            try:
                create_time = str(item['create_time'])[0:10]
                item['create_time'] = create_time

                update_time = str(item['update_time'])[0:10]
                item['update_time'] = update_time

            except Exception:
                continue

        #获取查询条件为空的的值
        none_vale_set = set()
        for i in range(len(sys_list)):
            for k, v in sys_list[i].items():
                if v is None:
                    none_vale_set.add(k)

        # 删除空值(不然 json dump会报错)
        none_vale_list = list(none_vale_set)
        for none_vale in none_vale_list:
            for item in sys_list:
                del item[none_vale]

        print('sys_list:', sys_list)
        return HttpResponse(json.dumps(sys_list))





'''******************** 公用 ********************'''

#构建测试用例
def build_case(request):
    if request.method == 'POST':

        release_dict = dict(request.POST)
        sys_name = release_dict['sys_name'][0]

        case_release_list = release_dict['case_release[]']

        if  'all' in case_release_list:
            public.git_code_and_build_case(sys_name)


        else:

            for  version_no in case_release_list:
                sys_name_ver= '/'.join([sys_name,version_no])
                public.git_code_and_build_case(sys_name_ver)

        return HttpResponse(json.dumps({'code': '200', 'msg': '执行成功'}, ensure_ascii=False))


def build_case_bak(request):
    if request.method == 'POST':
        print(request.POST)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        release_dict = dict(request.POST)
        case_release = release_dict['case_release[]']
        sys_name =  release_dict['sys_name'][0]
        process_count = len(case_release)

        print('sys_name:',sys_name)


        if  'all' in case_release:
            release_no_list = []

            #获取当前系统所有版本
            version_no_list = db_case_info.handel_query_special_case('ver_no')

            for ver_dict in version_no_list:
                for k, v in ver_dict.items():
                    release_no_list.append(v)

            version_no_list = list(set(release_no_list))

        else:
            version_no_list = case_release

        pc_id = str(uuid.uuid4())[-4:]
        case_task_list = []

        for  version_no in version_no_list:

            case_path = '\\'.join([sys_name,version_no])

            pid_case_path = ' '.join([pc_id,case_path])

            task = loop.create_task(  build_case_func(pid_case_path))

            case_task_list.append(task)

        loop.run_until_complete(asyncio.gather(*case_task_list))

        while True:
            already_exe_count = mc.get(pc_id)

            print('already_exe_count:',already_exe_count)

            if already_exe_count >= process_count:
                break

        return HttpResponse(json.dumps({'code': '200', 'msg': '执行成功'}, ensure_ascii=False))


#测试用例执行状态
def case_exe_status(request):
    req_data = request.body
    req_data_dict = json.loads(str(req_data, 'utf-8'))
    pc_id = req_data_dict['pc_id']

    process_count = mc.get(pc_id)
    if process_count:

        process_count = int(process_count)
        process_count += 1
        mc.set(pc_id,process_count,18000)

    else:

        mc.set(pc_id, 1,18000)

    return HttpResponse(json.dumps({'code': '200', 'msg': '回传成功'}, ensure_ascii=False))


def get_test_report(request):
    if request.method == 'POST':
        report = request.FILES.get('test_report')


        report_name = report.name
        print()
        sys_name = report_name.split('_')[0]

        report_info = {
            'sys_name':sys_name,
            'report_name':report_name,
            'create_time':get_cur_time.complete_time()
        }

        print('report_info:', report_info)

        report_save_path = os.path.join(config.dynamic_file_path, report_name)

        with open(report_save_path, 'wb') as fw:
            for data in report.chunks():
                fw.write(data)

        db_test_report.handel_save_test_report(**report_info)


        return HttpResponse(json.dumps({'code': '200', 'msg': '上传成功'}, ensure_ascii=False))


def export_case_fun(result_data_list: list):
    case_list = []

    #将元组转成 成列表
    for case in result_data_list:
        cs = list(case)
        case_list.append(cs)

    #时间格式转成成字符串
    for case in case_list:
        case[10] = str(case[10])

    # 获取列的字段信息
    fields = config.case_fields

    # 创建Excel对象
    workbook = xlwt.Workbook()

    # 添加sheet表单
    sheet = workbook.add_sheet('任务信息', cell_overwrite_ok=True)

    # 在导出报表中写上字段信息(列头)
    for field in range(len(fields)):
        sheet.write(0, field, fields[field])

    # 读取每一行每一列的信息
    for row in range(1, len(case_list) + 1):
        for col in range(0, len(fields)):
            sheet.write(row, col, case_list[row - 1][col + 1])
    export_file_name = os.path.join(config.base_dir, 'media', 'static_file', 'case_info.xls')
    workbook.save(export_file_name)
    file_path = os.path.join(config.localhost, 'media', 'static_file', 'case_info.xls').replace("\\", "/")

    response = (json.dumps({'code': '200', 'data': file_path, 'msg': '导出成功'}, ensure_ascii=False))

    return response


@check(mc)
def export_case(request):
    user_no = request.COOKIES.get('user')

    if request.method == 'POST':
        req_data = dict(request.POST)

        export_req_data = {}
        for k,v in req_data.items():
            export_req_data[k] = v[0]

        result_data_tuple = db_case_info.handel_query_case(tuple, **export_req_data)
        result_data_list = list(result_data_tuple)

        print('result_data_list:',result_data_list)

        response = export_case_fun(result_data_list)

        return HttpResponse(response)

@check(mc)
def download_report(request):
    # user_no = request.COOKIES.get('user')

    if request.method == 'POST':
        sys_name = request.POST.get('sys_name')
        if not sys_name:
            return HttpResponse(json.dumps({'code': '401', 'msg': '系统名称不能为空'}, ensure_ascii=False))

        report_name = db_test_report.handel_query_test_report(sys_name)
        print('report_name:',report_name)


        if not report_name:
            return HttpResponse(json.dumps({'code': '404', 'msg': '当前无测试报告'}, ensure_ascii=False))
        report_path = os.path.join(config.localhost, 'media', 'dynamic_file', report_name['report_name']).replace("\\", "/")

        print('report_path:',report_path)
        return  HttpResponse(json.dumps({'code': '200', 'data': report_path, 'msg': ''}, ensure_ascii=False))














        #保存测试用例


def save_test_info(request):
    if request.method == 'POST':
        req_data = request.body
        save_case_list = json.loads(str(req_data,'utf-8'))
        if len(save_case_list) > 0:
            db_case_info.handel_save_case(save_case_list)
            return HttpResponse('回传成功')

        else:
            return HttpResponse('用例不能为空')



@check(mc)
def query_sys_release(request):

    if request.method == 'POST':

        release_no_list = []

        sys_name = request.POST.get('sys_name')
        version_no = db_case_info.handel_query_special_case('ver_no',**{'sys_name':sys_name})

        for dic in version_no:
            for k, v in dic.items():
                release_no_list.append(v)

        release_no = list(set(release_no_list))


        if release_no:
            return HttpResponse(json.dumps({'code': '200','release_no':release_no, 'msg': '获取成功'}, ensure_ascii=False))
        else:
            return HttpResponse(json.dumps({'code': '400', 'release_no': release_no, 'msg': '当前无可执行用例'}, ensure_ascii=False))


def test(request):
    return  render(request,'test.html')