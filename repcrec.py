""" repcrec
main script

author: Xiaohan Wu, Yulin Hu
NYU NetID: xw2788, yh2094

"""
import argparse
import re

from src.taskmanager import TaskManager
from src.datamanager import DataManager
from src.variable import Variable

def parse_args():
    parser = argparse.ArgumentParser(
                    prog = 'repcerc',
                    description = 'What the program does')
    parser.add_argument('-f', '--filename')

    # TBD: semantic check
    # make sure users are not using both file input and std input
    # print help if the inputs are not valid
    return parser.parse_args()

def parse_instruction(line, tm, dm_list):
    """
    parse a line to use the corresponding functions
    each line is supposed to be a single instruction
    """
    pattern = "(.*)\((.*)\)"
    result = re.findall(pattern, line)
    if len(result) == 1:
        instruction, targets = result[0]
        if instruction in TaskManager.instructions:
            # add quote to targets to make them strings when convert instructions to functions
            params = ','.join([f"'{t}'" for t in targets.split(',')])
            eval(f"tm.{instruction}({params})", {'tm': tm})
        elif instruction in DataManager.instructions:
            eval(f"dm_list[{targets[0]}].{instruction}()", {'dm_list': dm_list})
        else:
            print(f"some unknown command {instruction}")
    else:
        print("Error: invalid input format detected.")
        return None

def main():

    # argparse
    args = parse_args()

    # initial states
    tm = TaskManager(1)
    dm_list = {i+1: DataManager(i+1) for i in range(10)}

    # initialize data
    for i in range(1, 21):
        if i % 2: # odd numbers are at one site each
            dm_list[i%10+1].set_variable(Variable(f"x{i}", i*10, False))
        else: # even numbers are at all sites
            for dm in dm_list.values():
                dm.set_variable(Variable(f"x{i}", i*10, True))

    # show init sites with data
    # for _, dm in dm_list.items():
    #     dm.dump()

    # input from file if args.filename is not None
    if args.filename:
        with open(args.filename, 'r') as f:
            for line in f:
                if line == '\n':
                    # a new tick
                    # deadlock detection
                    continue
                else:
                    parse_instruction(line, tm, dm_list)
    # input from std input if args.filename is None
    else:
        pass

if __name__ == "__main__":
    main()