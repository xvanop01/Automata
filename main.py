import re
import getopt
import sys
import os

print_std = False
print_dot = False
print_hoa = False
print_img = False
try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:", ["img="])
except getopt.GetoptError:
    print("Invalid argument(s), use: \"main.py -h\" for usage specifications.")
    exit(1)
for opt, arg in opts:
    if opt == "-h":
        print("Possible options are:\n"
              "-h\t\tprints help message\n"
              "-p <format>\t\tprints transformed automata to stdout, possible formats:\n"
              "\thoa - .hoa standard format\n"
              "\tdot - .dot standard format\n"
              "\tcsa - custom format (used in Safra's construction)\n"
              "--img <FILE>\t\tcreates schema of automaton (FILE.png) using dot command")
        exit(0)
    elif opt == "-p":
        if arg == "hoa":
            print_hoa = True
        elif arg == "dot":
            print_dot = True
        elif arg == "csa":
            print_std = True
    elif opt == "--img":
        print_img = True
        output_file = arg

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

acc = 8
# Safra's construction
completed = []
safra_states = [([0], [])]
transitions = []
loop_states = []
for state in safra_states:
    if state in completed:
        continue
    if state == ['fail']:
        transitions.append((state, 0, ['fail']))
        transitions.append((state, 1, ['fail']))
        continue
    new_state = ([], [])
    app_loop = False

    # 0 transit
    for item in state[0]:
        for tran in parsed[item]:
            if tran[0] == 0 and tran[1] not in new_state[0]:
                if item in state[1]:
                    new_state[1].append(tran[1])
                    if tran[1] == acc:
                        app_loop = True
                new_state[0].append(tran[1])
                if tran[1] == acc and acc not in new_state[1]:  # acceptance
                    new_state[1].append(acc)
    new_state[0].sort()
    new_state[1].sort()
    if new_state[0] == new_state[1]:
        new_state = (new_state[0], ['success'])
    if not new_state[0]:
        new_state = ['fail']
    if new_state not in safra_states:
        safra_states.append(new_state)
    if new_state not in loop_states and app_loop:
        loop_states.append(new_state)
    if (state, 0, new_state) not in transitions:
        transitions.append((state, 0, new_state))

    # 1 transit
    new_state = ([], [])
    app_loop = False
    for item in state[0]:
        for tran in parsed[item]:
            if tran[0] == 1 and tran[1] not in new_state[0]:
                if item in state[1]:
                    new_state[1].append(tran[1])
                    if tran[1] == acc:
                        app_loop = True
                new_state[0].append(tran[1])
                if tran[1] == acc and acc not in new_state[1]:  # acceptance
                    new_state[1].append(acc)
    new_state[0].sort()
    new_state[1].sort()
    if new_state[0] == new_state[1]:
        new_state = (new_state[0], ['success'])
    if not new_state[0]:
        new_state = ['fail']
    if new_state not in safra_states:
        safra_states.append(new_state)
    if new_state not in loop_states and app_loop:
        loop_states.append(new_state)
    if (state, 1, new_state) not in transitions:
        transitions.append((state, 1, new_state))
    completed.append(state)

if print_dot or print_img:
    print_str = ""
    string_acc = ""
    string_normal = ""
    for state in safra_states:
        if state != ['fail']:
            if state[1] == ['success']:
                string_acc = string_acc + "\t\t" + str(safra_states.index(state)) + " [label = \"" + str(state) + \
                             "\"]\n"
            else:
                string_normal = string_normal + "\t\t" + str(safra_states.index(state)) +\
                                " [label = \"" + str(state) + "\"]\n"
        else:
            string_normal = string_normal + "\t\t" + str(safra_states.index(state)) + " [label = \"" + str(state) + \
                            "\"]\n"
        i += 1
    if string_acc != "":
        string_acc = string_acc[0:-1] + ";\n"
    if string_normal != "":
        string_normal = string_normal[0:-1] + ";\n"

    print_str = "digraph automaton {\n\tnode [shape = doublecircle]\n" + string_acc + \
                "\tnode [shape = circle]\n" + string_normal
    for tran in transitions:
        print_str += "\t" + str(safra_states.index(tran[0])) + " -> " + str(safra_states.index(tran[2])) + \
                     " [ label = \"" + str(tran[1]) + "\" ];\n"
    print_str += "}"
    if print_img:
        file = open(output_file + ".dot", "w")
        file.write(print_str)
        file.close()
        os.system("dot -Tpng " + output_file + ".dot -o " + output_file + ".png")
    if print_dot:
        print(print_str)

if print_std:
    for state in safra_states:
        print(str(state) + ':')
        for tran in transitions:
            if tran[0] == state:
                print('\t' + str(tran))

if print_hoa:
    print_str = "HOA: v1\nStates: " + str(len(safra_states) + 1) + "\n" + "Start: 0\nacc-name: Buchi\nAcceptance: "
    i = 0
    for item in safra_states:
        if item != ['fail']:
            if item[1] == ['success'] or (8 in item[1] and len(item[1]) != 1):
                i += 1
    print_str += "1" + " Inf(0)"
    """j = 1
    while j < i:
        print_str += " & Inf(" + str(j) + ")"
        j += 1"""
    print_str += "\nproperties: explicit-labels state-acc trans-labels\nAP: 2 \"a0\" \"a1\"\n--BODY--\n"
    j = 0
    i = 0
    for item in safra_states:
        print_str += "State: " + str(i)
        if item != ['fail']:
            if item[1] == ['success'] or item in loop_states:
                print_str += " { " + "0" + " }"
                j += 1
        print_str += "\n\t[0 & !1] " + str(safra_states.index(transitions[i * 2][2])) + "\n\t[!0 & 1] " \
                     + str(safra_states.index(transitions[i * 2 + 1][2])) + "\n\t[!0&!1 | 0&1] " \
                     + str(len(safra_states)) + "\n"
        i += 1
    print_str += "State: " + str(len(safra_states)) + "\n\t[t] " + str(len(safra_states)) + "\n"
    print_str += "--END--"
    print(print_str)
