#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Software: PyCharm
# @File: test.py
# @Author: TangYong
# @Time: 五月 23, 2020



import winrm


def exe_remote_win_cmd(host='hostip', username='username', password='password'):
    """
    在 windows 下执行命令
    :param host: 远程Windows服务器IP
    :param username: 远程Windows服务器用户名
    :param password: 远程Windows服务器密码
    :return:
    """
    remote_win = winrm.Session('http://' + host + ':5985/wsman', auth=(username, password))

    cmd_res = remote_win.run_cmd(
        'D:'
        '& cd Python'
        '& python.exe D:\\jcmro\\bin\\build_case.py team\\iter_x'

    ) #多个命令使用 & 符号连接

    print(str(cmd_res.std_err, 'GBK'))
    print(str(cmd_res.std_out,'GBK'))






# D:\jcmro\bin\build_case.py

if __name__ == '__main__':
    # exe_remote_win_cmd('192.168.83.1','admin','admin')

    # from winrm.protocol import Protocol
    #
    # p = Protocol(
    #     endpoint='http://192.168.83.1:5985/wsman',
    #     transport='ntlm',
    #     username=r'admin',
    #     password='admin',
    #     server_cert_validation='ignore')
    # shell_id = p.open_shell()
    # command_id = p.run_command(shell_id, 'ipconfig', ['/all'])
    # std_out, std_err, status_code = p.get_command_output(shell_id, command_id)
    # p.cleanup_command(shell_id, command_id)
    # print(std_out, status_code)
    # p.close_shell(shell_id)
    # lis = ['a','b']
    # print(','.join(lis))

    sys_data_dict={'AC': {'passed': ['Passed'], 'failed': [], 'error': [], 'AC': '/acSys'},
                    'AF': {'passed': ['Passed'], 'failed': ['Failed'], 'error': ['Error'], 'AF': '/afSys'},
                    'W': {'passed': [], 'failed': [], 'error': [], 'W': '/wSys'}}
    all_sys_menu_dict = {}
    for  key,val in sys_data_dict.items():
      for k,v in val.items():
          if k == key:
              sys_menu_dict={ k:v}
              all_sys_menu_dict.update(sys_menu_dict)

    print(all_sys_menu_dict)



