import os
import pickle
from time import sleep

from selenium import webdriver  # 操作浏览器的工具
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from tools import custom_logger
from Configuration import Web_Info

# Customized logging
logger = custom_logger.getLogger('root')


# 实现免登陆
# 大麦网官网
damai_url = Web_Info.URL
# 登录
login_url = Web_Info.Login_URL
# 抢票目标页
target_url = Web_Info.Target_URL


class Concert:

    def __init__(self):
        self.status = 0  # 状态, 表示当前操作执行到了哪个步骤
        self.login_method = 1  # {0:模拟登录, 1:cookie登录}自行选择登录的方式
        # self.driver = webdriver.Chrome(executable_path=r'drive/chromedriver.exe')  # 当前浏览器驱动对象
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def login(self):
        if self.login_method == 0:
            logger.info('Simulate log in')
            # 登录网址
            self.driver.get(login_url)
            print('###开始登录###')
        elif self.login_method == 1:
            # 创建文件夹, 文件是否存在
            if not os.path.exists('cookies.pkl'):
                logger.info('Cannot find the file cookies.pkl, you need to login')
                self.set_cookies()  # 没有文件的情况下, 登录一下
            else:
                logger.info('Found the file cookies.pkl')
                self.driver.get(target_url)  # 跳转到抢票页
                self.get_cookie()  # 并且登录

    def set_cookies(self):
        # navigate to the official web
        self.driver.get(damai_url)
        print('###请点击登录###')
        # 我没有点击登录,就会一直延时在首页, 不会进行跳转
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:
            sleep(1)

        print('###请扫码登录###')
        # 没有登录成功
        while self.driver.title != '大麦网-全球演出赛事官方购票平台-100%正品、先付先抢、在线选座！':
            sleep(1)
        print('###扫码成功###')
        # get_cookies: driver里面的方法
        pickle.dump(self.driver.get_cookies(), open('cookies.pkl', 'wb'))  # self.driver.get_cookies() 获取cookies
        print('Save cookies.pkl file successfully')
        self.driver.get(target_url)

    # 如果已经有了cookie
    def get_cookie(self):
        cookies = pickle.load(open('cookies.pkl', 'rb'))
        for cookie in cookies:
            cookie_dict = {
                'domain': '.damai.cn',  # 必须要有的, 否则就是假登录
                'name': cookie.get('name'),
                'value': cookie.get('value')
            }
            self.driver.add_cookie(cookie_dict)

        logger.info('Loaded cookies.pkl successfully')


if __name__ == '__main__':
    logger.info('Program Start!')
    con = Concert()
    con.login()
