# coding:utf-8
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import logging
from Common.publicMethod import PubMethod

root_path = os.path.abspath(os.path.dirname(__file__)).split('Base')[0]
conf_path = os.path.join(root_path, "Conf/config.yaml")


def get_locator(page_elem_class, elem_name):
    """

    @param page_elem_class:传入页面元素对象
    @param elem_name:传入自定义的元素名称
    @return:
    """
    page_obj_elem = page_elem_class()
    elems_info = page_obj_elem.info
    for item in elems_info:
        if item.info["elem_name"] == elem_name:
            elem_locator = ("By.{}".format(item["data"]["method"]), item["data"]["value"])
            method = item["data"]["method"]
            value = item["data"]["value"]
            logging.info("元素名称为：{}，元素定位方式为：{}，元素对象值为：{}".format(elem_name, method, value))
            if method == "ID" and value is not None:
                return elem_locator
            elif method == "XPATH" and value is not None:
                return elem_locator
            elif method == "LINK_TEXT" and value is not None:
                return elem_locator
            elif method == "PARTIAL_LINK_TEXT" and value is not None:
                return elem_locator
            elif method == "NAME" and value is not None:
                return elem_locator
            elif method == "TAG_NAME" and value is not None:
                return elem_locator
            elif method == "CLASS_NAME" and value is not None:
                return elem_locator
            elif method == "CSS_SELECTOR" and value is not None:
                return elem_locator
            else:
                logging.error("元素名称：{}，此元素定位方式异常，定位元素值异常，请检查！！！".format(elem_name))


# Base层封装的是元素的操作方法
class Base:
    def __init__(self, driver):
        self.driver = driver
        self.timeout = 10
        self.poll_frequency = 0.5

    def get_url(self, url):
        """

        @param url: 测试url
        """
        try:
            self.driver.get(url)
            logging.info("{}获取成功".format(url))
        except Exception as e:
            logging.error("URL获取失败，错误信息为：{}".format(e))

    def get_login_url_from_config(self):
        """

        @return: 配置文件URL
        """
        config_info = PubMethod.read_yaml(conf_path)
        print("config_info地址：{}".format(config_info))
        return config_info["test_info"]["test_URL"]

    def login_by_config_url(self):
        """
            登录URL
        """
        self.driver.maximize_window()
        self.driver.get(self.get_login_url_from_config())

    def find_element(self, locator):
        logging.info("输出定位器信息：{}".format(locator))
        """
        :param locator: 传入定位器参数locator=(By.XX,"value")
        :return: 返回元素对象
        """
        if not isinstance(locator, tuple):
            logging.error('find_element：locator参数类型错误，必须传元祖类型：locator=(By.XX,"value")，错误参数为：{}'.format(locator))
        else:
            logging.info("find_element：正在定位元素信息：定位方式->%s,value值->%s" % (locator[0], locator[1]))
            try:
                time.sleep(1)
                elem = WebDriverWait(self.driver, self.timeout, self.poll_frequency).until(
                    lambda x: x.find_element(*locator))
                logging.info("元素对象为：{}".format(elem))
                return elem
            except Exception as e:
                logging.error("定位不到元素，错误信息为:{}".format(e))
                return False

    def find_elements(self, locator):
        """
        :param locator: 传入定位器参数locator=(By.XX,"value")
        :return: 返回元素对象列表
        """
        logging.info("输出定位器信息：{}".format(locator))
        if not isinstance(locator, tuple):
            logging.error('find_elements：locator参数类型错误，必须传元祖类型：locator=(By.XX,"value")')
        else:
            logging.info("find_elements：正在定位元素信息：定位方式->%s,value值->%s" % (locator[0], locator[1]))
            try:
                time.sleep(1)
                elems = WebDriverWait(self.driver, self.timeout, self.poll_frequency).until(
                    lambda x: x.find_elements(*locator))
                logging.info("元素对象为：{}".format(elems))
                return elems
            except Exception as e:
                logging.error("定位不到元素，错误信息为:{}".format(e))
                return False

    def switch_to_frame(self, locator):
        """
        :param locator: 传入定位器参数locator=(By.XX,"value")
        :return:
        """
        elem = self.find_element(locator)
        try:
            self.driver.switch_to.frame(elem)
            logging.info("frame切换成功")
        except Exception as e:
            logging.error("frame切换失败，错误信息为：{}".format(e))

    def switch_to_handle(self, index):
        """
            切换窗口句柄
        """
        # 获取当前所有窗口句柄
        try:
            handles = self.driver.window_handles
            logging.info("获取当前所有窗口句柄成功，句柄对象列表为：{}".format(handles))
        except Exception as e:
            logging.error("获取当前所有窗口句柄失败，错误信息为：{}".format(e))
        # 切换到新窗口句柄
        try:
            self.driver.switch_to.window(handles[index])
            logging.info("切换新窗口句柄成功，切换窗口的索引index为：{}".format(index))
        except Exception as e:
            logging.error("切换新窗口句柄失败，错误信息为：{}".format(e))

    def send_key(self, locator, value):
        """

        @param locator: 定位器
        @param value: value
        """
        elem = self.find_element(locator)
        try:
            elem.send_keys(value)
            logging.info("元素对象输入值成功，值为：{}".format(value))
        except Exception as e:
            logging.error("元素对象输入值失败，错误信息为：{}".format(e))

    def click_btn(self, locator):
        """

        @param locator: 定位器
        """
        elem = self.find_element(locator)
        try:
            elem.click()
            logging.info("元素对象点击成功")
        except Exception as e:
            logging.error("元素对象点击失败，错误信息为：{}".format(e))

    def get_text(self, locator):
        """

        @param locator:定位器
        @return:元素文本值
        """
        elem_text = None
        elem = self.find_element(locator)
        try:
            elem_text = elem.text
        except Exception as e:
            logging.error("元素text获取失败，错误信息为：{}".format(e))
        logging.info("元素text值：{}".format(elem_text))
        return elem_text

    def get_text_by_elements(self, locator, index):
        """

        @param locator: 定位器
        @return: 返回定位对象组的第一个元素的值
        """
        elem = self.find_elements(locator)
        try:
            elem_text = elem[index].text
            logging.info("获取元素组对象，索引位置{}的值成功，值为：{}".format(index, elem_text))
        except Exception as e:
            logging.error("获取元素组对象，索引位置{}的值失败，失败信息为：{}".format(e))
        return elem_text

    def get_placeholder(self, locator):
        """

        @param locator: 定位器
        @return: 返回placeholder属性值
        """
        elem = self.find_element(locator)
        try:
            elem_placeholder_text = elem.get_attribute("placeholder")
            logging.info("该元素对象获取placeholder成功，placeholder值为：{}".format(elem_placeholder_text))
        except Exception as e:
            logging.error("该元素对象获取placeholder失败，错误信息为：{}".format(e))
        return elem_placeholder_text

    def check_select_is_existence(self, locator):
        """

        @param locator: 定位器
        @return: 返回TRUE、FALSE
        """
        try:
            elem = self.find_element(locator)
            return True
        except Exception as e:
            return False

    def move_mouse_to_element(self, locator):
        """
        移动鼠标到某个元素上面
        @param locator:
        @return:
        """
        elem = self.find_element(locator)
        action = ActionChains(self.driver)
        action.move_to_element(elem).perform()

    def clear_input_value(self, locator):
        """
        清除输入框中的内容
        @param locator:
        @return:
        """
        elem = self.find_element(locator)
        elem.send_keys(Keys.CONTROL, "a")
        elem.send_keys(Keys.DELETE)

    def get_value(self, locator):
        """
        获取输入框的value
        @param locator:
        @return:
        """
        elem = self.find_element(locator)
        return elem.get_attribute("value")

    def double_click_elem(self, locator):
        """
        双击元素
        @param locator:
        @return:
        """
        elem = self.find_element(locator)
        ActionChains(self.driver).double_click(elem).perform()

    def elem_is_display(self, locator):
        """
        判断元素在页面是否显示，显示返回True,不显示返回false
        @param locator:
        @return:
        """
        elem = self.find_element(locator)
        return elem.is_displayed()

    def elem_is_selected(self, locator):
        """
        判断元素是否被选中，用于多选框，如果多选框被选中状态，返回True，否则返回False
        @param locator:
        @return:
        """
        elem = self.find_element(locator)
        return elem.is_selected()

    def elem_is_enable(self, locator):
        """
        判断页面元素是否可用
        @param locator:
        @return:
        """
        elem = self.find_element(locator)
        logging.info("按钮的点击状态，是否可点击：{}".format(elem.is_enabled()))
        return elem.is_enabled()

    def choose_select_by_value(self, locator, value):
        """
        根据内置属性value值值选择下拉输入框
        @param locator:
        @param value:
        @return:
        """
        elem = self.find_element(locator)
        Select(elem).select_by_value(value)

    def choose_select_by_index(self, locator, index):
        """
        根据索引选择下拉框
        @param locator:
        @param index:
        @return:
        """
        elem = self.find_element(locator)
        Select(elem).select_by_index(index)

    def choose_select_by_visible_value(self, locator, value):
        """
        根据下拉选项的文本值选择下拉框
        @param locator:
        @param value:
        @return:
        """
        elem = self.find_element(locator)
        Select(elem).select_by_visible_text(value)

    def choose_elem_by_visible_value(self, locator, value):
        """
        根据一组元素对象中某一个元素对象的文本值确定，哪一个元素对象
        @param locator:
        @param value:
        @return: 单个元素对象
        """
        elems = self.find_elements(locator)
        for item in elems:
            if self.elem_object_get_text(item) == value:
                return item

    def elem_object_click(self, elem):
        """
        元素点击，传入参数为元素对象
        @param elem:
        @return:
        """
        elem.click()

    def elem_object_get_text(self, elem):
        """
        元素对象获取text值，传入元素对象
        @param elem:
        @return:
        """
        elem_text = elem.text
        return elem_text


if __name__ == "__main__":
    print(root_path)
    print(conf_path)
    config_info = PubMethod.read_yaml(conf_path)
    print(config_info["test_info"])
