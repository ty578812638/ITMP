#!/anaconda3/envs/FEALPy/bin 
# -*- coding: utf-8 -*-
# @Software: PyCharm
# @File: test_report.py
# @Author: TangYong
# @Time: 十月 02, 2019


from tmp import  public


class TestReportInfoRepository:

    def __init__(self):
        self.conn = public.DBConnection()

    def handel_save_test_report(self,**kwargs):
        cursor = self.conn.connect()

        sql = """ insert into sys_test_report(%s) values(%s)"""

        key_list = []
        value_list = []

        for k, v in kwargs.items():
            key_list.append(k)
            value_list.append('%%(%s)s' % k)
        sql = sql % (','.join(key_list), ','.join(value_list))

        print('save_test_report:',sql)
        cursor.execute(sql,kwargs)

        self.conn.close()


    def handel_query_test_report(self,sys_name):
        cursor = self.conn.connect()

        sql = " select report_name from sys_test_report where sys_name = '%s' order by create_time desc; "%sys_name

        print('query_test_report:', sql)
        cursor.execute(sql)

        result = cursor.fetchone()

        self.conn.close()

        return result




if __name__ =='__main__':
    reportInfo = TestReportInfoRepository()
    report_name = reportInfo.handel_query_test_report('NAC')
    print(report_name)





