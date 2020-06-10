# !/user/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/5/12 21:11
# @Author  : chineseluo
# @Email   : 848257135@qq.com
# @File    : run.py
# @Software: PyCharm
import os
import sys
import json
import time
import logging
import pytest
from os import path
from Common.publicMethod import PubMethod

root_dir = os.path.dirname(__file__)
config_yaml = PubMethod.read_yaml("./Conf/config.yaml")


def modify_report_environment_file(report_widgets_dir):
    """
    向environment.json文件添加测试环境配置，展现在allure测试报告中
    @return:
    """
    environment_info = [
        {"name": '测试地址', "values": [config_yaml['allure_environment']['URL']]},
        {"name": '测试版本号', "values": [config_yaml['allure_environment']["version"]]},
        {"name": '测试账户', "values": [config_yaml['allure_environment']['username']]},
        {"name": '测试说明', "values": [config_yaml['allure_environment']['description']]}
    ]
    # 确保目录存在
    PubMethod.create_dirs(os.path.join(report_widgets_dir, 'widgets'))
    with open(report_widgets_dir + '/widgets/environment.json', 'w', encoding='utf-8') as f:
        json.dump(environment_info, f, ensure_ascii=False, indent=4)


# 保存历史数据
def save_history(history_dir, dist_dir):
    if not os.path.exists(os.path.join(dist_dir, "history")):
        PubMethod.create_dirs(os.path.join(dist_dir, "history"))
    else:
        # 遍历报告report下allure-report下的history目录下的文件
        for file in os.listdir(os.path.join(dist_dir, "history")):
            old_data_dic = {}
            old_data_list = []
            # 1、从report下allure-report下的history目录下的文件读取最新的历史纪录
            with open(os.path.join(dist_dir, "history", file), 'rb') as f:
                new_data = json.load(f)
            # 2、从Report下的history(历史文件信息存储目录)读取老的历史记录
            try:
                with open(os.path.join(history_dir, file), 'rb') as fr:
                    old_data = json.load(fr)
                    if isinstance(old_data, dict):
                        old_data_dic.update(old_data)
                    elif isinstance(old_data, list):
                        old_data_list.extend(old_data)
            except Exception as fe:
                print("{}文件查找失败信息：{}，开始创建目标文件！！！".format(history_dir, fe))
                PubMethod.create_file(os.path.join(history_dir, file))
            # 3、合并更新最新的历史纪录到report下的history目录对应浏览器目录中
            with open(os.path.join(history_dir, file), 'w') as fw:
                if isinstance(new_data, dict):
                    old_data_dic.update(new_data)
                    json.dump(old_data_dic, fw, indent=4)
                elif isinstance(new_data, list):
                    old_data_list.extend(new_data)
                    json.dump(old_data_list, fw, indent=4)
                else:
                    print("旧历史数据异常")


# 导入历史数据
def import_history_data(history_save_dir, result_dir):
    if not os.path.exists(history_save_dir):
        print("未初始化历史数据！！！进行首次数据初始化")
    else:
        # 读取历史数据
        for file in os.listdir(history_save_dir):
            # 读取最新的历史纪录
            with open(os.path.join(history_save_dir, file), 'rb') as f:
                new_data = json.load(f)
            # 写入目标文件allure-result中，用于生成趋势图
            PubMethod.create_file(os.path.join(result_dir, "history", file))
            try:
                with open(os.path.join(result_dir, "history", file), 'w') as fw:
                    json.dump(new_data, fw, indent=4)
            except Exception as fe:
                print("文件查找失败信息：{}，开始创建目标文件".format(fe))


# 运行命令参数配置
def run_all_case(browser, browser_opt, type_driver):
    # 测试结果文件存放目录
    result_dir = os.path.abspath("./Report/{}/allure-result".format(browser))
    # 测试报告文件存放目录
    report_dir = os.path.abspath("./Report/{}/allure-report".format(browser))
    # 测试历史结果文件存放目录，用于生成趋势图
    history_dir = os.path.abspath("./Report/history/{}".format(browser))
    PubMethod.create_dirs(history_dir)
    # 定义测试用例features集合
    allure_features = ["--allure-features"]
    allure_features_list = [
        # 'Register_page_case',
        'Login_page_case'
    ]
    allure_features_args = ",".join(allure_features_list)
    # 定义stories集合
    allure_stories = ["--allure-stories"]
    allure_stories_args = ['']
    allure_path_args = ['--alluredir', result_dir, '--clean-alluredir']
    test_args = ['-s', '-q', '--browser={}'.format(browser), '--browser_opt={}'.format(browser_opt), '--type_driver={}'.format(type_driver)]
    # 拼接运行参数
    run_args = test_args + allure_path_args + allure_features + [
        allure_features_args] + allure_stories + allure_stories_args
    # 使用pytest.main
    pytest.main(run_args)
    # 导入历史数据
    import_history_data(history_dir, result_dir)
    # 生成allure报告，需要系统执行命令--clean会清楚以前写入environment.json的配置
    cmd = 'allure generate ./Report/{}/allure-result -o ./Report/{}/allure-report --clean'.format(
        browser.replace(" ", "_"),
        browser.replace(" ", "_"))
    logging.info("命令行执行cmd:{}".format(cmd))
    try:
        os.system(cmd)
    except Exception as e:
        logging.error('命令【{}】执行失败！'.format(cmd))
        sys.exit()
    # 定义allure报告环境信息
    modify_report_environment_file(report_dir)
    # 保存历史数据
    save_history(history_dir, report_dir)
    # 打印url，方便直接访问
    url = '本地报告链接：http://127.0.0.1:63342/{}/Report/{}/allure-report/index.html'.format(root_dir.split('/')[-1],
                                                                                     browser.replace(" ", "_"))
    print(url)


# 命令行参数运行
def receive_cmd_arg():
    global root_dir
    input_browser = sys.argv
    if len(input_browser) > 1:
        try:
            if input_browser[1] == "chrome":
                root_dir.replace("\\", "/")
                root_dir = root_dir.replace("\\", "/")
                run_all_case(input_browser[1], input_browser[2], input_browser[3])
            elif input_browser[1] == "firefox":
                root_dir = root_dir.replace("\\", "/")
                run_all_case(input_browser[1], input_browser[2], input_browser[3])
            elif input_browser[1] == "ie":
                root_dir.replace("\\", "/")
                root_dir = root_dir.replace("\\", "/")
                run_all_case("ie", input_browser[2], input_browser[3])
            else:
                logging.error("参数错误，请重新输入！！！")
        except Exception as e:
            logging.error("命令行传参错误信息：{}".format(e))
    else:
        run_all_case("chrome", "close", "remote")


if __name__ == "__main__":
    receive_cmd_arg()

