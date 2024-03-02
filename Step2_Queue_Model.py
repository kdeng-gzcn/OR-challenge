import simpy
import math
import pandas as pd




class ShiftQueueModel:
    def __init__(self, solution, data, is_show):
        '''

        :param solution: strategy
        :param data: simulated df
        :param is_show: disp
        '''
        self.is_show = is_show
        self.solution = solution
        self.arrival_inter_times = list(data['Arrival Inter Time'].values)
        self.deployment_times = list(data['Deployment Time (hrs)'].values)
        self.priorities = list(data['Priority'].values)
        self.locations = [[x, y] for x, y in zip(data['Longitude'], data['Latitude'])]
        self.env = simpy.Environment()
        self.Stations = []

        for i in range(3):
            if self.solution[i]:
                temp_station = self.ServerResource(self.env, capacity=self.solution[i],
                                                   resource_type=f"Station {i + 1}")
                temp_station.total_idle_time = 0
                self.Stations.append(temp_station)
                self.env.process(self.track_idle_time(temp_station))

        self.events_num = []
        self.levels = []
        self.latitutes = []
        self.longitutes = []
        self.res_times = []
        self.tra_times = []
        self.is_on_time = []
        self.station_free_time = []
        self.arrival_times = []
        self.res_ac_times = []


        self.env.process(self.customer_generator(self.env, self.Stations, self.priorities, self.arrival_inter_times,
                                                 self.deployment_times, self.locations))


        # self.env.process(self.customer_generator(self.env, self.Stations, self.arrival_rates[1], priority=2,
        #                                          customer_service_times=self.deployment_times))
        # self.env.process(self.customer_generator(self.env, self.Stations, self.arrival_rates[2], priority=3,
        #                                          customer_service_times=self.deployment_times))

    def my_print(self, is_show, *x):

        if is_show == False:
            pass
        else:
            print(*x)

    def track_idle_time(self, resource):
        '''
        get free time for each station
        :param resource:
        :return:
        '''
        while self.env.now <= 8:
            yield self.env.timeout(0.0001)
            if len(resource.users) < resource.capacity:
                resource.total_idle_time += 0.0001

    def haversine(self, lon1, lat1, lon2, lat2):
        '''
        compute distance through lon & lat
        :param lon1:
        :param lat1:
        :param lon2:
        :param lat2:
        :return:
        '''
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        R = 6371.0

        distance = R * c * 0.621371
        return distance

    class ServerResource(simpy.PriorityResource):
        '''
        consider station as server resource
        queue principle should be priority
        '''

        def __init__(self, env, capacity, resource_type):
            super().__init__(env, capacity=capacity)

            self.resource_type = resource_type

            if int(resource_type.split()[-1]) == 1:
                self.location = (-4.2579871, 55.868709)
            if int(resource_type.split()[-1]) == 2:
                self.location = (-4.2164508, 55.849171)
            if int(resource_type.split()[-1]) == 3:
                self.location = (-4.2468263, 55.830168)

            self.total_idle_time = 0

    def customer_generator(self, env, resources, priorities, arrival_inter_times, customer_service_times, locations):
        '''
        load events as customer
        :param env:
        :param resources:
        :param priorities:
        :param arrival_inter_times:
        :param customer_service_times:
        :param locations:
        :return:
        '''
        customer_count = 0

        while customer_count < len(priorities):

            yield env.timeout(arrival_inter_times[customer_count])
            # yield env.timeout(1/arrival_rates)

            e_location =  locations[customer_count]
            # e_location = next(location_cycle)


            available_stations = [station for station in resources if station.count < station.capacity]

            if available_stations:
                distances = [self.haversine(station.location[0], station.location[1], e_location[0], e_location[1]) for
                             station in available_stations]
                min_distance = min(distances)
                resource = available_stations[distances.index(min_distance)]
            else:
                self.my_print(self.is_show, 'ALL Policemen are busy')
                queues = [len(station.queue) for station in resources]
                min_queue = min(queues)
                min_queue_indices = [i for i, value in enumerate(queues) if value == min_queue]
                temp = [self.haversine(resources[index].location[0], resources[index].location[1], e_location[0],
                                       e_location[1]) for index in min_queue_indices]
                min_distance = min(temp)
                resource = resources[min_queue_indices[temp.index(min_distance)]]


            level = 0
            if priorities[customer_count] == 'Immediate':
                level = 1
            elif priorities[customer_count] == 'Prompt':
                level = 2
            elif priorities[customer_count] == 'Standard':
                level = 3

            env.process(self.customer(env, f"Event {customer_count+1}", resource, level,
                                      customer_service_times[customer_count], e_location))

            customer_count += 1

    def customer(self, env, name, resource, priority, customer_service_time, location):
        '''
        property of event
        :param env:
        :param name:
        :param resource:
        :param priority:
        :param customer_service_time:
        :param location:
        :return:
        '''
        with resource.request(priority=priority) as req:
            if priority == 1:
                level = 'Immediate'
            elif priority == 2:
                level = 'Prompt'
            elif priority == 3:
                level = 'Standard'

            wait_start_time = env.now

            self.events_num.append(priority)

            if priority == 1:
                res_interval = 1
            elif priority == 2:
                res_interval = 3
            elif priority == 3:
                res_interval = 6

            temp = self.haversine(resource.location[0], resource.location[1], location[0], location[1])
            travel_t = temp / 30

            self.my_print(self.is_show,
                f'{round(env.now, 4)}: {level} {name} arrival, simulate location: {location}, should be solved by station: {resource.resource_type}, simulate travel time: {round(travel_t, 4)}')

            yield req

            res_time = env.now - wait_start_time
            self.res_times.append(res_time)

            if res_time <= res_interval:
                self.is_on_time.append(1)
            else:
                self.is_on_time.append(0)

            self.tra_times.append(travel_t)
            self.levels.append(level)
            self.latitutes.append(location[1])
            self.longitutes.append(location[0])
            self.arrival_times.append(wait_start_time)
            self.res_ac_times.append(env.now)

            self.my_print(self.is_show,
                f"{round(env.now, 4)}: after waiting for {round(env.now - wait_start_time, 4)} , {level} {name} is responsed by {resource.resource_type}")

            service_time = customer_service_time

            total_service_time = service_time + travel_t
            yield env.timeout(total_service_time)

            self.my_print(self.is_show, f"{round(env.now, 4)}: {level} {name} has been solved by {resource.resource_type}")

    def run(self):
        self.env.run()

    def get_all_events(self):
        '''

        :return: df for result events
        '''
        self.all_events = pd.DataFrame({
            'Arrival Time': self.arrival_times,
            'Response Actual Time': self.res_ac_times,
            'Level': self.levels,
            'Latitude': self.latitutes,
            'Longitude': self.longitutes,
            'Response Time': self.res_times,
            'Travel Time': self.tra_times,
            'Is On Time': self.is_on_time
        })

        self.my_print(self.is_show, self.all_events.to_string())

        return self.all_events

    def get_free_time_list(self):
        for station in self.Stations:
            self.my_print(self.is_show,
                f'Station {station.resource_type.split()[-1]} free time: {round(station.total_idle_time, 4)}')
            self.station_free_time.append(station.total_idle_time)
        return self.station_free_time

    def get_current_queue(self):
        queues = []
        for station in self.Stations:
            self.my_print(self.is_show,
                f"Station {station.resource_type.split()[-1]} Current Queue Size: {len(station.queue)}")
            queues.append(len(station.queue))
        return sum(queues)

    def get_results(self):
        '''

        :return: some critical indexes
        '''

        self.all_events = pd.DataFrame({
            'Arrival Time': self.arrival_times,
            'Response Actual Time': self.res_ac_times,
            'Level': self.levels,
            'latitude':self.latitutes,
            'longitude':self.longitutes,
            'Response Time': self.res_times,
            'Travel Time': self.tra_times,
            'Is On Time': self.is_on_time
        })


        prompt_events = self.all_events[self.all_events['Level'] == 'Prompt' ]
        prompt_events = prompt_events[prompt_events['Response Time'] != 0]

        im_events = self.all_events[self.all_events['Level'] == 'Immediate']
        im_events = im_events[im_events['Response Time'] != 0]


        st_events = self.all_events[self.all_events['Level'] == 'Standard']
        st_events = st_events[st_events['Response Time'] != 0]

        p_times = []
        i_times = []
        s_times = []

        for time in prompt_events['Response Time']:
            p_times.append(time)

        for time in im_events['Response Time']:
            i_times.append(time)

        for time in st_events['Response Time']:
            s_times.append(time)

        p_tras = []
        i_tras = []
        s_tras = []

        for time in self.all_events[self.all_events['Level'] == 'Prompt' ]['Travel Time']:
            p_tras.append(time)

        for time in self.all_events[self.all_events['Level'] == 'Immediate']['Travel Time']:
            i_tras.append(time)

        for time in self.all_events[self.all_events['Level'] == 'Standard']['Travel Time']:
            s_tras.append(time)

        p_average_res_time = sum(p_times) / len(p_times) if p_times else 0
        i_average_res_time = sum(i_times) / len(i_times) if i_times else 0
        s_average_res_time = sum(s_times) / len(s_times) if s_times else 0

        p_avgT = sum(p_tras) / len(p_tras) if p_tras else 0
        i_avgT = sum(i_tras) / len(i_tras) if i_tras else 0
        s_avgT = sum(s_tras) / len(s_tras) if s_tras else 0

        i_rt = self.all_events[self.all_events['Level'] == 'Immediate']['Is On Time']
        p_rt = self.all_events[self.all_events['Level'] == 'Prompt']['Is On Time']
        s_rt = self.all_events[self.all_events['Level'] == 'Standard']['Is On Time']

        i_PRT = i_rt.sum()/len(i_rt) * 100
        p_PRT = p_rt.sum()/len(p_rt) * 100
        s_PRT = s_rt.sum()/len(s_rt) * 100


        average_tra_time = sum(self.tra_times) / len(self.tra_times) if self.tra_times else 0
        percentage_on_time = (sum(self.is_on_time) / len(self.is_on_time) if self.is_on_time else 0) * 100

        self.my_print(self.is_show, f"\nImmediate Average Wait Time: {round(i_average_res_time, 4)}")
        self.my_print(self.is_show, f"\nPrompt Average Wait Time: {round(p_average_res_time, 4)}")
        self.my_print(self.is_show, f"\nStandard Average Wait Time: {round(s_average_res_time, 4)}")

        self.my_print(self.is_show, f"\nAverage Travel Time: {round(average_tra_time, 4)}")

        self.my_print(self.is_show, f"\nOn Time %: {round(percentage_on_time, 4)} % \n")

        results = [[i_average_res_time, p_average_res_time, s_average_res_time], average_tra_time, percentage_on_time, self.res_ac_times[-1], [i_avgT, p_avgT, s_avgT], [i_PRT, p_PRT, s_PRT], max(self.arrival_times)]

        return results

def events_to_excel(solution, data_name, to_excel_name):
    model = ShiftQueueModel(solution, pd.read_excel(data_name), False)
    model.run()
    events = model.get_all_events()
    events.to_excel(f'{to_excel_name}')
    print(f'to excel successfully{to_excel_name}')
    return events

#################################################### main ##############################################################
if __name__ == "__main__":
    # evaluation
    # [17, 8, 15], f(x) = 4.127680485583175

    # [22, 18, 0], f(x) = 9.466486097628566

    # [8, 0, 7], f(x) = 6.106436093298256


    k = 10
    solution = [8, 0, 7]





    if sum(solution) == 15:
        shift = 'early'
    elif sum(solution) == 25:
        shift = 'day'
    elif sum(solution) == 40:
        shift = 'night'
    else:
        print('error!!!')

    day1_early = ShiftQueueModel(solution, pd.read_excel(f'./simulated data/day{k}/{shift}.xlsx'), True) # disp
    day1_early.run()
    day1_early.get_all_events()
    results = day1_early.get_results()
    delta = results[3] - results[6]

    print('delta', delta)
    print('fitness1', delta + (100 / results[2]) * (
                0.1 * results[0][0]  + 0.3 * results[0][1] + 0.6 * results[0][2]  + results[1] * 10))
    print('fitness2', delta + (100 / results[2]) * (
                0.33 * results[0][0]  + 0.33 * results[0][1]  + 0.33 * results[0][2]  + results[1] * 10))

    print('make table:', '\n'
          ,results[0][0], results[4][0], results[5][0], '\n'
          , results[0][1], results[4][1], results[5][1], '\n'
          , results[0][2], results[4][2], results[5][2])

    # events_to_excel(solution, r'./simulated data/day8/day.xlsx', r'./solution data/day8/day/11 8 6.xlsx')