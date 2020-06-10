# !/user/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/6/4 9:14
# @Author  : luozhongwen
# @Email   : luozw@inhand.com.cn
# @File    : test_script.py
# @Software: PyCharm
import os
import logging
from Common.publicMethod import PubMethod
from selenium.webdriver.common.by import By

login_elem_data = os.path.join(os.path.dirname(__file__), "Login_page.yaml")


c = {
    "a": 11,
    "b": 22
}
c["d"] = 33
print(c)