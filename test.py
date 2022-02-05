'''
@Version:v1.0
@author:张程
@filename:test.py
@time:2021/12/28/11:15:03
Description:


'''

import os
import sys
import threading
import urllib.request as ask
import time,datetime

class test_httpd_process_ability():
    '''
    test the ability of http server
    '''
    def __init__(self):
        self.time_period = 0.1
        self._init_threading()


    def _init_threading(self):
        '''
        start threading
        '''
        self.__t1 = threading.Thread(target=self.working_threading)
        self.__t1.setDaemon(False)
        self.__t1.start()

    def working_threading(self):
        '''
        threading:
        test the action of http server:
        '''

        while True:
            time.sleep(self.time_period)
            startTime = datetime.datetime.utcnow()
            try:
                self._resp_obj = ask.urlopen('http://118.112.248.107:8585/zhifei')
                self._resp_str = self._resp_obj.read().decode('utf-8')
                print(self._resp_obj.read().decode('utf-8'))
            except Exception as err:
                print('-----',err)

            stopTime = datetime.datetime.utcnow()
            timeCost = (stopTime - startTime).microseconds/1000000.0
            print('----------',timeCost)

# _resp_obj = ask.urlopen('http://118.112.248.107:8585/zhifei')
# print(_resp_obj.read().decode('utf-8'))

if __name__ == '__main__':
    test_obj = test_httpd_process_ability()
