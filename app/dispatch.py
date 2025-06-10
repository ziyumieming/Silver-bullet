# 每12h测试一次代理
TESTER_CYCLE =  43200*12
GETTER_CYCLE =  43200*12
TESTER_ENABLED = True
GETTER_ENABLED = True
API_ENABLED = True
API_HOST =  '0.0.0.0'
API_PORT = 8080

from multiprocessing import Process
from interface import app
from get import Getter
from detect import Tester
import time

class Scheduler():
    def schedule_tester(self, cycle=TESTER_CYCLE):
        testers = [
            Tester(redis_key='proxies_inner', test_url='http://www.baike.baidu.com'),
            Tester(redis_key='proxies_outer', test_url='https://www.wikipedia.org')
        ]
        while True:
            time.sleep(5)
            print('测试器开始运行')
            for tester in testers:
                tester.run()
            time.sleep(cycle)

    def schedule_getter(self, cycle=GETTER_CYCLE):
        getters = [
            Getter(redis_key='proxies_inner'),
            Getter(redis_key='proxies_outer')
        ]
        while True:
            print('开始抓取代理')
            for getter in getters:
                getter.run()
            time.sleep(cycle)

    def schedule_api(self):
        """
        开启API
        """
        app.run(API_HOST, API_PORT)

    def run(self):
        print('代理池开始运行')
        if TESTER_ENABLED:
            tester_process = Process(target=self.schedule_tester)
            tester_process.start()

        if GETTER_ENABLED:
            getter_process = Process(target=self.schedule_getter)
            getter_process.start()

        if API_ENABLED:
            api_process = Process(target=self.schedule_api)
            api_process.start()


if __name__ == '__main__':
    scheduler = Scheduler()
    scheduler.run()
    print('代理池运行中...')