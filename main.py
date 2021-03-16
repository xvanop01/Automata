import re
import getopt
import sys
import os

output_file = "output"
print_std = False
dot_print = False
try:
    opts, args = getopt.getopt(sys.argv[1:], "ho:p", ["img"])
except getopt.GetoptError:
    print("main.py [-o <output>]\n")
    exit(1)
for opt, arg in opts:
    if opt == "-h":
        print("Possible options are:\n"
              "-h\t\tprints help message\n"
              "-o <output>\tspecifies name of output file\n"
              "-p\t\tprints transformed automata to stdout (custom format)\n"
              "--img\t\tcreates schema of automaton (.png) using dot command")
        exit(0)
    elif opt == "-o":
        output_file = arg
    elif opt == "-p":
        print_std = True
    elif opt == "--img":
        dot_print = True

file = open("new-s-15-r-1.00-f-0.10--1-of-100.ba-red.hoa", 'r')
string = file.read()
file.close()
head, body = string.split('--BODY--')
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

all_states = [x for x in range(int(re.findall('(?<=States: )[0-9]+(?=\n)', head)[0]))]
reach_acc = [[] for x in range(int(re.findall('(?<=States: )[0-9]+(?=\n)', head)[0]))]
acc = re.findall('(?<=Inf\()[0-9]+(?=\))', head)
for i in range(acc.__len__()):
    acc[i] = int(acc[i])

# DAG run
visited = []
set_of_states = [[[0]]]
all_states.remove(0)
i = 0
finished = 0
while finished == 0:
    new_set = []
    finished = 1
    for x in set_of_states[i]:
        if x == "acc":
            new_set.append(x)
            continue
        for y in x:
            if y == "acc":
                new_set.append(y)
                continue
            work_set = parsed[y][0::1]
            for j in range(work_set.__len__()):
                work_set[j] = work_set[j][1]
                if work_set[j] in acc:
                    work_set[j] = "acc"
            new_set.append(work_set)
    final = []
    for x in new_set[:]:
        if x in final:
            continue
        else:
            if x in visited:
                final.append(x)
                continue
            finished = 0
            final.append(x)
            visited.append(x)
    set_of_states.append(final)
    # print(final)
    i += 1

# Safra's construction
completed = []
safra_states = [([0], [])]
transitions = []
for state in safra_states:
    if state in completed or state == ['fail']:
        continue
    new_state = ([], [])
    # 0 transit
    for item in state[0]:
        for tran in parsed[item]:
            if tran[0] == 0 and tran[1] not in new_state[0]:
                if item in state[1]:
                   new_state[1].append(tran[1])
                new_state[0].append(tran[1])
                if tran[1] == 0 and 0 not in new_state[1]:
                    new_state[1].append(0)
    new_state[0].sort()
    new_state[1].sort()
    if new_state[0] == new_state[1]:
        new_state = (new_state[0], ['success'])
    if not new_state[0]:
        new_state = ['fail']
    if new_state not in safra_states:
        safra_states.append(new_state)
    if (state, 0, new_state) not in transitions:
        transitions.append((state, 0, new_state))
    # 1 transit
    new_state = ([], [])
    for item in state[0]:
        for tran in parsed[item]:
            if tran[0] == 1 and tran[1] not in new_state[0]:
                if item in state[1]:
                   new_state[1].append(tran[1])
                new_state[0].append(tran[1])
                if tran[1] == 0 and 0 not in new_state[1]:
                    new_state[1].append(0)
    new_state[0].sort()
    new_state[1].sort()
    if new_state[0] == new_state[1]:
        new_state = (new_state[0], ['success'])
    if not new_state[0]:
        new_state = ['fail']
    if new_state not in safra_states:
        safra_states.append(new_state)
    if (state, 1, new_state) not in transitions:
        transitions.append((state, 1, new_state))
    completed.append(state)

string_acc = ""
string_normal = ""
for state in safra_states:
    if state != ['fail']:
        if state[1] == ['success']:
            string_acc = string_acc + "\t\t" + str(safra_states.index(state)) + " [label = \"" + str(state) + "\"]\n"
        else:
            string_normal = string_normal + "\t\t" + str(safra_states.index(state)) +\
                            " [label = \"" + str(state) + "\"]\n "
    else:
        string_normal = string_normal + "\t\t" + str(safra_states.index(state)) + " [label = \"" + str(state) + "\"]\n"
    if print_std:
        print(str(state) + ':')
        for tran in transitions:
            if tran[0] == state:
                print('\t' + str(tran))
    i += 1
if string_acc != "":
    string_acc = string_acc[0:-1] + ";\n"
if string_normal != "":
    string_normal = string_normal[0:-1] + ";\n"

file = open(output_file + ".dot", "w")
file.write("digraph automaton {\n\tnode [shape = doublecircle]\n" + string_acc +
           "\tnode [shape = circle]\n" + string_normal)
for tran in transitions:
    file.write("\t" + str(safra_states.index(tran[0])) + " -> " + str(safra_states.index(tran[2])) +
               " [ label = \"" + str(tran[1]) + "\" ];\n")
file.write("}\n")
file.close()
if dot_print:
    os.system("dot -Tpng " + output_file + ".dot -o " + output_file + ".png")
