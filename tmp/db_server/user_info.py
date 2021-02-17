#!/anaconda3/envs/FEALPy/bin 
# -*- coding: utf-8 -*-
# @Software: PyCharm
# @File: user_info.py
# @Author: TangYong
# @Time: 十月 02, 2019


from tmp import  public
from tmp.db_server import sys_info
from tmp import  config


class UserInfoRepository:

    def __init__(self):
        self.conn = public.DBConnection()

    def handel_crate_user(self,**kwargs):

        cursor = self.conn.connect()

        sql = """ insert into user_info(%s) values(%s)"""

        key_list = []
        value_list = []

        for k, v in kwargs.items():
            key_list.append(k)
            value_list.append('%%(%s)s' % k)
        sql = sql % (','.join(key_list), ','.join(value_list))

        print('create_user sql:',sql)
        cursor.execute(sql, kwargs)
        self.conn.close()


    def handel_query_user_info(self,*args,**kwargs):
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

            sql = "select %s from user_info where %s;" % (columns, condition)

        else:
            sql = "select %s from user_info;" % (columns)

        print('查询用户信息:', sql)
        cursor.execute(sql)

        result = cursor.fetchall()

        self.conn.close()

        return result

    def hand_delete_user(self,user_no):
        cursor = self.conn.connect()

        sql = "delete  from user_info where user_no = '%s';"%user_no


        cursor.execute(sql)

        self.conn.close()


    def hand_update_user(self,**kwargs):

        cursor = self.conn.connect()

        sql_str = "update user_info  set %s = '%s' where user_no = '%s';"

        for k, v in kwargs.items():
            sql = sql_str %(k,v,kwargs['user_no'])
            print('update_user_info sql:',sql)
            cursor.execute(sql)

        self.conn.close()


    # def get_user_sys_list(self,user_no):
    #     '''
    #     根据用户编号查询锁拥有的系统列表
    #     :param user_no:  用户编号
    #     :return: 系统列表(list[sys_no])
    #     '''
    #     user_sys_menu_dict = {}
    #     cursor = self.conn.connect()
    #     sql =  "select sys_no from user_info where user_no = '%s' ;"%(user_no)
    #     cursor.execute(sql)
    #
    #     get_user_info = cursor.fetchall()
    #
    #
    #     if get_user_info:
    #         sys_no_list = get_user_info[0]['sys_no']
    #         if sys_no_list:
    #             sys_no_list = sys_no_list.split(',')
    #
    #
    #
    #
    #
    #
    #
    #             for sys_no in sys_no_list:
    #                 user_sys_menu_dict[sys_no] = config.sys_menu_dict.get(sys_no)
    #             return [user_sys_menu_dict,sys_no_list]
    #         else:
    #             print('sys_no_list:',sys_no_list)
    #             return None
    #     else:
    #         return None


    def get_user_sys_list(self, user_no):
        '''
        根据用户编号查询锁拥有的系统列表
        :param user_no:  用户编号
        :return: 系统编号、菜单路由列表
        '''
        user_sys_menu_dict = {}
        cursor = self.conn.connect()
        sql = "select sys_no from user_info where user_no = '%s' ;" % (user_no)
        cursor.execute(sql)

        get_user_info = cursor.fetchall()

        if get_user_info:
            sys_no_list = get_user_info[0]['sys_no']
            if sys_no_list:
                sys_no_list = sys_no_list.split(',')

                # 从系统管理中获取所有系统菜单名称以及对应的菜单路由
                db_sys_info = sys_info.SysInfoRepository()
                sys_menu_dict = db_sys_info.handel_by_sys_no_gen_menu()

                # 根据系统编号动态生成对应的菜单路由如：/afSys
                for sys_no in sys_no_list:
                    user_sys_menu_dict[sys_no] = sys_menu_dict.get(sys_no)
                return [user_sys_menu_dict, sys_no_list]

            else:
                return None
        else:
            return None




if __name__ =='__main__':
    user = UserInfoRepository()
    r = user.get_user_sys_list('admin')
    print(r)







