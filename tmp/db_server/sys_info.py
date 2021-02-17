#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Software: PyCharm
# @File: sys_info.py
# @Author: TangYong
# @Time: 五月 03, 2020



from tmp import public

class SysInfoRepository:

    def __init__(self):
        self.conn = public.DBConnection()

    def handel_create_sys(self,**kwargs):

        cursor = self.conn.connect()

        sql = """ insert into sys_manage(%s) values(%s)"""

        key_list = []
        value_list = []

        for k, v in kwargs.items():
            key_list.append(k)
            value_list.append('%%(%s)s' % k)
        sql = sql % (','.join(key_list), ','.join(value_list))

        cursor.execute(sql, kwargs)
        self.conn.close()


    def handel_query_sys(self, *args, **kwargs):

        cursor = self.conn.connect()

        if len(args) == 0:
            columns = '*'
        elif len(args) == 1:
            columns = str(args).replace('(', '').replace(')', '').replace("'", '')[:-1]
        else:
            columns = str(args).replace('(', '').replace(')', '').replace("'", '')

        # 添加空值
        null_value_list = []
        for k, v in kwargs.items():
            if not v:
                null_value_list.append(k)

        # 删除空值
        if null_value_list:
            for k in null_value_list:
                del kwargs[k]

        condition = ''
        for k, v in kwargs.items():
            condition += " %s = '%s' and " % (k, v)
        condition = condition.strip()[:-4]


        if condition:

            sql = "select %s from sys_manage where %s;"%(columns,condition)

        else:
            sql = "select %s from sys_manage;"%(columns)


        print('查询系统信息:', sql)
        cursor.execute(sql)

        result = cursor.fetchall()

        self.conn.close()

        return result


    def hand_delete_sys(self,sys_no):
        cursor = self.conn.connect()

        sql = "delete  from sys_manage where sys_no = '%s';"%sys_no

        cursor.execute(sql)

        self.conn.close()


    def hand_update_sys(self,**kwargs):

        cursor = self.conn.connect()

        sql_str = "update sys_manage  set %s = '%s' where sys_no = '%s';"

        for k, v in kwargs.items():
            sql = sql_str %(k,v,kwargs['sys_no'])

            cursor.execute(sql)

        self.conn.close()


    def handel_by_sys_no_gen_menu(self):
        '''
        根据系统编号生成菜单路由
        :return:  菜单路由
        '''
        sys_menu_dict = {}
        cursor = self.conn.connect()
        sql = "select sys_no from sys_manage"
        cursor.execute(sql)
        result_list = cursor.fetchall()

        #根据系统编号生成菜单路由
        for result in result_list:
            for k,v in result.items():
                sys_menu_dict[v] = '/%sSys' % (v).lower()
        self.conn.close()

        return sys_menu_dict



if __name__ ==  '__main__':
    bd_sys = SysInfoRepository()
    bb = bd_sys.handel_by_sys_no_gen_menu()
    print(bb)