'''
提取数据库中的数据，供综合显示数据显示

'''

import psutil
from influxdb import InfluxDBClient
import datetime

class remote_infuxdb_data_methods():
    def __init__(self,db_ip,meas_name):
        self._ip = db_ip
        self._name = meas_name
        self._find_meas_time_counter = 700 #先设置成这个数字，是为了初始化的时候能够计算一次；
        self.set_db_paras()
        self.frm_db_data_str = None





    def set_db_paras(self):
        self.client_all = InfluxDBClient(self._ip, "8086", username='smeri_server_admin', password='zc160513127',timeout=2)
        self.client_all.switch_database(self._name)
        self.find_latest_measurements()

    def find_latest_measurements(self):
        '''
        计算出最新的时间表
        '''
        # 每隔60*period时间间隔，计算是否有最新的数据库数据产生
        if self._find_meas_time_counter < 60:
            return

        self._find_meas_time_counter =0

        list_measurements=self.client_all.get_list_measurements()
        self.timestamp = datetime.datetime.now().strftime('%Y%m%d')

        '''
        20220110:
        根据最新的秒数，比大小，找到最新的时间表（measurement）
        '''
        findflag= False
        compare_int = 0
        for i in range(len(list_measurements)):
            if self.timestamp in list_measurements[i]['name']:
                # 找到时间比较值的初始位置索引值
                date_index = str(list_measurements[i]['name']).find(self.timestamp)
                # 找到符合条件的“表”的时间部分的字符串
                transfer_int_str  = int(str(list_measurements[i]['name'])[date_index:date_index+14])
                # 比较时间字符串转换的数字，谁的最大，代表这谁的表示的“表”是最新的数据库数据
                if transfer_int_str > compare_int:
                    compare_int = transfer_int_str
                    self.selected_measurements = list_measurements[i]['name']
                    findflag = True
                # print(list_measurements[i]['name'])

        if findflag == False:
            self.timestamp = str(int(datetime.datetime.now().strftime('%Y%m%d'))-1)

            compare_int = 0
            for i in range(len(list_measurements)):
                if self.timestamp in list_measurements[i]['name']:
                    # 找到时间比较值的初始位置索引值
                    date_index = str(list_measurements[i]['name']).find(self.timestamp)
                    # 找到符合条件的“表”的时间部分的字符串
                    transfer_int_str = int(str(list_measurements[i]['name'])[date_index:date_index + 14])
                    # 比较时间字符串转换的数字，谁的最大，代表这谁的表示的“表”是最新的数据库数据
                    if transfer_int_str > compare_int:
                        compare_int = transfer_int_str
                        self.selected_measurements = list_measurements[i]['name']
                        findflag = True
        # print(self.timestamp)

        self._process_db_data_2_frm()

    def _withdraw_frm_data_from_db(self,meansurement:str):
        result_sets = self.client_all.query(
            "select * from " +
            meansurement + " where time >  now() - 5s" )

        if not result_sets:
            return None

        db_items = list(result_sets.get_points())  # from iterator to list
        # print(db_items[-1])
        return db_items[-1]

    def _process_db_data_2_frm(self):
        frm_db_data = self._withdraw_frm_data_from_db(self.selected_measurements)
        if frm_db_data == None:
            self.frm_db_data_str = None
            return None

        frm_db_data_str = ''
        for i in range(7):
            frm_db_data_str += '*'+str(i)
            frm_db_data_str += frm_db_data[str(i)]

        self.frm_db_data_str = frm_db_data_str
        # print(frm_db_data_str)



    def get_single_frame(self):
        '''
        供外部调用
        '''
        try:
            self._find_meas_time_counter += 1
            self.find_latest_measurements()
            self._process_db_data_2_frm()
        except:
            pass   

        return self.frm_db_data_str






if __name__ == '__main__':
    remote_infuxdb_data_methods()
