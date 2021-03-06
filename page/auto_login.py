# !/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import re
import shelve
import requests
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from page.base import Base
from page.ticket import Ticket


class Auto_Login(Base):
    _url = 'https://kyfw.12306.cn/otn/resources/login.html'
    _coordinate = [[-105, -20], [-35, -20], [40, -20], [110, -20], [-105, 50], [-35, 50], [40, 50], [110, 50]]
    with shelve.open('./info') as db:
        def __init__(self, driver, username=db['self._username'], password=db['self._password']):
            super().__init__(driver)
            self._username = username
            self._password = password

    def auto_login(self):
        # 用户名、密码输入
        self.wait_ele_clickable(3, (By.LINK_TEXT, '账号登录'))
        self.find(By.LINK_TEXT, '账号登录').click()
        self.find(By.ID, 'J-userName').send_keys(f'{self._username}')
        self.find(By.ID, 'J-password').send_keys(f'{self._password}')

        # def img_verify(self):
        while True:
            self.wait_to_invisible(10, (By.CSS_SELECTOR, '.lgcode-loading'))
            img_ele = self.find(By.ID, 'J-loginImg')
            base64_str = img_ele.get_attribute("src").split(",")[-1]
            img_data = base64.b64decode(base64_str)
            with open('verify.jpg', 'wb') as file:
                file.write(img_data)
            # def getVerifyResult(self):
            url = "http://littlebigluo.qicp.net:47720/"
            response = requests.request("POST", url, data={"type": "1"}, files={
                'pic_xxfile': open('verify.jpg', 'rb')})
            result = []
            # print(response.text)
            try:
                for i in re.findall("<B>(.*)</B>", response.text)[0].split(" "):
                    result.append(int(i) - 1)
            except Exception as e:
                print("图像处理服务器繁忙，即将尝试")
                continue
            # def moveAndClick(self):
            action_chains = self.action_chains()
            for i in result:
                action_chains.move_to_element(img_ele).move_by_offset(self._coordinate[i][0],
                                                                      self._coordinate[i][1]).click()
            action_chains.perform()
            try:
                self.find(By.ID, 'J-login').click()
                if self.finds(By.ID, 'nc_1_n1z'):
                    break
                elif self.finds(By.XPATH, '//*[contains(text(),"密码长度不能少于6位")]'):
                    print("密码长度不能少于6位！")
                    self.screen_shot('./密码太短.png')
                    raise Exception
                else:
                    print('验证码选择失败，即将重试')
                    self.find(By.CSS_SELECTOR, '.lgcode-refresh').click()
            except ElementClickInterceptedException:
                self.refresh()
                continue

        # def slide(self):
        while True:
            try:
                start = self.find(By.ID, 'nc_1_n1z')
                self.action_chains().click_and_hold(start).move_by_offset(340, 0).pause(0.1).release().perform()
                self.implicitly_wait(2)
                if self.finds(By.LINK_TEXT, '刷新'):
                    self.find(By.LINK_TEXT, '刷新').click()
                elif self.finds(By.LINK_TEXT, '确定'):
                    self.find(By.LINK_TEXT, '确定').click()
                    break
                elif self.finds(By.XPATH, '//*[text()="个人中心"]'):
                    break
                elif self.finds(By.XPATH, '//*[contains(text(),"密码输入错误")]'):
                    print('密码输入错误。')
                    raise Exception
                else:
                    raise Exception
                self.implicitly_wait(8)
            except Exception:
                self.screen_shot('./登录失败.png')
                print('登录失败')
                raise Exception
        return Ticket(self._driver)
