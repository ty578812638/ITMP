# -*- coding: utf-8 -*-
# @Software: PyCharm
# @File: case_info.py
# @Author: TangYong
# @Time: 五月 02, 2020

import pymysql
from tmp import public


get_cur_time = public.GetCurrentTime()


class CaseInfoRepository:

    def __init__(self):
        self.conn = public.DBConnection()

    def handel_save_case(self, case_list: list):
        cursor = self.conn.connect()
        key_list = []
        value_list = []
        add_sql = """ insert into case_info(%s) values(%s)"""

        for case in case_list:
            for k, v in case.items():
                key_list.append(k)
                value_list.append('%%(%s)s' % k)
            addSql = add_sql % (','.join(key_list), ','.join(value_list))

            try:
                cursor.execute(addSql, case)

            except Exception as e:
                print('保存测试用例异常信息:', e)

                    # uqe_case_no 表示重复插入错误
                if 'uqe_case_no' in str(e):
                    # 获取重复插入的用例编号
                    case_no = str(e).split("'")[1]
                    update_sql = "update case_info  set %s = '%s' where case_no = '%s';"
                    case['update_time'] = get_cur_time.complete_time()
                    for k, v in case.items():
                        updateSql = update_sql % (k, v, case_no)
                        cursor.execute(updateSql)
            finally:

                # 使数据恢复到初始状态
                add_sql = """ insert into case_info(%s) values(%s)"""
                key_list.clear()
                value_list.clear()

        self.conn.close()


    # def handel_save_case(self, **test_case:dict):
    #     cursor = self.conn.connect()
    #     key_list = []
    #     value_list = []
    #     add_sql = """ insert into case_info(%s) values(%s)"""
    #
    #
    #     for k, v in test_case.items():
    #         key_list.append(k)
    #         value_list.append('%%(%s)s' % k)
    #     addSql = add_sql % (','.join(key_list), ','.join(value_list))
    #
    #     try:
    #         cursor.execute(addSql, test_case)
    #
    #     except Exception as e:
    #
    #         print('保存测试用例异常信息:', e)
    #
    #             # uqe_case_no 表示重复插入错误
    #         if 'uqe_case_no' in str(e):
    #             # 获取重复插入的用例编号
    #             case_no = str(e).split("'")[1]
    #             update_sql = "update case_info  set %s = '%s' where case_no = '%s';"
    #             test_case['update_time'] = get_cur_time.complete_time()
    #             for k, v in test_case.items():
    #                 updateSql = update_sql % (k, v, case_no)
    #                 cursor.execute(updateSql)
    #     finally:
    #
    #         # 使数据恢复到初始状态
    #         add_sql = """ insert into case_info(%s) values(%s)"""
    #         key_list.clear()
    #         value_list.clear()
    #
    #     self.conn.close()


    def handel_query_case(self, data_type=None, **kwargs):
        if data_type:
            cursor = self.conn.connect(pymysql.cursors.Cursor)
        else:
            cursor = self.conn.connect()

        order = ' order by update_time desc;'
        other_condition = ''
        time_condition = ''
        sql_str = "select *  from case_info where  "

        start_time = kwargs.get('create_time')
        if start_time:
            time_condition = "create_time >= '%s'" % start_time
            del kwargs['create_time']

        end_time = kwargs.get('end_time')
        if end_time:
            time_condition = "create_time <= '%s'" % end_time
            del kwargs['end_time']

        if start_time and end_time:
            time_condition = "create_time >= '%s' and create_time <= '%s'" % (start_time, end_time)

        # try:
        #     if kwargs['create_time']:
        #         start_time = kwargs['create_time']
        #         time_condition = "create_time >= '%s'" % start_time
        #
        #     if kwargs['end_time']:
        #         end_time = kwargs['end_time']
        #         time_condition = "create_time <= '%s'" % end_time
        #
        #     if kwargs['start_date'] and kwargs['end_date']:
        #         start_time = kwargs['start_date']
        #         end_time = kwargs['end_date']
        #         time_condition = "create_time >= '%s' and create_time <= '%s'" % (start_time, end_time)
        #
        #     del kwargs['create_time']
        #     del kwargs['end_time']
        #
        # except Exception:
        #     pass

        # 添加空值
        null_value_list = []
        for k, v in kwargs.items():
            if not v:
                null_value_list.append(k)

        # 删除空值
        if null_value_list:
            for k in null_value_list:
                del kwargs[k]

        for k, v in kwargs.items():
            other_condition += " %s = '%s' and " % (k, v)
        other_condition = other_condition.strip()[:-4]

        # print('other_condition:', other_condition)
        # print('time_condition:', time_condition)

        if time_condition and other_condition:

            sql = sql_str + time_condition + ' and ' + other_condition + order

        elif time_condition:

            sql = sql_str + time_condition + order

        elif other_condition:

            sql = sql_str + other_condition + order

        else:

            sql = "select *  from case_info  " + order

        print('query_case_info:', sql)
        cursor.execute(sql)

        result = cursor.fetchall()

        self.conn.close()

        return result


    def handel_query_special_case(self, *args, **kwargs):
        cursor = self.conn.connect()
        if len(args) == 0:
            columns = '*'
        else:
            columns = str(args).replace('(', '').replace(')', '').replace("'", '')[:-1]

        is_null = ''
        condition = ''

        for k, v in kwargs.items():
            is_null += v

        if is_null == '':
            sql = " select %s from case_info " % columns

        else:
            for k, v in kwargs.items():
                condition += " %s = '%s' and " % (k, v)

            sql = " select %s from case_info where %s" % (columns, condition)

            sql = sql.strip()[:-4]

        print('sql:', sql)

        cursor.execute(sql)

        result = cursor.fetchall()

        self.conn.close()

        return result


    def handel_query_case_by_sys(self, *args, **kwargs):
        cursor = self.conn.connect()
        sql_str = "select  *  from case_info "

        sys_condition = ''
        other_condition = ''

        order = ' order by update_time desc;'

        if args:
            if len(args) > 1:
                sys_condition = " sys_name in {}".format(args)

            else:
                sys_condition = " sys_name in ('%s')" % args

        if kwargs:
            for k, v in kwargs.items():
                other_condition += " %s = '%s' and " % (k, v)
            other_condition = other_condition.strip()[:-4]

        if sys_condition and other_condition:
            sql = sql_str + 'where ' + sys_condition + ' and ' + other_condition + order

        elif sys_condition:
            sql = sql_str + 'where ' + sys_condition + order

        elif other_condition:
            sql = sql_str + 'where ' + other_condition + order

        else:
            sql = sql_str + order

        print('sql:', sql)
        cursor.execute(sql)

        result = cursor.fetchall()

        self.conn.close()

        return result


if __name__ == '__main__':
    db_case_info = CaseInfoRepository()
    r= db_case_info.handel_query_case(None,**{'sys_name':'af'})
    r1 = r[0]['create_time']
    print(str(r1))
    test_info = {
        'sys_name': 'AF',
        'ver_no': '123',
        'case_no': '122',  # 用例编号
        'case_name': 'test',  # 用例名称
        'case_story': '测试场景',  # 测试 场景
        'exp_res': '预期结果',  # 预期结果
        'act_res': '实际结果',  # 实际结果
        'test_res': 'Passed',  # 测试结果
        'tester': 'tangyong',


    }


    # passed_list = []
    # failed_list = []
    # error_list = []
    # sys_list = []
    # sys_list = []
    #
    # for data in all_data_list:
    #   for k,v in data.items():
    #       if v == 'passed':
    #           passed_list.append(v)
    #       if v == 'failed':
    #           failed_list.append(v)
    #       if v == 'error':
    #           error_list.append(v)
    #       if  k == 'sys_name':
    #           sys_list.append(v)
    #
    #       if k ==  'NAC,team':
    #           sys_list.append()
    #
    #
    #
    # print('passed_list:', passed_list)
    # print('failed_list:', failed_list)
    # print('failed_list:', error_list)
    # print('sys_list:', list(set(sys_list)))
