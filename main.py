import re
import getopt
import sys
import os
from lib.ArgMem import PrintOptions
from lib.State import State


printOpt = PrintOptions()
try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:r:", ["img="])
except getopt.GetoptError:
    print("Invalid argument(s), use: \"main.py -h\" for usage specifications.")
    exit(1)
for opt, arg in opts:
    if opt == "-h":
        print("Possible options are:\n"
              "-h\t\tprint help message\n"
              "-p <format>\t\tprint transformed automata to stdout, possible formats:\n"
              "\thoa - .hoa standard format\n"
              "\tdot - .dot standard format\n"
              "\tcsa - custom format (used in Safra's construction)\n"
              "-r <FILE>\t\tprint run through automata on string from file\n"
              "--img <FILE>\t\tcreate schema of automaton (FILE.png) using dot command")
        exit(0)
    elif opt == "-p":
        if arg == "hoa":
            printOpt.hoa = True
        elif arg == "dot":
            printOpt.dot = True
        elif arg == "csa":
            printOpt.std = True
    elif opt == "-r":
        printOpt.run = True
        runFile = arg
    elif opt == "--img":
        printOpt.img = True
        output_file = arg
del opt
del arg
del opts
del args

file = open("new-s-15-r-1.00-f-0.10--1-of-100.ba-red.hoa", 'r')
string = file.read()
file.close()
del file
head, body = string.split('--BODY--')
del string
states = body.split('State')
states = states[1:]
states[-1] = re.sub('--END--', '', states[-1])
parsed = []
i = 0
for st in states:
    parsed.append([])
    st = st[5:]
    st = re.sub('.*?}\n', '', st)
    while st != '':
        st = re.sub('^.*?(?=\[)', '', st)
        if st[1] != '!':
            new_item = (int(st[1]), int(re.findall("[0-9]+(?=\n)", st[8:14])[0]))
            parsed[i].append(new_item)
            if st[5] != '!':
                new_item = (int(st[5]), int(re.findall("[0-9]+(?=\n)", st[8:14])[0]))
                parsed[i].append(new_item)
        elif st[6] != '!':
            new_item = (int(st[6]), int(re.findall("[0-9]+(?=\n)", st[8:14])[0]))
            parsed[i].append(new_item)
        st = re.sub('^\[.*] [0-9]+\n', '', st)
    i += 1
del i
del states
del new_item

all_states = [x for x in range(int(re.findall('(?<=States: )[0-9]+(?=\n)', head)[0]))]
# TODO detect acc
"""acc = re.findall('(?<=Inf\()[0-9]+(?=\))', head)
for i in range(acc.__len__()):
    acc[i] = int(acc[i])"""
tran = int(re.findall('(?<=AP: )[0-9]+', head)[0])
del body
del head

acc = 8
# Safra's construction
completed = []
safra_states = [State([0])]
for state in safra_states:
    if state in completed:
        continue
    possible_states = []
    i = 0
    while i < tran:
        new_state = state.transition(i, parsed, acc)
        new_state.horizontalMerge()
        new_state.verticalMerge()
        if new_state not in safra_states:
            safra_states.append(new_state)
        i += 1
print(safra_states)
