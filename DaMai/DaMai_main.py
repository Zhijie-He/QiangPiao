import os
import pickle
from time import sleep

from selenium import webdriver  # 操作浏览器的工具
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from tools import custom_logger
from Configuration import Web_Info
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

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
        # self.driver = webdriver.Chrome(executable_path=r'drive/chromedriver105.exe')  # 当前浏览器驱动对象
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

    def enter_concert(self):
        logger.info('Enter DaMai.')
        # 调用登录
        self.login()  # 先登录再说
        self.driver.refresh()  # 刷新页面
        self.status = 2  # 登录成功标识
        logger.info('Login Successfully.')

        # 处理弹窗
        if self.isElementExist('/html/body/div[2]/div[2]/div/div/div[3]/div[2]'):
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div/div[3]/div[2]').click()

    def choose_ticket(self):
        if self.status == 2:
            logger.info('Start to choose date and ticket price')

            while self.driver.title.find("确认订单") == -1:
                try:
                    buybutton = self.driver.find_element(By.CLASS_NAME, 'buybtn').text
                    if buybutton == '提交缺货登记':
                        self.status = 2  # 没有进行更改操作
                        self.driver.get(target_url)  # 刷新页面 继续执行操作
                    elif buybutton == '立即预定':
                        # 点击立即预定
                        self.driver.find_element(By.CLASS_NAME, 'buybtn').click()
                        self.status = 3
                    elif buybutton == '立即购买':
                        self.driver.find_element(By.CLASS_NAME, 'buybtn').click()
                        self.status = 4
                    elif buybutton == '选座购买':
                        self.driver.find_element(By.CLASS_NAME, 'buybtn').click()
                        self.status = 5
                except:
                    logger.info('###没有跳转到订单结算界面###.')

                title = self.driver.title

                if title == '选座购买':
                    # 选座购买的逻辑
                    logger.info('选座购买.')
                    self.choice_seats()
                elif title == '确认订单':
                    # 实现下单的逻辑
                    while True:
                        # 如果标题为确认订单
                        logger.info('Loading....')
                        # 如果当前购票人信息存在 就点击
                        if self.isElementExist('//*[@id="container"]/div/div[9]/button'):
                            # 下单操作
                            self.check_order()
                            break

    def choice_seats(self):
        while self.driver.title == '选座购买':

            while self.isElementExist('//*[@id="app"]/div[2]/div[2]/div[1]/div[2]/img'):
                logger.info('Select the seat quickly')

            while self.isElementExist('//*[@id="app"]/div[2]/div[2]/div[2]/div'):
                self.driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/button').click()

    def check_order(self):
        if self.status in [3, 4, 5]:
            logger.info('Check the order')
            try:
                # 默认选第一个购票人信息
                self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[2]/div[2]/div[1]/div/label').click()
            except Exception as e:
                logger.info('Cannot find the personal information')
                logger.warning(e)
            # 最后一步提交订单
            #self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[1]/div[4]/div[1]/div[2]/span/input'). \
                #send_keys("hezhijie")
            #self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[1]/div[4]/div[2]/div[2]/span[2]/input'). \
                #send_keys("18205229522")

            sleep(0.5)  # 太快了不好, 影响加载 导致按钮点击无效

            self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[9]/button').click()

    def isElementExist(self, element):
        flag = True
        browser = self.driver
        try:
            browser.find_element(By.XPATH, element)
            return flag
        except:
            flag = False
            return flag

    def finish(self):
        self.driver.quit()


if __name__ == '__main__':
    logger.info('Program Start!')
    con = Concert()
    con.enter_concert()
    con.choose_ticket()
