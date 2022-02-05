'''
2022.01.05  工作逻辑：
    1.接收数据库中的数据,并且将最新的数据写入ini文件中；
    2.解析传感器数据；
    3.封装传感器数据，序列化成json格式的；


'''
import sys,os
import configparser
import threading
import time
import json
sys.path.append('/usr/local/zc/httpd/first_edition/')
from withdraw_influxdb_data import remote_infuxdb_data_methods as rm_db_obj
from withdraw_sensor_data import withdraw_datas_methods as ship_data_obj
from json_zhifei_http import sensor_json_methods

class crt_full_frm_obj():
    '''
    接收数据库的数据，并且生成数据文件，供其他目的使用；
    传感器、功率数据中心


    '''

    
    def __init__(self):
        self._set_paras()

        self._instance_obj()

        self._init_threadings()




    def _set_paras(self):
        '''
        设置各种参数
        '''

        '''
        远程服务器中的数据
        '''
        self._ini_file_path = 'httd_settings.ini'
        self.ini_obj = configparser.ConfigParser()
        self.ini_obj.read(self._ini_file_path)
        #print(self.ini_obj.sections())
        self._db_ip = self.ini_obj.get('dbc_setting', 'db_ip')
        self._db_name = self.ini_obj.get('dbc_setting', 'db_name')
        self._threading_fresh_period = self.ini_obj.get('global_setting', 'refreshPeriod')

    def _init_threadings(self):
        '''
        初始化线程
        :return:None
        '''
        t1 = threading.Thread(target=self._working_threading)
        t1.setDaemon(False)
        t1.start()


    def _instance_obj(self):
        '''
        实例化各种类
        :return:

        '''
        self.rm_db_ct = rm_db_obj(self._db_ip,self._db_name)
        self.ship_data_ct = ship_data_obj()
        self.sensor_json_obj = sensor_json_methods()


    def _update_ct_data(self):
        '''
        更新ini文件中的数据，关于数据库的，这里是所有数据的源头
        :return: None
        '''
        self.new_ship_data_frm = {}

        self.new_ship_data_frm = self.ship_data_ct.withdraw_300TEU_sensor_data(self.rm_db_ct.get_single_frame())

        for key,value in self.new_ship_data_frm.items():
            self.ini_obj.set('sensor_data', str(key), str(value))

        self.ini_obj.write(open(self._ini_file_path, 'w'))
        print('self.new_ship_data_frm---',self.new_ship_data_frm)


    def _update_json_file(self):
        '''
        更新Json文件中的数据
        :return:
        '''
        self.sensor_json_obj.refresh_json_file(self.new_ship_data_frm)



    def _working_threading(self):
        '''
        线程，负责更新数据
        :return:
        '''

        while True:

            time.sleep(float(self._threading_fresh_period))

            '''
            20220106:
            判断数据中心是否有数据传回，
            如果没有，则相应的数据需要清空。
            '''
            try:

                self._rm_db_data_frm = self.rm_db_ct.get_single_frame()

                # print('crt_full_frm.py 数据中心返回的数据',self._rm_db_data_frm)
                if self._rm_db_data_frm :
                    self._update_ct_data() #更新数据库数据
                    self._update_json_file() #更新json文件数据
                else:

                    self.sensor_json_obj.clear_json_data()

            except Exception as err:
                pass
                print(err)


            with open("data_center.json", "r", encoding='utf-8') as f:
                json_file = json.load(f)
                f.seek(0)
                print(str(json_file))




            # print('success',self.new_ship_data_frm)








if __name__ == '__main__':
    obj = crt_full_frm_obj()
    while True:
        time.sleep(1)
