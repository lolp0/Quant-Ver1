'''
Deep learning reinfocement based trading
State: return_t, return_t-1. return_t-2....,return_t-m
instant reward : Ft * return_t 1
Q-value : instant reward   max(Q(a|s 1))
Created on 14 May 2016
Using two layers CNN

v4 : use random memory to train to avoid correlation of the data
v5 : discount rate - > 0.000009 (four rate, compound annual interest rate is 2%)
* discount rate need to be discussed
v6 : two model : online network and target network, online use to calculate action, 
and target network used to calculate the value of greedy policy, detailed in double DQN
change memory.get_batch
v6 test : for running on desktop UNSW
v6 test shared variable: store variable on GPU using theano.shared

@author: Daytona
'''

#import os
#os.environ['CUDA_LAUNCH_BLOCKING'] = '1'
import theano
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers.core import Dense
from keras.optimizers import sgd
#from keras.utils.visualize_util import  plot
import matplotlib.pyplot as plt
import datetime
import logging
from time import gmtime, strftime
from theano import shared, config
import json
import copy

ACTION_LIST = [1,0,-1]

class FX_Market():
    def __init__(self,ret_train, look_back_term, transaction_cost):
        self.__ret_train = shared(np.asarray(ret_train), name="ret_train")
        self.__look_back_term = shared(look_back_term,name="look_back_term")
        self.__previous_action = shared(1,name="previous_action")
        self.__transaction_cost = shared(transaction_cost,name="transaction_cost")

    def reset(self):
        self.__previous_action.set_value(1)

    def get_state(self,t):
        state = np.zeros((1,self.__look_back_term))
        state[0] = self.__ret_train.get_value()[t - self.__look_back_term.get_value() +  1 : t + 1]
        return state

    def get_instant_reward(self, t , action):
        return ACTION_LIST[action] * self.__ret_train.get_value()[t+1] - \
            self.__transaction_cost * abs(ACTION_LIST[self.__previous_action] - ACTION_LIST[action])
        
    def act(self, t, action):
        state_new = self.get_state(t + 1)
        reward = self.get_instant_reward(t, action)
        self.__previous_action = action
        return state_new, reward


class Trading_Memory():
    def __init__(self,max_memory, discount = 0.9):
        self.__max_memory = max_memory
        self.__memory = list()
        self.discount = discount

    def memory(self,state, state_new, action, reward):
        self.__memory.append([state, state_new, action, reward])
        if len(self.__memory) > self.__max_memory:
            del self.__memory[0]

    def get_batch(self, target_model,online_model, batch_size=30):
        # use target_model to decide greedy policy (action), 
        # and target_model to calculate the value 
        len_memory = len(self.__memory)

        num_actions = target_model.output_shape[-1]

        env_dim = self.__memory[0][0].shape[1]

        inputs = np.zeros((min(len_memory, batch_size), env_dim))
        targets = np.zeros((inputs.shape[0], num_actions))

        for i, idx in enumerate(np.random.randint(0, len_memory,size=inputs.shape[0])):
            state, state_new, action, reward = self.__memory[idx]
            inputs[i:i+1] = state
            
            targets[i] = target_model.predict(state)[0]
            action_next = np.argmax(online_model.predict(state_new)[0])
            Q_sa = target_model.predict(state_new)[0][action_next]
            
            targets[i, action] = reward + self.discount * Q_sa
        return inputs, targets

def run():
    global ACTION_LIST
    # parameters
    epsilon = 0.1  # exploration
    num_actions = len(ACTION_LIST)  # [buy, hold, sell]
    transcation_cost = 0.0005
    epoch = 150
    max_memory = 1000000
    hidden_size = 600
    batch_size = 50
    look_back_term = 200
    training_period_start = 0
    training_period_stop = 10000
    learning_rate = 0.1
    discount_rate = 0.95
    step_size = 10 # iterate step to update target_model
    input_data = "GBPUSD240.csv"

    # log
    time_start_epoch = datetime.datetime.now()
    time_start = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    log_name = '../log/DRL_Learning_v6_' + time_start + '.log'
    logging.basicConfig(filename=log_name,level=logging.DEBUG)
    logging.info("Time start : " + str(time_start))
    logging.info("Input data :" + input_data)
    logging.info("Parameter setting :")
    logging.info("epsilon = " + str(epsilon))
    logging.info("transaction_cost = " + str(transcation_cost))
    logging.info("epoch ="  + str(epoch))
    logging.info("max_memory = " + str(max_memory))
    logging.info("batch_size = " + str(batch_size))
    logging.info("look back term = " + str(look_back_term))
    logging.info("hidden_size = " + str(hidden_size))
    logging.info("training period = " + str(training_period_start) + " ~ " + str(training_period_stop))
    logging.info("learning rate = " + str(learning_rate))
    logging.info("discount rate = " + str(discount_rate))
    logging.info("step_size = " + str(step_size))
    print "log start"

    # import return data
    data = pd.read_csv("../Data/" + input_data,header=None)
    close = data[5].values
    ret_train = (close[1:] - close[:-1])[training_period_start : training_period_stop]
    
    #ret_train_shared = shared(np.asarray(ret_train), name="ret_train")
    #print ret_train_shared.get_value()
    
    model = Sequential()
    model.add(Dense(hidden_size, input_shape=(look_back_term,), activation='relu'))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(num_actions))
    model.compile(sgd(lr=learning_rate), "mse")
    
    target_model = copy.deepcopy(model)
    
    env = FX_Market(ret_train = ret_train, look_back_term = look_back_term, transaction_cost = transcation_cost)
    trading_his = Trading_Memory(max_memory = max_memory, discount=discount_rate)
    

    # Train
    return_list = []
    for e in range(epoch):
        print "epoch : " + str(e)
        env.reset()
        accumulate_ret = [0.0]
        if e % step_size == 0:
            target_model = copy.deepcopy(model)
        for t in range(look_back_term - 1 , len(ret_train) - 2) :
            state = env.get_state(t)
            # decide action
            if np.random.rand() < epsilon:
                action = np.random.randint(0, num_actions, size=1)
            else:
                q = target_model.predict(state)
                action = np.argmax(q[0])

            new_state, reward = env.act(t, action)

            accumulate_ret.append(accumulate_ret[-1]  + reward)

            trading_his.memory(state, new_state, action, reward)
            
            inputs, targets = trading_his.get_batch(target_model, model,batch_size=batch_size)
            
            model.train_on_batch(inputs, targets)
        print "accumulate return : " + str(accumulate_ret[-1])
        return_list.append(accumulate_ret[-1])
        logging.info("accumulate return : " + str(accumulate_ret[-1]))
        loop_time = datetime.datetime.now() - time_start_epoch
        time_left = float(loop_time.seconds) / 3600.0 / float(e+1) * float(epoch - e + 1)
        print "left time : " + str(time_left) + " hours"
        
    result = pd.DataFrame()
    result["accumulate return"] = return_list
    result.to_csv("../Result_Data/DRL_v6_result_" + time_start + ".csv")

    model.save_weights("../Model/DRL_model_v6_" + time_start + ".h5", overwrite=True)
    with open("../Model/DRL_model_v6_" + time_start + ".json", "w") as outfile:
        json.dump(model.to_json(), outfile)

    #plt.plot(range(len(return_list)),return_list,"r.")
    #plt.show()
    #test(model, ret_test)

    time_used = datetime.datetime.now() - time_start_epoch
    time_used = float(time_used.seconds) / 3600.0
    logging.info("Processing time : " + str(time_used) + " hours")
    print "finished"

if __name__ == '__main__': run()
