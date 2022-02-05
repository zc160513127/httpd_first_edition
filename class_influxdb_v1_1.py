#-*- code UTF-8
#writed by zc
#$Date 2020.11.27

import psutil
from influxdb import InfluxDBClient
import datetime
import time
import threading
from queue import Queue
'''
21.2.19 更改：
1.切换数据库时，没有返回值ret
2.加入线程，与主程序隔离，做到数据库的连接和更换，不影响主程序；
    存储数据放入消息队列中，进行操作；
3.加入对消息队列数据的保护；
4.存入数据库中的数据格式：['measurement','----','data_kind','-------',
                        key1,value1,key2,value2,key3,value3,.....]
                        
21.2.25 更改：
1.存入数据库中的数据格式加入数据自身时间戳，方便对比矫正操作！！！！！！！
['measurement','----','data_kind','-------','data_time','-------',
                        key1,value1,key2,value2,key3,value3,.....]
'''

class mydatabase():


    def __init__(self):
        '''
        初始化
        '''
        self._init_paras_actions()


    def _init_paras_actions(self):
        '''
        初始化参数和线程
        :return:
        '''
        self.client_all = None
        self.current_database = None

        self._create_queue()
        self._init_threading_paras()


    def _create_queue(self):
        '''
        创建默认消息队列，
        :return:
        '''
        self._send_queue=Queue(20)
        self._send_queue.queue.clear()
        time.sleep(0.001)
        self._frame_data=None#一帧消息队列里的数据

# *************线程************************

    def _init_threading_paras(self):
        '''
        启用线程，负责将数据发送给数据库，
        并且可有外部控制线程的工作与否，默认工作
        :return:
        '''
        self._working_threading1_flag=True#默认开始就工作
        t1=threading.Thread(target=self._working_threading1)
        t1.setDaemon(True)
        t1.start()

    def start_threading(self):
        self._working_threading1_flag = True

    def stop_threading(self):
        self._working_threading1_flag = False

    def _working_threading1(self):
        '''
        工作线程，将消息队列数据发送给数据库
        :return:
        '''
        while True:
            if not self._working_threading1_flag or not self.client_all or not self.current_database:
                time.sleep(0.5)
                continue
            try:
                if not self._send_queue.empty():
                    self._write_single_data_to_db()
            except:
                pass
            time.sleep(0.002)

    def _processed_frame_queue_data(self):
        '''
        将消息队列中的列表数据，解析成数据库中的数据格式
        :return:
        '''

        if not self.client_all and not self.current_database:
            return None

        #处理消息队列中的数据
        self._frame_data = self._send_queue.get_nowait()

        counter1 = (len(self._frame_data) - 4) % 2
        if self._frame_data[0] != 'measurement' and self._frame_data[2] != 'data_kind' and counter1 != 0:
            return None

        data_frame= {}

        data_frame['measurement'] = self._frame_data[1]#---1

        temp1={'saved_data_kind': self._frame_data[3]}
        data_frame['tags']=temp1                        #---2


        counter2=int((len(self._frame_data) - 4)/2)
        temp2={}
        for i in range(counter2):
            pass
            temp2[self._frame_data[2*i+4]] = self._frame_data[2*i+4+1]#---3

        temp2['cpu-usage']=psutil.cpu_percent(None)#---4
        temp2['memory-usage']=psutil.virtual_memory().percent#---5
        data_frame['fields'] = temp2  #注意存储进数据库的数据不能够带/和%

        data_frame_list=[]
        data_frame_list.append(data_frame)

        # print('db_data_frame ----'+str(data_frame_list))

        return data_frame_list


#**************功能区************************
    def connect_db_server(self):
        '''
        :return: 返回是否成功建立数据库客户端
        '''
        try:
            self.client_all = InfluxDBClient("localhost", "8086", "", "", "", timeout=1)
            # self.client_all = InfluxDBClient("118.112.248.107", "8086", username='admin', password='zc160513127',  timeout=1)
            return self.client_all
        except:
            return None

    def get_list_databases(self):
        '''
        :return: 返回数据库服务器中，所有数据库的列表
        '''
        if self.client_all:
            try:
                return self.client_all.get_list_database()
            except:
                return None
        else:
            return None

    def get_list_measurements(self):
        if self.client_all:
            return self.client_all.get_list_measurements()
        else:
            return None

    def open_db(self,database_name):
        '''
        :param database_name: 输入数据库名称
        :return: 打开的客户端名称
        '''
        if not self.client_all:
            return None
        database_list = self.client_all.get_list_database()
        flag_judge_database_if_exesit = False
        for i in database_list:
            if database_name in i.values():
                flag_judge_database_if_exesit = True
        if not flag_judge_database_if_exesit:
            self.client_all.create_database(database_name)
            self.client_all.switch_database(database_name)
        else:
            self.client_all.switch_database(database_name)

        self.current_database=database_name
        return self.current_database

    def disconnect_db_server(self):
        if self.client_all:
            self.client_all.close()
            self.client_all=None
            self.current_database=None

    def get_current_database(self):
        '''
        :return: 返回当前类中使用的数据库
        '''
        return self.current_database

    def get_data_list_in_period(self,meansurement='',time_scale='5s',flag=True):
        '''
        :param meansurement: 从哪个表中提取数据
        :param time_scale: 提取数据的时间跨度
        :param flag: 采用绝对时间模式，还是相对时间模式；False，当前时间往前推；True，数据库中的时间往前推
        :return: 返回数据列表
        '''

        if self.client_all and self.current_database:
            if flag == True:
                result_sets = self.client_all.query("select * from " + meansurement + " LIMIT 50 ")
                if not result_sets:
                    return None

            else:
                result_sets = self.client_all.query(
                    "select * from " +
                    meansurement + " where time >  now() - " + time_scale)
                if not result_sets:
                    return None
            db_items = list(result_sets.get_points())  # from iterator to list
            return db_items

    def get_data_list_in_number(self,number):
        pass

    def _write_single_data_to_db_server(self):
        '''
        ---作废！！
        :return:
        '''
        # 存储进数据库的相关数据的数据结构
        # global save_data_stycle, commdata_influxdb_saved, save_data_ID_and_stycle
        # data_list = [
        #     {
        #         'measurement': save_data_ID_and_stycle,
        #         'tags': {
        #             'saved_data_stycle': save_data_stycle
        #         },
        #
        #         'fields': {
        #             'cpu-usage/%': psutil.cpu_percent(None),
        #             'memory-usage/%': psutil.virtual_memory().percent,
        #             'data': commdata_influxdb_saved
        #         }
        #     }
        # ]

    def _write_single_data_to_db(self):
        '''
        类内部存储函数
        :return:
        '''
        if not self.client_all and not self.current_database:
            return None
        ret=self._processed_frame_queue_data()
        self.client_all.write_points(ret)

    def add_data_2_send(self,data):
        '''
        将数据加入到消息队列中进行存储操作，
        异常时对消息队列进行清空
        ---data:列表格式---
        :return:
        '''
        if not self.client_all and not self.current_database:
            return None
        else:
            try:
                self._send_queue.put_nowait(data)
            except:
                # 这里需要注意，当接收数据过多没有处理的时候，需要清楚消息队列
                try:
                    if self._send_queue.full():
                        counter = self._send_queue.qsize() - 1
                        for i in range(counter):
                            if not self._send_queue.empty():
                                self._send_queue.get_nowait()
                                time.sleep(0.001)  # 延时函数是为了给清楚消息队列的时间，否则清楚不干净
                except:
                    if not self._send_queue.empty():
                        counter = self._send_queue.qsize() - 1
                        for i in range(counter):
                            if not self._send_queue.empty():
                                self._send_queue.get_nowait()
                                time.sleep(0.001)  # 延时函数是为了给清楚消息队列的时间，否则清楚不干净


    def delete_measurements(self,name):
        '''
        :param name: 从当前数据库中删除表单名
        :return:
        '''
        if self.client_all and self.current_database:
            self.client_all.drop_measurement(name)
            return True
        else:
            return None




