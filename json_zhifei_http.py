'''
@Version:v1.0
@author:张程
@filename:json_zhifei_http.py
@time:2022/01/06/08:53:49
Description:
    1.将上层传下来的传感器数据，生成json格式的数据；
    2.部署到服务器中；


'''
import json
import sys
import configparser
from _datetime import datetime


class zhifei_httpd_formats():
    '''
    智飞数据的数据格式
    '''
    def __init__(self):

        self.zhifei_sensor_data={'jsonTag' : 'zhifei_ship_info',
                                 'shipName' : 'zhifei',
                                 'shipType' : 'container',
                                 'MMSI': '413286730',
                                 'shipStatus': 'ONLINE',
                                 'messageStatus': 'Success',
                                 "timestamp":"None",
                                 "sensor_data":
                            {
                             'rot': '000.66',
                             'hdt': '357.8',
                             'cog': '0.00',
                             'sog': '0.00',
                             'lon': '12052.36080394E',
                             'lat': '3622.40313364N',
                             'pitch': '+001.54',
                             'roll': '+001.05',
                             'windDirection': '346.6',
                             'windSpeed': '003.3',

                            }}

        self.zhifei_power_data = {}

        self.zhifei_AIS_target_info = {}

        self.zhifei_route_info = {}

class sensor_json_methods():
    '''
    对传感器数据进行Json化，并且生成合适的数据
       提取出需要的传感器数据，字典形式给出；
        {'ths1' :None,
         'hdt1' :None,
         'rot1' :None,
         'ths2' :None,
         'hdt2' :None,
         'rot2' :None,
         'cog1' :None,
         'sog1' :None,
         'cog2' :None,
         'sog2' :None,
         'lon1' :None,
         'lat1' :None,
         'lon2' :None,
         'lat2' :None,
         'pitch':None,
         'roll' :None,
         'wd1' :None,
         'ws1' :None,
         'wd2' :None,
         'ws2' :None
        }
    '''
    def __init__(self):
        self.httpd_sensor_fmt_obj = zhifei_httpd_formats().zhifei_sensor_data

        self.sensor_json_data = None

    def refresh_json_file(self,sensor_dict:dict):

        self.sensor_json_data = self.process_sensor_dict(sensor_dict)
        with open("/usr/local/zc/httpd/first_edition/data_center.json", "w+", encoding='utf-8') as f:
            f.write(self.sensor_json_data)  ##indent 缩进4个


    def process_sensor_dict(self,sensor_dict:dict):
        '''
        处理字典数据，提取生成关键数据
        :param sensor_dict: 包含传感器数据的字典结构数据
        :return: 处理后的JSON格式数据
        "sensor_data":
                            {
                             'rot': '000.66',
                             'hdt': '357.8',
                             'cog': '0.00',
                             'sog': '0.00',
                             'lon': '12052.36080394E',
                             'lat': '3622.40313364N',
                             'pitch': '+001.54',
                             'roll': '+001.05',
                             'windDirection': '346.6',
                             'windSpeed': '003.3',

                            }
        '''
        self.httpd_sensor_fmt_obj["sensor_data"]["rot"] = round((float(sensor_dict['rot1']) +float(sensor_dict['rot2']))/2.0,3)
        self.httpd_sensor_fmt_obj["sensor_data"]["hdt"] = round((float(sensor_dict['ths1']) + float(
            sensor_dict['hdt2'])) / 2.0,3)
        self.httpd_sensor_fmt_obj["sensor_data"]["cog"] = round((float(sensor_dict['cog1']) + float(
            sensor_dict['cog2'])) / 2.0,3)
        self.httpd_sensor_fmt_obj["sensor_data"]["sog"] = round((float(sensor_dict['sog1']) + float(
            sensor_dict['sog2'])) / 2.0,3)
        self.httpd_sensor_fmt_obj["sensor_data"]["windDirection"] = round((float(sensor_dict['wd1']) + float(
            sensor_dict['wd2'])) / 2.0,3)
        self.httpd_sensor_fmt_obj["sensor_data"]["windSpeed"] = round((float(sensor_dict['ws1']) + float(
            sensor_dict['ws2'])) / 2.0,3)

        self.httpd_sensor_fmt_obj["sensor_data"]["lon"] = str((float(sensor_dict['lon1'][:-1]) + float(
            sensor_dict['lon2'][:-1])) / 2.0) +sensor_dict['lon1'][-1]

        self.httpd_sensor_fmt_obj["sensor_data"]["lat"] = str((float(sensor_dict['lat1'][:-1]) + float(
            sensor_dict['lat2'][:-1])) / 2.0) + sensor_dict['lat1'][-1]

        self.httpd_sensor_fmt_obj["sensor_data"]["pitch"] = sensor_dict['pitch']
        self.httpd_sensor_fmt_obj["sensor_data"]["roll"] = sensor_dict['roll']

        self.httpd_sensor_fmt_obj["timestamp"] =  datetime.now().strftime('%Y%m%d%H%M%S%f')

        self.httpd_sensor_fmt_obj["shipStatus"] = 'ONLINE'
        self.httpd_sensor_fmt_obj["messageStatus"] = 'success'

        json_data = json.dumps(self.httpd_sensor_fmt_obj, indent=8)


        return json_data

    def clear_json_data(self):
        '''
        由于上端数据没有，将json格式中的所有数据清空，相应标志位清空；
        :return: None
        '''

        self.httpd_sensor_fmt_obj["shipStatus"] = 'OFFLINE'
        self.httpd_sensor_fmt_obj["messageStatus"] = 'FAIL,check server connection!!'
        self.httpd_sensor_fmt_obj["sensor_data"]["rot"] = None
        self.httpd_sensor_fmt_obj["sensor_data"]["hdt"] = None
        self.httpd_sensor_fmt_obj["sensor_data"]["cog"] = None
        self.httpd_sensor_fmt_obj["sensor_data"]["sog"] = None
        self.httpd_sensor_fmt_obj["sensor_data"]["windDirection"] = None
        self.httpd_sensor_fmt_obj["sensor_data"]["windSpeed"] = None

        self.httpd_sensor_fmt_obj["sensor_data"]["lon"] = None

        self.httpd_sensor_fmt_obj["sensor_data"]["lat"] = None

        self.httpd_sensor_fmt_obj["sensor_data"]["pitch"] = None
        self.httpd_sensor_fmt_obj["sensor_data"]["roll"] = None

        self.httpd_sensor_fmt_obj["timestamp"] = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        with open("/usr/local/zc/httpd/first_edition/data_center.json", "w+", encoding='utf-8') as f:
            f.write(json.dumps(self.httpd_sensor_fmt_obj, indent=8))  ##indent 缩进4个


if __name__ == '__main__':
    sensor_json_methods()



