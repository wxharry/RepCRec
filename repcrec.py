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
                    prog = 'repcrec',
                    description = 'What the program does')
    parser.add_argument('filename')

    # TBD: semantic check
    # make sure users are not using both file input and std input
    # print help if the inputs are not valid
    return parser.parse_args()

def parse_instruction(line, tm, dm_list, tick):
    """
    parse a line to use the corresponding functions
    each line is supposed to be a single instruction
    """
    pattern = "(.*)\((.*)\)"
    result = re.findall(pattern, line)
    if len(result) == 1:
        instruction, params = result[0]
        if instruction in TaskManager.instructions:
            tm.parse_instruction(instruction, params, tick)
        if instruction in DataManager.instructions:
            # print(params)
            # print(dm_list)
            dm_list[int(params)].parse_instruction(instruction, tick)
    else:
        print(f"Error: invalid input format {line}.")
        return None

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

    # show init sites with data
    # for _, dm in dm_list.items():
    #     dm.dump()

    # input from file if args.filename is not None
    tick = 1
    if args.filename:
        with open(args.filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line == '':
                    tick += 1
                    # deadlock detection
                    continue
                # handle comments
                elif line.startswith('//'):
                    continue
                else:
                    if '/' in line:
                        line = line[:line.index('/')]
                    parse_instruction(line, tm, dm_list, tick)
    # input from std input if args.filename is None
    else:
        pass

if __name__ == "__main__":
    main()