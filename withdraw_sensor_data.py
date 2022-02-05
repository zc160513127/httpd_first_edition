

'''
*0$THS&27.6$HDT&27.6
*1$THS&27.6$HDT&27.6
*2$VTG&13.8T&4.7N$GGA&0004.596666N&00004.596666E
*3$VTG&13.8T&4.7N$GGA&0004.596666N&00004.596666E
*4$DID&12.6&12.6&13.8
*5$MWV&27.5&2.5
*6$MWV&27.5&2.5
'''

'''
2021 11 13：
    --变成类，可以识别出数据缺失并且报警；
'''
class withdraw_datas_methods():
    def __init__(self):
        self.sensor_state={
            'gyro1_alarm_flag':False,
            'gyro2_alarm_flag': False,
            'dgps1_alarm_flag': False,
            'dgps2_alarm_flag': False,
            'mru_alarm_flag': False,
            'wind1_alarm_flag': False,
            'wind2_alarm_flag': False
        }                           # 7个传感器的报警标志位

        self.sensor_lost_time_counter = [0,0,0,0,0,0,0]    # 7个传感器的丢失时间计数器
        self.alarm_thresholdvalue_counter = 10    #  传感器的信号丢失报警阈值




    def withdraw_300TEU_sensor_data(self,data_str :str):
        '''
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
        # 存放最终的数据
        result_data = {'ths1' :None,
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
         'wd1': None,
         'ws1': None,
         'wd2': None,
         'ws2': None
        }

        star_indexs = []
        sensor_list = []


        for i in range(len(data_str)):
            if data_str[i] == '*':
                star_indexs.append(i)

        for i in range(len(star_indexs) - 1):
            sensor_list.append(data_str[star_indexs[i]:star_indexs[i + 1]])
        sensor_list.append(data_str[star_indexs[-1]:])
        # print('每个传感器数据列表sensor_list：',sensor_list)
        '''
        将来可以查看，如果sensor_list的列表里每个都是字符串长度为4时，代表没有数据
        '''

        '''
           找到每组的ID号，区分开来
        '''
        class_ID_list = []
        for i in range(len(sensor_list)):
            pass
            index1 = sensor_list[i].index('$')
            class_ID_list.append(sensor_list[i][1:index1])
        print('每个传感器的ID号',class_ID_list)

        '''
        2021.11.20 更改：
        添加处理传感器状态的程序
        参数：sensor_list： ['*0$THS&27.6$HDT&27.6', '*1$THS&27.6$HDT&27.6', '*2$VTG。。。]
            class_ID_list:['0', '1', '2', '3', '4', '5', '6']
        '''
        self.process_sensor_state(sensor_list,class_ID_list)

        details_str_list = []
        dollar_list = []
        for i in range(len(star_indexs)):
            temp = []
            for j in range(len(sensor_list[i])):
                if sensor_list[i][j] == '$':
                    temp.append(j)
            dollar_list.append(temp)
        print('每个传感器数据里$的位置dollar_list：',dollar_list)

        for i in range(len(star_indexs)):
            temp1 = []
            for j in range(len(dollar_list[i]) - 1):
                temp1.append(sensor_list[i][dollar_list[i][j]:dollar_list[i][j + 1]])
            temp1.append(sensor_list[i][dollar_list[i][-1]:])

            details_str_list.append(temp1)
        # print('每个数据列表里数据的切分details_str_list',details_str_list)

        #将不同数据列表里的数据放在正确的字典中
        try:
            direct_list = result_data
            try:
                if '0' in class_ID_list:
                    index1_class_id = class_ID_list.index('0')
                    for i in range(len(details_str_list[index1_class_id])):
                        if 'THS' in details_str_list[index1_class_id][i]:
                            index1 = details_str_list[index1_class_id][i].index('&')
                            direct_list['ths1'] = details_str_list[index1_class_id][i][index1 + 1:]

                        if 'ROT' in details_str_list[index1_class_id][i]:
                            index1 = details_str_list[index1_class_id][i].index('&')
                            direct_list['rot1'] = details_str_list[index1_class_id][i][index1 + 1:]

            except:
                pass

            try:
                if '1' in class_ID_list:
                    index1_class_id = class_ID_list.index('1')
                    for i in range(len(details_str_list[index1_class_id])):
                        if 'ROT' in details_str_list[index1_class_id][i]:
                            index1 = details_str_list[index1_class_id][i].index('&')
                            direct_list['rot2'] = details_str_list[index1_class_id][i][index1 + 1:]

                        if 'HDT' in details_str_list[index1_class_id][i]:
                            index1 = details_str_list[index1_class_id][i].index('&')
                            direct_list['hdt2'] = details_str_list[index1_class_id][i][index1 + 1:]
            except:
                pass

            try:
                if '2' in class_ID_list:
                    index1_class_id = class_ID_list.index('2')
                    for i in range(len(details_str_list[index1_class_id])):
                        if 'GGA' in details_str_list[index1_class_id][i]:
                            index1 = details_str_list[index1_class_id][i].index('&')
                            index2 = details_str_list[index1_class_id][i].rindex('&')
                            direct_list['lat1'] = details_str_list[index1_class_id][i][index1 + 1:index2]
                            direct_list['lon1'] = details_str_list[index1_class_id][i][index2 + 1:]

                        if 'VTG' in details_str_list[index1_class_id][i]:
                            index1 = details_str_list[index1_class_id][i].index('&')
                            index2 = details_str_list[index1_class_id][i].rindex('&')
                            direct_list['cog1'] = details_str_list[index1_class_id][i][index1 + 1:index2 - 1]
                            direct_list['sog1'] = details_str_list[index1_class_id][i][index2 + 1:-1]
            except:
                pass

            try:
                if '3' in class_ID_list:
                    index1_class_id = class_ID_list.index('3')
                    for i in range(len(details_str_list[index1_class_id])):
                        if 'GGA' in details_str_list[index1_class_id][i]:
                            index1 = details_str_list[index1_class_id][i].index('&')
                            index2 = details_str_list[index1_class_id][i].rindex('&')
                            direct_list['lat2'] = details_str_list[index1_class_id][i][index1 + 1:index2]
                            direct_list['lon2'] = details_str_list[index1_class_id][i][index2 + 1:]

                        if 'VTG' in details_str_list[index1_class_id][i]:
                            index1 = details_str_list[index1_class_id][i].index('&')
                            index2 = details_str_list[index1_class_id][i].rindex('&')
                            direct_list['cog2'] = details_str_list[index1_class_id][i][index1 + 1:index2 - 1]
                            direct_list['sog2'] = details_str_list[index1_class_id][i][index2 + 1:-1]
            except:
                pass

            try:
                if '4' in class_ID_list:
                    index1_class_id = class_ID_list.index('4')
                    for i in range(len(details_str_list[index1_class_id])):
                        temp1 = []
                        if 'DID' in details_str_list[index1_class_id][i]:
                            for j in range(len(details_str_list[index1_class_id][i])):
                                if details_str_list[index1_class_id][i][j] == '&':
                                    temp1.append(j)

                            direct_list['pitch'] = details_str_list[index1_class_id][i][temp1[0] + 1:temp1[1]]
                            direct_list['roll'] = details_str_list[index1_class_id][i][temp1[1] + 1:temp1[2]]
            except:
                pass

            try:
                if '5' in class_ID_list:
                    index1_class_id = class_ID_list.index('5')
                    for i in range(len(details_str_list[index1_class_id])):
                        if 'MWV' in details_str_list[index1_class_id][i]:
                            index1 = details_str_list[index1_class_id][i].index('&')
                            index2 = details_str_list[index1_class_id][i].rindex('&')
                            direct_list['wd1'] = details_str_list[index1_class_id][i][index1 + 1:index2]
                            direct_list['ws1'] = details_str_list[index1_class_id][i][index2 + 1:]
            except:
                pass

            try:
                if '6' in class_ID_list:
                    index1_class_id = class_ID_list.index('6')
                    for i in range(len(details_str_list[index1_class_id])):
                        if 'MWV' in details_str_list[index1_class_id][i]:
                            index1 = details_str_list[index1_class_id][i].index('&')
                            index2 = details_str_list[index1_class_id][i].rindex('&')
                            direct_list['wd2'] = details_str_list[index1_class_id][i][index1 + 1:index2]
                            direct_list['ws2'] = details_str_list[index1_class_id][i][index2 + 1:]
            except:
                pass

        except:
            pass
        # print('处理好的数据字典',direct_list)
        return direct_list


    def withdraw_300TEU_POWER_data(self,data_str:str):
        '''
        提取推进系统的数据
        '''
        POWER_DATA = {
        'DG1_PWR_KW':None,
        'DG2_PWR_KW':None,
        'DG3_PWR_KW':None,
        'DG1_SPD_RPM':None,
        'DG2_SPD_RPM':None,
        'DG3_SPD_RPM':None,
        'DB1_PWR_KW':None,
        'DB2_PWR_KW':None,
        'DG1_RUN':None,
        'DG2_RUN':None,
        'DG3_RUN':None,
        'DG1_BRK_CLS':None,
        'DG2_BRK_CLS':None,
        'DG3_BRK_CLS':None,
        'DB1_RUN':None,
        'DB2_RUN':None,
        'DB1_BRK_CLS':None,
        'DB2_BRK_CLS':None,
        'BUS_TIE_CLS':None,
        'MP1_SPD_REF_RPM':None,
        'MP1_STR_REF_DU':None,
        'MP1_SPD_FB_RPM':None,
        'MP1_STR_FB_DU':None,
        'MP1_PWR_KW':None,
        'MP1_BRK_CLS':None,
        'MP1_RUN':None,
        'MP1_ACK_FRM_MPS':None,
        'MP2_SPD_REF_RPM':None,
        'MP2_STR_REF_DU':None,
        'MP2_SPD_FB_RPM':None,
        'MP2_STR_FB_DU':None,
        'MP2_PWR_KW':None,
        'MP2_BRK_CLS':None,
        'MP2_RUN':None,
        'MP2_ACK_FRM_MPS':None,
        'BT1_SPD_REF_RPM':None,
        'BT1_SPD_FB_RPM':None,
        'BT1_PWR_KW':None,
        'BT1_BRK_CLS':None,
        'BT1_RUN':None,
        'BT1_ACK_FRM_MPS':None,
        'BT2_SPD_REF_RPM':None,
        'BT2_SPD_FB_RPM':None,
        'BT2_PWR_KW':None,
        'BT2_BRK_CLS':None,
        'BT2_RUN':None,
        'BT2_ACK_FRM_MPS':None
        }

        and_index_list = []
        for i in range(len(data_str)):
            if data_str[i] =='&':
                and_index_list .append(i)


        power_data_list = []
        for i in range(len(and_index_list)-1):
            power_data_list.append(data_str[and_index_list[i]+1:and_index_list[i+1]])

        power_data_list.append(data_str[and_index_list[-1]+1:])

        try:
            POWER_DATA['DG1_PWR_KW'] = float(power_data_list[1])
            POWER_DATA['DG2_PWR_KW'] = float(power_data_list[2])
            POWER_DATA['DG3_PWR_KW'] = float(power_data_list[3])
            POWER_DATA['DB1_PWR_KW'] = float(power_data_list[7])
            POWER_DATA['DB2_PWR_KW'] = float(power_data_list[8])


            DG_DB_DEVICE_STATE = int(power_data_list[9])
            POWER_DATA['DG1_RUN'] = (DG_DB_DEVICE_STATE & 0x01) >>0
            POWER_DATA['DG2_RUN'] = (DG_DB_DEVICE_STATE & 0x02)>>1
            POWER_DATA['DG3_RUN'] = (DG_DB_DEVICE_STATE & 0x04)>>2
            POWER_DATA['DG1_BRK_CLS'] = (DG_DB_DEVICE_STATE & 0x08)>>3
            POWER_DATA['DG2_BRK_CLS'] = (DG_DB_DEVICE_STATE & 16)>>4
            POWER_DATA['DG3_BRK_CLS'] = (DG_DB_DEVICE_STATE & 32)>>5

            POWER_DATA['DB1_RUN'] = (DG_DB_DEVICE_STATE & 64)>>6
            POWER_DATA['DB2_RUN'] = (DG_DB_DEVICE_STATE & 128)>>7
            POWER_DATA['DB1_BRK_CLS'] = (DG_DB_DEVICE_STATE & 256)>>8
            POWER_DATA['DB2_BRK_CLS'] = (DG_DB_DEVICE_STATE & 512)>>9

            POWER_DATA['BUS_TIE_CLS'] = (DG_DB_DEVICE_STATE & 1024)>>10

            POWER_DATA['MP1_PWR_KW'] = float(power_data_list[14])
            MP1_STATE = int(power_data_list[15])
            POWER_DATA['MP1_BRK_CLS']  = (MP1_STATE & 1) >>0
            POWER_DATA['MP1_RUN'] = (MP1_STATE & 2) >>1

            POWER_DATA['MP2_PWR_KW'] = float(power_data_list[24])
            MP2_STATE = int(power_data_list[25])
            POWER_DATA['MP2_BRK_CLS'] = (MP2_STATE & 1) >> 0
            POWER_DATA['MP2_RUN'] = (MP2_STATE & 2) >> 1

            POWER_DATA['BT1_PWR_KW'] = float(power_data_list[32])
            BT1_STATE = int(power_data_list[33])
            POWER_DATA['BT1_BRK_CLS'] = (BT1_STATE & 1)
            POWER_DATA['BT1_RUN'] = (BT1_STATE & 2)  >> 1

            POWER_DATA['BT2_PWR_KW'] = float(power_data_list[42])
            BT2_STATE = int(power_data_list[43])
            POWER_DATA['BT2_BRK_CLS'] = (BT2_STATE & 1)
            POWER_DATA['BT2_RUN'] = (BT2_STATE & 2) >> 1

            return POWER_DATA












        except Exception as err:
            pass
            print('withdraw power data error :--',err)


    def process_sensor_state(self,sensor_list:list,class_ID_list:list):
        pass
        '''
        处理传感器数据中，得到的传感器状态；
         ['*0$THS&27.6$HDT&27.6', '*1$THS&27.6$HDT&27.6', '*2$VTG&13.8T&4.7N$GGA&0004.596666N&00004.596666E', 
         '*3$VTG&13.8T&4.7N$GGA&0004.596666N&00004.596666E', '*4$DID&12.6&12.6&13.8', '*5$MWV&27.5&2.5', '*6$MWV&27.5&2.5']

        ['0', '1', '2', '3', '4', '5', '6']
        {
            'gyro1_alarm_flag':False,
            'gyro2_alarm_flag': False,
            'dgps1_alarm_flag': False,
            'dgps2_alarm_flag': False,
            'mru_alarm_flag': False,
            'wind1_alarm_flag': False,
            'wind2_alarm_flag': False
        }                           # 7个传感器的报警标志位

        '''
        sensor_state_flag = False

        for i in range(len(class_ID_list)):
            if 'NAN' in sensor_list[i]:
                if class_ID_list[i] =='0':#GC80
                    self.sensor_state['gyro1_alarm_flag'] =True
                if class_ID_list[i] =='1':#船供罗经
                    self.sensor_state['gyro2_alarm_flag'] =True
                if class_ID_list[i] == '2':# trimble
                    self.sensor_state['dgps1_alarm_flag'] = True

                if class_ID_list[i] =='3':
                    self.sensor_state['dgps2_alarm_flag'] =True

                if class_ID_list[i] =='4':
                    self.sensor_state['mru_alarm_flag'] =True
                if class_ID_list[i] =='5':
                    self.sensor_state['wind1_alarm_flag'] =True
                if class_ID_list[i] =='6':
                    self.sensor_state['wind2_alarm_flag'] =True

        if sensor_state_flag ==False:
            self.sensor_state = {
                'gyro1_alarm_flag': False,
                'gyro2_alarm_flag': False,
                'dgps1_alarm_flag': False,
                'dgps2_alarm_flag': False,
                'mru_alarm_flag': False,
                'wind1_alarm_flag': False,
                'wind2_alarm_flag': False
            }









if __name__ == '__main__':

    test_str = '*0$THS&27.6$HDT&27.6*1$THS&27.6$HDT&27.6*2$VTG&13.8T&4.7N$GGA&0004.596666N&00004.596666E*3$VTG&13.8T&4.7N$GGA&0004.596666N&00004.596666E*4$DID&12.6&12.6&13.8*5$MWV&27.5&2.5*6$MWV&27.5&2.5'
    with_obj =withdraw_datas_methods()
    with_obj.withdraw_300TEU_sensor_data(test_str)
