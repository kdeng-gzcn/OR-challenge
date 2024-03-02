import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import random

def simulation_time(events_num):
    '''
    simulate exp dist inter time
    :param events_num:
    :return:
    '''
    Lambda = events_num
    event_inter_times = [random.expovariate(Lambda) for _ in range(events_num)]
    event_times = [sum(event_inter_times[:i]) for i in range(1, events_num + 1)]
    return [event_inter_times, event_times]

def simulation_time_for_shift(data, shift):
    initial = 0

    if shift == 1:
        initial = 0
    elif shift == 2:
        initial = 8
    elif shift == 3:
        initial = 16

    for i in range(8):
        temp = data[data['Hour'] == initial + i]

        Arrival_info = simulation_time(len(temp))

        data.loc[temp.index, 'Arrival Inter Time'] = Arrival_info[0]
        data.loc[temp.index, 'Arrival Time'] = Arrival_info[1]
        data.loc[temp.index, 'Arrival Time'] = data.loc[temp.index, 'Arrival Time'].copy() + i

    return data

def simulation_data_to_excel(data, k, shift):
    demo = data
    demo['Arrival Inter Time'] = 0
    demo['Arrival Time'] = 0

    if shift == 'early':
        j = 1
    elif shift == 'day':
        j = 2
    else:
        j = 3

    shift_data = simulation_time_for_shift(demo, j)
    shift_data = shift_data.sort_values(by='Arrival Time')


    # to excel
    shift_data.to_excel(f'.\\simulated data\\day{k}\\{shift}.xlsx', index=False)
    print('successful!')
    return shift_data

class dataset:
    def __init__(self, week):
        '''
        import data
        '''
        if week == 1:
            self.week1 = pd.read_excel(r'./data/data.xlsx')
        elif week == 2:
            self.week1 = pd.read_excel(r'./data/OR Comp validation data.xlsx')

        self.station = pd.read_excel(r'./data/data.xlsx', sheet_name=1)
        self.station.set_index('Station No.', inplace=True)

        print(self.week1.head())

    def get_shift(self, k, j):
        '''

        :param k: dayk
        :param j: shiftj
        :return: df for dayk, shiftj
        '''
        df = self.week1[self.week1['Day'] == k]

        if j == 'early':
            df = df[(df['Hour'] >= 0) & (df['Hour'] < 8)]
        elif j == 'day':
            df = df[(df['Hour'] >= 8) & (df['Hour'] < 16)]
        elif j == 'night':
            df = df[(df['Hour'] >= 16) & (df['Hour'] < 24)]
        else:
            print('error')

        return df

    def get_simulation(self, k, j):
        '''

        :param k:
        :param j:
        :return: new df with simulated arrival time
        '''
        df = self.get_shift(k, j)
        df = simulation_data_to_excel(df, k, j)

        return df


#################################################### main ##############################################################
if __name__ == "__main__":
    dataset = dataset(2)
    df = dataset.get_simulation(12, 'night')
    print(df.to_string(), df.shape) # disp