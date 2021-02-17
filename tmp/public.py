#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Software: PyCharm
# @File: public.py
# @Author: TangYong
# @Time: 五月 02, 2020
import os

import uuid
import time
import winrm
import hashlib
import psutil
import random
import pymysql
import paramiko
import memcache
from tmp import config

mc = memcache.Client([config.mem_cache], debug=True)

from tmp import  config



class GetCurrentTime:

    def __init__(self):
        self.current_time = time.localtime()

    def all_number_time(self):

        year = (self.current_time[0])
        year = str(year)

        month = self.current_time[1]
        if month < 10:
            month = ''.join(['0', str(month)])
        else:
            month = str((self.current_time[1]))

        day = self.current_time[2]
        if day < 10:
            day = ''.join(['0', str(day)])
        else:
            day = str((self.current_time[2]))

        hour = self.current_time[3]
        if hour < 10:
            hour = ''.join(['0', str(hour)])
        else:
            hour = str((self.current_time[3]))

        # min = self.current_time[4]
        # if min < 10:
        #     min = ''.join(['0', str(min)])
        # else:
        #     min = str((self.current_time[4]))

        final_time = ''.join([year, month, day, hour])

        return final_time

    def year_mont_day(self):

        year = (self.current_time[0])
        year = str(year)

        month = self.current_time[1]
        if month < 10:
            month = ''.join(['0', str(month)])
        else:
            month = str((self.current_time[1]))

        day = self.current_time[2]
        if day < 10:
            day = ''.join(['0', str(day)])
        else:
            day = str((self.current_time[2]))

        final_date = '/'.join([year, month, day])

        return final_date

    def hour_min_sec(self):

        hour = self.current_time[3]
        if hour < 10:
            hour = ''.join(['0', str(hour)])
        else:
            hour = str((self.current_time[3]))

        min = self.current_time[4]
        if min < 10:
            min = ''.join(['0', str(min)])
        else:
            min = str((self.current_time[4]))

        sec = self.current_time[4]

        if sec < 10:
            sec = ''.join(['0', str(sec)])
        else:
            sec = str((self.current_time[4]))

        final_time = ':'.join([hour, min, sec])

        return final_time

    @classmethod
    def complete_time(cls):
        return  time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

class Linux(object):
    # 通过IP, 用户名，密码，超时时间初始化一个远程Linux主机
    def __init__(self, ip, username, password, port=22, timeout=100):
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.username = username
        self.password = password

        # 链接失败的重试次数
        self.try_times = 5

        # 创建客户端对象
        self.ssh = paramiko.SSHClient()

        # 创建文件传输对象
        # self.transport = paramiko.Transport((self.ip, self.port))
        self.transport = paramiko.Transport((self.ip, self.port))

    # 调用该方法连接远程主机
    def conn_linux(self):
        while True:
            # 连接过程中可能会抛出异常，比如网络不通、链接超时
            try:
                # 允许连接不在know_hosts文件中的主机
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password,
                                 timeout=self.timeout)

                print('连接【%s】成功' % self.ip)

                return '200'

            except Exception as e:
                print('错误信息:', e)
                if self.try_times != 0:
                    print(u'连接【%s】失败，进行重试' % self.ip)
                    self.try_times -= 1
                    return str(e)
                else:
                    print('重试3次失败，结束程序', e)
                    return str(e)

    # 断开连接
    def close(self):
        self.ssh.close()
        self.transport.close()
        # self.sftp.close()

    def execute_cmd(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        result = stdout.read().decode('utf-8')
        return result

        # 获得命令执行结果

    def get_cmd_result(self, cmd):

        result = self.execute_cmd(cmd)

        return result

    # 下载文件
    def download(self, remote_path, local_path):
        self.transport.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        self.sftp.get(remote_path, local_path)
        self.close()

    # 上传文件
    def upload(self, local_path, remote_path):
        self.transport.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        self.sftp.put(local_path, remote_path)
        self.close()

class DBConnection:
    '''
    数据库链接
    '''
    def __init__(self):
        self.__conn_dict =config.mysql_conn
        self.conn = None
        self.cursor = None

    def connect(self, cursor=pymysql.cursors.DictCursor):
        # 创建数据库连接
        self.conn = pymysql.connect(**self.__conn_dict)

        # 创建游标
        self.cursor = self.conn.cursor(cursor=cursor)
        return self.cursor

    def close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def close_conn(self):
        self.cursor.close()
        self.conn.close()


def md5_encrypt( text):
    md5 = hashlib.md5()
    md5.update(text.encode('utf-8'))
    encrypt = md5.hexdigest()
    return encrypt

def generate_md5_pwd(pwd, md5_salt=None):


    if md5_salt is None:
        # 生成盐值
        md5_salt = ''
        for i in range(24):
            salts = random.choice([chr(random.randint(65, 90)), chr(random.randint(97, 122))])
            md5_salt += salts

    pwd_str = ''.join([pwd, md5_salt])



    md5_pwd = md5_encrypt(pwd_str)



    return [md5_pwd, md5_salt]


def generate_token(user):
    # get_time = GetCurrentTime()
    # date_str = get_time.year_mont_day()
    # date_str = str(date_str).replace('-', '')
    #
    # encryptAndDecrypt = EncryptAndDecrypt()
    #
    # serial_number = ''
    # number_list = [0,1,2,3,4,5,6,7,8,9]
    #
    # for i in range(6):
    #     serial_number += str(random.choice(number_list))
    #
    # token_str = ''.join([user, date_str, serial_number])
    #
    # token = encryptAndDecrypt.md5_encrypt(token_str)
    # encryptAndDecrypt = EncryptAndDecrypt()
    token_user = user
    token_uuid = str(uuid.uuid4()).replace('-', '')
    token_str = ''.join([token_user, token_uuid])
    # token = encryptAndDecrypt.md5_encrypt(token_str)
    token = md5_encrypt(token_str)
    return token


def update_token(request, user, html_page):
    token = request.COOKIES.get('token')
    html_page.set_cookie('user', user, max_age=config.timeout)
    html_page.set_cookie('token', token, max_age=config.timeout)
    return html_page



def exe_remote_win_cmd(host, username, password,case_info):
    """
    在 windows 下执行命令
    :param host: 远程Windows服务器IP
    :param username: 远程Windows服务器用户名
    :param password: 远程Windows服务器密码
    :return:
    """
    remote_win = winrm.Session('http://' + host + ':5985/wsman', auth=(username, password))

    #先判断远程PC知否可用
    remote_win.run_cmd(
        'D:'
        '& cd Python'
        '& python.exe D:\\jcmro\\bin\\pc_status.py %s'%case_info

    )  # 多个命令使用 & 符号连接
    pc_is_enable = mc.get('5')

    print('pc_is_enable:',pc_is_enable)

    if pc_is_enable != True:
        return False

    cmd_res = remote_win.run_cmd(
        'D:'
        '& cd Python'
        '& python.exe D:\\jcmro\\bin\\build_case.py %s'%case_info

    ) #多个命令使用 & 符号连接


    print(str(cmd_res.std_err, 'GBK'))
    str(cmd_res.std_out,'GBK')


def git_code_and_build_case(case_file_name =''):

    linux = Linux(config.case_exe_dev_info['host'],config.case_exe_dev_info['user'],config.case_exe_dev_info['pwd'])
    linux.conn_linux()
    project_bak = config.project_root_path+'.bak'
    start_time = time.time()

    linux.execute_cmd(f'mv {config.project_root_path} {project_bak}')
    linux.execute_cmd(f'cd /usr/src/;pwd; {config.gitlab_host}')

    while True:
        cmd_result = linux.execute_cmd(f'ls -l {config.case_build_path}')
        if cmd_result:
            time.sleep(5)
            print(f'命令:python3 {config.case_build_path} {case_file_name}')
            case_result = linux.execute_cmd(f'python3 {config.case_build_path} {case_file_name}')
            linux.execute_cmd(f'rm -rf {project_bak}')
            time.sleep(1)
            print('新代码执行完毕,执行结果:',case_result)
            break

        else:
            time.sleep(1)
            if time.time() - start_time > 120:
                linux.execute_cmd(f'mv {project_bak} {config.project_root_path}')
                linux.execute_cmd(f'python3 {config.case_build_path} {case_file_name}')
                print('旧代码执行完毕')
                break

    linux.close()
















if __name__ == '__main__':
    pass
    # sys_no_dict = get_user_sys_list('t3')
    # print(sys_no_dict[1])
    #
    # import sys
    # r = exe_remote_win_cmd('192.168.83.1', 'tangyong', 'tangyong','pid 5 team')
    # print(r)
    # git_code_and_build_case('AF/8040')

