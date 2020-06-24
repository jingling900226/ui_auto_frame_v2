# -*- coding: utf-8 -*-
# @Time    : 2018/7/19 下午5:23
# @Author  : liwei
# @File    : Email.py

"""
封装邮件等相关操作

"""
import smtplib
import imaplib
import json
import time
import sys
import re
import os
import email
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import Parser
from Common.publicMethod import PubMethod
from imapclient import IMAPClient

config_path = os.path.join(os.path.dirname(__file__).split("Common")[0], "Conf/config.yaml")
config_yaml = PubMethod.read_yaml(config_path)
email_info = config_yaml["mail_info"]


class Mail:

    def rec_email(self, sender, pattern):
        """
        根据正则表达式匹配邮件中想要的内容，车载项目在注册确认链接正则（r'<a href="(.*?)"'）返回列表中
        第二个元素, 不存在的返回None, 只接收最新的一封邮件
        :param sender: 查找从哪个发件人发送的当天邮件
        :param pattern: 正则表达式
        :return: 返回符合正则表达式的列表
        """
        today_s = str(time.strftime("%d-%b-%Y"))
        server = IMAPClient(host=email_info["imap_server"], ssl=True)
        try:
            server.login(email_info["email_username"], email_info["email_password"])
            print(server.list_folders())
            print("已登录进入")
        except server.Error:
            print('Could not log in')
            sys.exit(1)
        #  选取收件箱 只读模式
        select_info = server.select_folder('INBOX', readonly=True)
        #  在收件箱里按照时间和发件人来搜索过滤邮件， 该方法无法筛选发件人无效，在以下处理为最新一封邮件
        messages = server.search(['TEXT', sender, 'SINCE', today_s])
        #  获取邮件内容、结果为两部分邮件id和邮件内容
        server_fetch = server.fetch(messages, ['BODY.PEEK[]'])
        u_id_list = []
        if server_fetch.items():
            # u_id 最大的为最新的一封邮件。先把所有的u_id保存到一个列表
            for u_id, message in server_fetch.items():
                # 校验发送者，当前只支持一个发送者，不考虑多个
                u_id_list.append(u_id)
                # print(message.keys())
            # 只有当最大的u_id时才做URL的查找，不然其他邮件根本就匹配不到。
            for u_id, message in server_fetch.items():
                if u_id == max(u_id_list):
                    url = self.get_url(message, pattern)
                    print("url:{}".format(url))
            return url
        else:
            return None

    def assert_email(self, sender, expect: list, receive='', receive_pw=''):
        """
        校验当天发送邮件里面的内容，如果有返回True，如果无返回False
        :param receive_pw: 邮件接收者密码。默认是ABc124
        :param receive:  邮件接收者，默认是test@inhand.com.cn
        :param sender:  邮件发送者
        :param expect:  校验内容（邮件内容转换为Html格式，某个指定标签里面的内容），
                        列表格式，可验证最近多封邮件。
        :return:   True, False
        """
        today_s = str(time.strftime("%d-%b-%Y"))
        server = IMAPClient(host=email_info["imap_server"], ssl=True)
        if receive == "" and receive_pw == "":
            receive_email = email_info["email_username"]
            receive_email_pw = email_info["email_password"]
        else:
            receive_email = receive
            receive_email_pw = receive_pw
        try:
            server.login(receive_email, receive_email_pw)
            print("已登录进入")
        except server.Error:
            print('Could not log in')
            sys.exit(1)
        select_info = server.select_folder('INBOX', readonly=True)
        messages = server.search(['TEXT', sender, 'SINCE', today_s])
        server_fetch = server.fetch(messages, ['BODY.PEEK[]'])
        all_content = []
        # 校验当天所有的邮件中是否包含期望的内容
        if server_fetch.items():
            for u_id, messages in server_fetch.items():
                e = email.message_from_string(messages[b'BODY[]'].decode())
                # 校验发送者，当前只支持一个发送者，不考虑多个
                mail_from = email.header.decode_header(e['From'])
                if '<' + sender + '>' in mail_from[0][0].split(" "):
                    all_content.append(self.get_mail_content(e))
        if len(all_content) == 0:
            raise AssertionError("未搜索到今日相关发送邮件")
        else:
            all_content_str = "".join(all_content[0:])
            for i in expect:
                assert (i in all_content_str)

    @staticmethod
    def get_url(message, pattern):
        e = email.message_from_string(message[b'BODY[]'].decode("gb2312"))  # 生成Message类型
        html = ''
        for part in e.walk():
            html = part.get_payload(decode=True)
        #  正则获取html的url链接
        pat = re.compile(pattern)
        # pat = re.compile(r'<a href="(.*?)"')
        res = pat.findall(html.decode("utf-8"))
        print("res:{}".format(res))
        return res

    @staticmethod
    def get_mail_content(msg):
        if msg is None:
            return None
        for part in msg.walk():
            if not part.is_multipart():
                data = part.get_payload(decode=True)
        return data.decode("utf-8")

    # 解析邮件内容
    @staticmethod
    def get_body(msg):
        if msg.is_multipart():
            return msg.get_body(msg.get_payload(0))
        else:
            return msg.get_payload(None, decode=True)


    def delete_email(self, receive, receive_pw, date=''):
        """
        删除Inbox里面的邮件。
        :param date:  时间默认是今日，当然也可以传入， 格式为"%d-%b-%Y"
        :param receive_pw: 邮件接收者密码。默认是ABc124
        :param receive:  邮件接收者，默认是test@inhand.com.cn
        :return:   True, False
        """
        if date:
            today_s = date
        else:
            today_s = str(time.strftime("%d-%b-%Y"))
        if receive and receive_pw:
            receive_email = receive
            receive_email_pw = receive_pw
        else:
            receive_email = email_info["email_username"]
            receive_email_pw = email_info["email_password"]
        box = imaplib.IMAP4_SSL(email_info["imap_server"], 993)
        box.login(receive_email, receive_email_pw)
        box.select('Inbox')
        # 如果是查找收件箱所有邮件则是box.search(None, 'ALL')
        typ, data = box.search(None, 'SINCE', today_s)
        for num in data[0].split():
            box.store(num, '+FLAGS', '\\Deleted')
        box.expunge()
        box.close()
        box.logout()


if __name__ == '__main__':
    # mail = Mail()
    # res = mail.rec_email("customer-service@inhand.com.cn", r'[0-9]{6}\r\n')
    # print(res[0].split("\\r\\n")[0])
    print(config_path)
