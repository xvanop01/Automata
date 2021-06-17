import re
import getopt
import sys
import os
from lib.ArgMem import PrintOptions
from lib.State import State

printOpt = PrintOptions()
output_file = "output"
opts = []
filename = None
try:
    opts, args = getopt.getopt(sys.argv[1:], "hp:r:f:", ["img="])
except getopt.GetoptError:
    print("Invalid argument(s), use: \"main.py -h\" for usage specifications.")
    exit(1)
for opt, arg in opts:
    if opt == "-h":
        print("Possible options are:\n"
              "-h\t\tprint help message\n"
              "-f <FILE>\t\tdefine file containing automata\n"
              "-p <format>\t\tprint transformed automata to stdout, possible formats:\n"
              "\thoa - .hoa standard format\n"
              "\tdot - .dot standard format\n"
              "--img <FILE>\t\tcreate schema of automaton (FILE.png) using dot command")
        exit(0)
    elif opt == "-p":
        if arg == "hoa":
            printOpt.hoa = True
        elif arg == "dot":
            printOpt.dot = True
    elif opt == "-f":
        filename = arg
    elif opt == "--img":
        printOpt.img = True
        output_file = arg

if not filename:
    print("Missing automata file, use -f parameter!")
    exit(1)
file = open(filename, 'r')
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
acc = re.findall('(?<=State: )[0-9]+(?= {[ ]*[0-9]+[ ]*}\n)', body)
for i in range(acc.__len__()):
    acc[i] = int(acc[i])
possible_tran = int(re.findall('(?<=AP: )[0-9]+', head)[0])
del body
del head

# Safra's construction
completed = []
safra_states = [State([0])]
transitions = []
max_inf = 0
for state in safra_states:
    if state in completed:
        continue
    i = 0
    while i < possible_tran:
        new_state = state.transition(i, parsed, acc)
        new_state.setNode(1)
        n = 2
        ex_n = 1
        layer = 1
        while ex_n != n:
            ex_n = n
            n = new_state.setChildren(n, layer)
            layer += 1
        n = new_state.getNumberOfStates() + 1

        new_state.horizontalMerge()
        merged = new_state.verticalMerge()

        layer = 1
        ex_missing = 0
        missing = 2
        while ex_missing != missing:
            ex_missing = missing
            missing = new_state.getMissing(missing, layer)
            layer += 1
        if new_state not in safra_states:
            safra_states.append(new_state)

        if not new_state.possible_states:
            transitions.append((state, new_state, None))
        elif n > missing and merged == 1 and not new_state.substates:
            transitions.append((state, new_state, 0))
        elif n > merged > 0:
            inf = (merged - 2) * 2 + 2
            transitions.append((state, new_state, inf))
            if max_inf < inf:
                max_inf = inf
        elif missing != n:
            transitions.append((state, new_state, (missing - 2) * 2 + 1))
        else:
            transitions.append((state, new_state, None))
        i += 1

if printOpt.hoa:
    print_str = "HOA: v1\nStates: " + str(len(safra_states)) + "\n" + "Start: 0\nacc-name: parity min even 7\n" \
                                                                      "Acceptance: "
    i = 2
    string_start = " Inf(0)"
    string_end = ""
    while i < max_inf:
        string_start += " | (Fin(" + str(i - 1) + ") & (Inf(" + str(i) + ")"
        string_end += "))"
        i += 2
    string_start += " | (Fin(" + str(i - 1) + ") & Inf(" + str(i) + "))"
    print_str += str(max_inf + 1) + string_start + string_end
    print_str += "\nproperties: explicit-labels trans-labels\nAP: 2 \"a0\" \"a1\"\n--BODY--\n"
    i = 0
    for item in safra_states:
        print_str += "State: " + str(i)
        print_str += "\n\t[0 & !1] " + str(safra_states.index(transitions[i * 2][1]))
        if transitions[i * 2][2] is not None and transitions[i * 2][2] <= max_inf:
            print_str += " { " + str(transitions[i * 2][2]) + " }"
        print_str += "\n\t[!0 & 1] " + str(safra_states.index(transitions[i * 2 + 1][1]))
        if transitions[i * 2 + 1][2] is not None and transitions[i * 2 + 1][2] <= max_inf:
            print_str += " { " + str(transitions[i * 2 + 1][2]) + " }"
        print_str += "\n\t[!0&!1 | 0&1] " + str(safra_states.index(State([]))) + "\n"
        i += 1
    print_str += "--END--"
    print(print_str)

if printOpt.dot or printOpt.img:
    string_normal = ""
    for state in safra_states:
        string_normal = string_normal + "\t\t" + str(safra_states.index(state)) + " [label = \"" + str(state) + \
                            "\"]\n"
    string_normal = string_normal[0:-1] + ";\n"
    print_str = "digraph automaton {\n\tnode [shape = circle]\n" + string_normal
    i = 0
    for tran in transitions:
        if tran[2]:
            print_str += "\t" + str(safra_states.index(tran[0])) + " -> " + str(safra_states.index(tran[1])) + \
                         " [ label = \"" + str(i) + " (" + str(tran[2]) + ")\" ];\n"
        else:
            print_str += "\t" + str(safra_states.index(tran[0])) + " -> " + str(safra_states.index(tran[1])) + \
                         " [ label = \"" + str(i) + "\" ];\n"
        i += 1
        if i == possible_tran:
            i = 0
    print_str += "}"
    if printOpt.img:
        file = open(output_file + ".dot", "w")
        file.write(print_str)
        file.close()
        os.system("dot -Tpng " + output_file + ".dot -o " + output_file + ".png")
    if printOpt.dot:
        print(print_str)
