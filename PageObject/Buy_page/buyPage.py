# coding:utf-8
from Base.base import Base
from PageObject.elemParams import BuyPageElem


# 封装速涡手游加速器购买页面操作对象及各个元素及操作方法
class Buy_page(Base):
    def __init__(self, driver):
        super().__init__(driver)
        self.elem_locator = BuyPageElem()

    def find_button_buy(self):
        """
        查找购买按钮文本
        @return:
        """
        elem = self.elem_locator.get_locator("ProductBuyBtn")
        return self.get_text_by_elements(elem)
