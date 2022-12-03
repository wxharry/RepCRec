import os

for i in range(1,25):
    command1 = "python3 repcrec.py tests/test" + str(i) + ".txt > output" + str(i) + ".txt"
    # command2 = "diff a.txt refout/out" + str(i) + "_16_f"
    # command2 = "~frankeh/Public/mmu -f128 -af -oOPFS inputs/in"+ str(i)+ " inputs/rfile > b.txt"
    # command3 = "diff a.txt b.txt"
    os.system(command1)
    # os.system(command2)
    # os.system(command3)

os.system("python3 repcrec.py tests/test3.5.txt > output3.5.txt")
os.system("python3 repcrec.py tests/test3.7.txt > output3.7.txt")
