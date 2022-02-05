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
sys.path.append('/usr/local/zc/httpd/first_edition/')
from class_influxdb_v1_1 import *

class test_httpd_process_ability():
    '''
    test the ability of http server
    '''
    def __init__(self):
        self.time_period = 0.01
        self._db_obj = mydatabase()
        self._init_db_paras()

        self._init_threading()



    def _init_threading(self):
        '''
        start threading
        '''
        self.__t1 = threading.Thread(target=self.working_threading)
        self.__t1.setDaemon(False)
        self.__t1.start()

    def _init_db_paras(self):
        '''
        connect db
        '''
        self.__db_measurement_name_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.__db_compare_timestamp = datetime.datetime.utcnow()
        self._db_obj.connect_db_server()
        self._db_obj.open_db('httpd_respond_timeCost')
        self._connect_db_server_flag = True
        self._opend_db_flag = True


    def __run_db_update_policy(self):
        '''
        运行数据库维护策略
            --指定表名更新时间策略，或者其他
        '''

        now_utc = datetime.datetime.utcnow()
        sub_time = now_utc - self.__db_compare_timestamp

        if sub_time.days > 0:
            self.__db_measurement_name_timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            self.__db_compare_timestamp = datetime.datetime.utcnow()


    def _send_data_2_db(self, raw_data, data_kind):
        '''
        将数据,先打包封装一下，再发送到客户端

        ['measurement','----','data_kind','-------',
                        key1,value1,key2,value2,key3,value3,.....]

        '''
        if not self._connect_db_server_flag and not self._opend_db_flag:
            return None

        timestamp1 = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        data = raw_data.copy()

        data.insert(0, 'measurement')
        data.insert(1,  'httpd_timeCost' + self.__db_measurement_name_timestamp  )
        data.insert(2, 'data_kind')
        data.insert(3, data_kind)
        data.insert(4, 'data_time')
        data.insert(5, timestamp1)

        self._db_obj.add_data_2_send(data)
        # print('send_2_db_data  : '+str(data))



    def working_threading(self):
        '''
        threading:
        test the action of http server:
        '''

        while True:
            time.sleep(self.time_period)
            self.__run_db_update_policy()
            startTime = datetime.datetime.utcnow()
            try:
                self._resp_obj = ask.urlopen('http://118.112.248.107:8585/zhifei')
                self._resp_str = self._resp_obj.read().decode('utf-8')
                # print(self._resp_obj.read().decode('utf-8'))
            except Exception as err:
                print('-----',err)

            stopTime = datetime.datetime.utcnow()
            timeCost = (stopTime - startTime).microseconds/1000000.0
            temp_list = ['timecost',timeCost]
            self._send_data_2_db(temp_list,'realtime')
            # print('----------',timeCost)

# _resp_obj = ask.urlopen('http://118.112.248.107:8585/zhifei')
# print(_resp_obj.read().decode('utf-8'))

if __name__ == '__main__':
    test_obj = test_httpd_process_ability()





