from Step2_Queue_Model import ShiftQueueModel
from Step3_Genetic_Algorithm import Genetic
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

def get_random_solution(vec_sum):
    '''
    to create random initial pop
    :param vec_sum:
    :return: random integer
    '''
    x = np.random.randint(0, vec_sum + 1)
    y = np.random.randint(0, vec_sum + 1 - x)
    z = vec_sum - x - y
    return [x, y, z]

def fitness_feasible(solution, data_name):
    '''
    fitness for evaluating queue system
    :param solution:
    :param data_name:
    :return: evaluation for a strategy
    '''
    model = ShiftQueueModel(solution, pd.read_excel(data_name), False)
    model.run()

    results = model.get_results()

    return results[0][0] + results[1]*10

# evaluation
def get_feasible_solutions(k, j):
    '''
    select feasible solutions by algorithm
    :param k:
    :param j:
    :return:
    '''
    if j == 'early':
        vec_sum = 15
    elif j == 'day':
        vec_sum = 25
    elif j == 'night':
        vec_sum = 40
    else:
        vec_sum = 0
        print('error!')
    model = Genetic(fitness_feasible, vec_sum=vec_sum, data_name=f'.\\simulated data\\day{k}\\{j}.xlsx')
    model.run()  # disp

def evaluation(optimal, feasible,  k, j):
    '''
    record optimal, feasible, random solutions' results
    need to select optimal and feasible solutions by hand
    :param k:
    :param j:
    :return: data for plotting scatter
    '''
    df = pd.read_excel(f'.\\simulated data\\day{k}\\{j}.xlsx')
    columns_names = ["AvgRI", "AvgTI", "AvgRP", "AvgTP", "AvgRS", "AvgTS"]

    # 1
    # need to select feasible solutions

    optimal_results = []
    model = ShiftQueueModel(optimal, df, False)
    model.run()
    result = model.get_results()
    # print([result[0][0], result[4][0], result[0][1], result[4][1], result[0][2], result[4][2]])
    optimal_results.append([result[0][0], result[4][0], result[0][1], result[4][1], result[0][2], result[4][2]])
    optimal_df = pd.DataFrame(optimal_results, columns=columns_names)

    # 2
    # need to select feasible solutions

    feasible_results = []
    for solution in feasible:
        model = ShiftQueueModel(solution, df, False)
        model.run()
        result = model.get_results()
        # print([result[0][0], result[4][0], result[0][1], result[4][1], result[0][2], result[4][2]])
        feasible_results.append([result[0][0], result[4][0], result[0][1], result[4][1], result[0][2], result[4][2]])

    feasible_df = pd.DataFrame(feasible_results, columns=columns_names)

    # 3
    random = []
    if j == 'early':
        vec_sum = 15
    elif j == 'day':
        vec_sum = 25
    elif j == 'night':
        vec_sum = 40
    else:
        vec_sum = 0
        print('error!')
    for i in range(15): # create 15 solutions
        random.append(get_random_solution(vec_sum))

    random_results = []
    for solution in random:
        model = ShiftQueueModel(solution, df, False)
        model.run()
        result = model.get_results()
        random_results.append([result[0][0], result[4][0], result[0][1], result[4][1], result[0][2], result[4][2]])

    random_df = pd.DataFrame(random_results, columns=columns_names)

    # print
    print(optimal_df.to_string())
    print(feasible_df.to_string())
    print(random_df.to_string())

#################################################### main ##############################################################
# get_feasible_solutions(k=8, j='day')
# evaluation(optimal=[11, 8, 6], feasible=[[14, 0, 11], [10, 13, 2], [10, 3, 12], [25, 0, 0]], k=8, j='day')


