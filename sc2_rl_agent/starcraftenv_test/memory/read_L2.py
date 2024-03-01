import os
import json

def convert_to_desired_format(L2_file):
    # 读取L1_observation.json
    with open(L2_file, 'r', encoding='utf-8') as file:
        L2_data = json.load(file)
        print("len of L2_data: ", len(L2_data))
        print("__________________________________________________________")
        print(L2_data[0][0])
        print(L2_data[1][0])
        print(L2_data[2][0])
        print(L2_data[3][0])
        print(L2_data[4][0])


        print("__________________________________________________________")

convert_to_desired_format("commander.json")