#!/user/bin/env python
# -*- coding: utf-8 -*-

"""
------------------------------------
@Project : ui_auto
@Time    : 2020/6/15 13:49
@Auth    : luozhongwen
@Email   : luozw@inhand.com.cn
@File    : ci_result.py
@IDE     : PyCharm
------------------------------------
"""
import os
import json
import sys

if __name__ == '__main__':
    result_file_path = os.path.abspath('./Report/chrome/allure-report/widgets/summary.json')
    print('文件路径：', result_file_path)
    with open(result_file_path, 'rb') as f:
        result = json.load(f)['statistic']
    print('测试结果：', result)
    if result['failed'] > 0 or result['broken'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)
