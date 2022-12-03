""" repcrec
main script

author: Xiaohan Wu, Yulin Hu
NYU NetID: xw2788, yh2094

"""
import argparse
import re
import os

from src.taskmanager import TaskManager
from src.datamanager import DataManager
from src.variable import Variable
from src.art import title

def parse_args():
    parser = argparse.ArgumentParser(
                    prog = 'repcrec',
                    description = 'Distributed replicated concurrency control and recovery')
    parser.add_argument('filename', nargs='?',
                    help='input filename')

    parser.add_argument('-i', '--interactive', default=False, action='store_true',
                    help='enter interactive mode')

    # TBD: semantic check
    # make sure users are not using both file input and std input
    # print help if the inputs are not valid
    return parser.parse_args()

def parse_instruction(line, tm, dm_list, tick):
    """
    parse a line to use the corresponding functions
    each line is supposed to be a single instruction
    """

    # remove comments
    if '//' in line:
        line = line[:line.index('/')].strip()
    # parse command if line is not empty
    if not line:
        return

    # print(line)
    pattern = "(.*)\((.*)\)"
    result = re.findall(pattern, line)
    if len(result) == 1:
        instruction, params = result[0]
        if instruction.lower() in TaskManager.instructions:
            r = tm.parse_instruction(instruction, params, tick)
            if r :
                print(r)
        # if instruction.lower() in DataManager.instructions:
        #     r = dm_list[int(params)].parse_instruction(instruction, tick)
        #     if r:
        #         print(r)
    else:
        print(f"Error: invalid input format {line}.")
        return None
    return

def main():

    # argparse
    args = parse_args()

    # initial states
    dm_list = {i+1: DataManager(i+1) for i in range(10)}

    # initialize data
    for i in range(1, 21):
        if i % 2: # odd numbers are at one site each
            dm_list[i%10+1].set_variable(Variable(f"x{i}", i*10, 0, False))
        else: # even numbers are at all sites
            for dm in dm_list.values():
                dm.set_variable(Variable(f"x{i}", i*10, 0, True))

    tm = TaskManager(1, dm_list)

    # input from file if args.filename is not None
    if args.filename:
        with open(args.filename, 'r') as f:
            tick = 1
            for line in f:
                line = line.strip()
                if not line:
                    continue
                tick += 1
                parse_instruction(line, tm, dm_list, tick)
    # input from std input if args.filename is None
    if not args.filename:
        tick = 0
        # if screen will be cleared for linux or mac
        if os.name == 'posix':
            os.system('clear')
        # else screen will be cleared for windows
        else:
            os.system('cls')

        print(title)
        while True:
            line = input("> ")
            if line.lower().strip() in ['exit', 'q', 'quit']:
                print("Bye~")
                break
            line = line.strip()
            # skip empty lines
            if not line:
                continue
            tick += 1
            parse_instruction(line, tm, dm_list, tick)
            

if __name__ == "__main__":
    main()
