from Step2_Queue_Model import ShiftQueueModel
import numpy as np
import pandas as pd
import random

class Genetic(object):
    def __init__(self, fitness, vec_sum, data_name):
        '''
        load data
        :param fitness:
        :param vec_sum:
        :param data_name:
        '''
        self.fitness = fitness
        self.vec_sum = vec_sum
        self.data_name = data_name

    def get_initial_solutions(self):
        return self.random_solutions

    def get_track_fit_values(self):
        '''
        track fitness for evaluating algorithm
        :return:
        '''
        return self.fit_values

    def get_random_solution(self, vec_sum):
        '''
        to create initial pop
        :param vec_sum:
        :return: random integer
        '''
        x = np.random.randint(0, vec_sum + 1)
        y = np.random.randint(0, vec_sum + 1 - x)
        z = vec_sum - x - y
        return [x, y, z]

    def elite_select(self, pop, select_num):
        '''
        step in algorithm
        :param pop:
        :param select_num:
        :return: selection based on fitness
        '''
        scores = sorted([(self.fitness(vec, self.data_name), vec) for vec in pop])
        ranked = [vec for score, vec in scores]
        return ranked[:select_num]

    def plusminus1_15(self, vec):
        '''
        one of operators
        :param vec:
        :return:
        '''
        i = random.sample(range(len(vec)), 2)

        if vec[i[0]] != 15 and vec[i[1]] != 0:
            vec[i[0]], vec[i[1]] = vec[i[0]] + 1, vec[i[1]] - 1
        else:
            vec = self.plusminus1_15(vec)

        if round(random.random()):
            vec = self.plusminus1_15(vec)

        return vec

    def crossover(self, vec):
        '''
        one of operators
        :param vec:
        :return:
        '''
        i = random.sample(range(len(vec)), 2)

        vec[i[0]], vec[i[1]] = vec[i[1]], vec[i[0]]

        if round(random.random()):
            vec = self.crossover(vec)

        return vec

    def mutate(self, vec):
        '''
        one of operators
        :param vec: solution
        :return: mutate input solution
        '''

        if round(random.random()):
            i = random.randint(1, len(vec) - 1)
            vec = vec[i:] + vec[:i]
        else:
            # +1-1
            vec = self.crossover(vec)

        return vec

    def run(self):
        # set up params
        elite = 0.5
        mutprob = 0.3
        popsize = 16
        vec_sum = self.vec_sum

        maxiter = 20

        topelite = int(elite * popsize)

        # initial solution
        pop = []
        for i in range(popsize):
            pop.append(self.get_random_solution(vec_sum))

        self.random_solutions = pop
        self.fit_values = []

        # start
        for i in range(maxiter):
            print(f'This is NO.{i + 1} iteration')

            print(pop)
            pop = self.elite_select(pop, topelite)

            # if self.disp:
            self.fit_values.append(self.fitness(pop[0], self.data_name))
            print(f"the optimal solution is {pop[0]}, f(x) = {self.fitness(pop[0], self.data_name)}")

            while len(pop) < popsize and i != maxiter - 1:

                variant = random.randint(0, topelite - 1)

                if random.random() < mutprob:
                    pop.append(self.mutate(pop[variant].copy()))
                else:
                    pop.append(self.plusminus1_15(pop[variant].copy()))

        print(f"Optimal Solution:{pop[0]}, Fitness Value:{self.fitness(pop[0], self.data_name)}")
        return pop[0]

def fitness(solution, data_name):
    '''
    fitness for evaluating queue system
    :param solution:
    :param data_name:
    :return: evaluation for a strategy
    '''
    model = ShiftQueueModel(solution, pd.read_excel(data_name), False)
    model.run()

    results = model.get_results()

    # free_times = model.get_free_timelist()

    delta = results[3] - results[6]
    # print(delta)

    if delta > 0.33:
        # overload
        return delta + (100 / results[2]) * (
                    0.1 * results[0][0]+ 0.3 * results[0][1]+ 0.6 * results[0][2] + results[1] * 10)
    elif delta <= 0.33:
        # surplus
        return delta + (100 / results[2]) * (
                    0.33 * results[0][0] + 0.33 * results[0][1] + 0.33 * results[0][2] + results[1] * 10)

#################################################### main ##############################################################
if __name__ == "__main__":

    k = 10
    shift = 'early'








    if shift == 'early':
        vec = 15
    if shift == 'day':
        vec = 25
    if shift == 'night':
        vec = 40

    model = Genetic(fitness, vec_sum=vec, data_name=f'.\simulated data\day{k}\\{shift}.xlsx')
    model.run() # disp