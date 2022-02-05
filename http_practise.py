'''
@Version:v1.0
@author:张程
@filename:http_practise.py
@time:2021/11/25/10:01:52
Description:


'''
from _datetime import datetime
import urllib.request as url
from django.http import HttpResponse as hpr

system_start_time = datetime.utcnow()

response = url.urlopen('http://118.112.248.107:8585/test')
print(datetime.utcnow())
print('response',response.read().decode('utf-8'))
system_end_time = datetime.utcnow()
# 计算整个程序运行花费的时间
time_delta = system_end_time - system_start_time
# 转换为秒，显示整体的所需时间
cost_system_time_float = '%.3f' % (time_delta.total_seconds())
print('cost time :',cost_system_time_float)





