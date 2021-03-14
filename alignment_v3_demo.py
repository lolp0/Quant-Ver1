# @dMingjie
# Alignment of two fibers fixed on two Thorlabs MX606 Stage with power meter

import sys
sys.path.insert(0, ".\\cdll_lib")
import time
import pdb
from tqdm import tqdm
from time import sleep

import MotorList
from StepperMotor import *
# from PiezoMotor import *
from PowerMeter import *

#################### Parameter setting ####################

# Homing motor when intializing motor
IF_HOME = False
# Programme sleep time to wait for the finish of homing motor
HOME_SLEEP_TIME = 20
# Centering motor when initializing motor
IF_CENTERING = False

# Moving step when searching the best position of SM motor
# Unit is mm for Stepper motor
SM_MOV_STEP = [0.1, 0.05, 0.025, 0.0125, 0.00625]
# Moving step when searching the best position of PZT motor
PZ_MOV_STEP = []
# Will loop the stepper motor searching action again if the power increment is lower
# than this threshold
SM_LOOP_POWER_THRESHOLD = 1.1

# Power meter channel used if applicable
POWER_METER_CHANNEL = "B"
# GPIB channel number for power meter
PM_GPIB_CHANNEL = 5

# Motor movement limit and centring position for SM motor
LINEAR_SM_UP_LIMIT = 4
LINEAR_SM_LOW_LIMIT = 0
LINEAR_SM_MID_POSITION = (LINEAR_SM_UP_LIMIT + LINEAR_SM_LOW_LIMIT) / 2

ROTATE_SM_UP_LIMIT = 6
ROTATE_SM_LOW_LIMIT = 0
ROTATE_SM_MID_POSITION = (ROTATE_SM_UP_LIMIT + ROTATE_SM_LOW_LIMIT) / 2

# Motor movement limit and centring position for PZT motor
LINEAR_PZ_UP_LIMIT = 4
LINEAR_PZ_LOW_LIMIT = -4
LINEAR_PZ_MID_POSITION = (LINEAR_PZ_UP_LIMIT + LINEAR_PZ_LOW_LIMIT) / 2

ROTATE_PZ_UP_LIMIT = 6
ROTATE_PZ_LOW_LIMIT = -6
ROTATE_PZ_MID_POSITION = (ROTATE_PZ_UP_LIMIT + ROTATE_PZ_LOW_LIMIT) / 2

###########################################################


def sm_move_higher_power_v2(motor_list, step_list, power_meter):
    iteration = 0
    for step in step_list:
        movement_dict = {}
        max_power_mot_idx = None
        max_power = 0
        current_power = power_meter.query_power()
        previous_power = 1 / 1e100
        while current_power / previous_power >= SM_LOOP_POWER_THRESHOLD:
            iteration += 1
            print ("Iteration {}, movement step {} mm, start searching....".format(iteration, step))
            previous_power = power_meter.query_power()
            for mot_idx in tqdm(range(len(motor_list))):
                movement, power = sm_search_bidirection(motor_list[mot_idx], step, power_meter)
                movement_dict[mot_idx] = movement
                if power > max_power:
                    max_power = power
                    max_power_mot_idx = mot_idx
            motor_list[max_power_mot_idx].move_to(movement_dict[max_power_mot_idx])
            current_power = power_meter.query_power()
            
            print("Iteration {}, movement step {} mm, searching result: Motor {} of {} current position {:.4f} nm, power is {:.3f} microW.".format(
                iteration, step, motor_list[max_power_mot_idx]._movement, motor_list[max_power_mot_idx]._stage, motor_list[max_power_mot_idx].get_position(), 
                power_meter.query_power() * 1e6))

def sm_search_bidirection(motor, step, power_meter):
    # step motor, linear movement
    # find the movement having highr power
    # positive = 1 / negative = -1 / stand still = 0

    power_dict = {}

    power_zero = power_meter.query_power()
    position_zero = motor.get_position()

    power_dict[0] = power_zero
    motor.move_to(position_zero + step)
    power_dict[1] = power_meter.query_power()
    motor.move_to(position_zero - step)
    power_dict[-1] = power_meter.query_power()
    motor.move_to(position_zero)

    max_movement = max(power_dict, key=power_dict.get)

    return position_zero + max_movement * step, power_dict[max_movement]


def pz_linear_move_higher_power(motor, step, power_meter):
    # return positive = 1 / negative = -1 / stand still = 0
    # TODO

    return movement


def pz_rotate_move_higher_power(motor, step, power_meter):
    # return positive = 1 / negative = -1 / stand still = 0
    # TODO

    return movement


def main():
    # initialize
    initialize_device()

    # initialize six Stepper motors
    stepperMotorLinearContainer = [SM_Motor(i[0], i[1], i[
                                            2], i[3], "Linear", if_home=IF_HOME, movement_limit_upper=LINEAR_SM_UP_LIMIT,
                                            movement_limit_lower=LINEAR_SM_LOW_LIMIT) for i in MotorList.Stepper_Motor_Linear_List.values()]
    stepperMotorRotationContainer = [SM_Motor(i[0], i[1], i[
                                              2], i[3], "Rotation", if_home=IF_HOME, movement_limit_upper= ROTATE_SM_UP_LIMIT,
                                              movement_limit_lower = ROTATE_SM_LOW_LIMIT) for i in MotorList.Stepper_Motor_Rotation_List.values()]

    print ("Initilaze motors completed.")
    if IF_HOME:
        for mot in stepperMotorLinearContainer + stepperMotorRotationContainer:
            mot.move_home_position(wait=False)
            print("Waiting for Homing...")
            sleep(HOME_SLEEP_TIME)

    # initialize Stepper Motor
    if IF_CENTERING:
        for mot in stepperMotorLinearContainer:
            mot.move_to(LINEAR_SM_MID_POSITION)
        for mot in stepperMotorRotationContainer:
            mot.move_to(ROTATE_SM_MID_POSITION)

    # initialize Power meter
    powerMeter = Power_Meter(PM_GPIB_CHANNEL, POWER_METER_CHANNEL)

    # seraching best position
    sm_move_higher_power(stepperMotorLinearContainer + stepperMotorRotationContainer, SM_MOV_STEP, powerMeter)

    ######################## PZT MOVEMENT ########################
    # initialize six Piezo motor
    # piezoMotorContainer = [PZ_Motor(list(i.values[0]), list(
    #    i.values[1])) for i in MotorList.Stepper_Motor_List]
    # TODO

    print("Position alignment finished. Current power is {:.3f} microW".format(powerMeter.query_power() * 1e6))

if __name__ == '__main__':
    main()
