import re
import getopt
import sys
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
transitions = []
for state in safra_states:
    if state in completed:
        continue
    i = 1
    while i >= 0:
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
            transitions.append((state, new_state, (merged - 2) * 2 + 2))  # (ef - 3) * 2 + 2))
        elif missing != n:
            transitions.append((state, new_state, (missing - 2) * 2 + 1))  # (ef - 2) * 2 + 1))
        else:
            transitions.append((state, new_state, None))
        i -= 1

print_str = "HOA: v1\nStates: " + str(len(safra_states)) + "\n" + "Start: 0\nacc-name: parity min even 7\n" \
                                                                  "Acceptance: "
print_str += "7" + " Inf(0) | (Fin(1) & (Inf(2) | (Fin(3) & (Inf(4) | (Fin(5) & Inf(6))))))"
print_str += "\nproperties: explicit-labels trans-labels\nAP: 2 \"a0\" \"a1\"\n--BODY--\n"
i = 0
for item in safra_states:
    print_str += "State: " + str(i)
    print_str += "\n\t[!0 & 1] " + str(safra_states.index(transitions[i * 2][1]))
    if transitions[i * 2][2] is not None:
        print_str += " { " + str(transitions[i * 2][2]) + " }"
    print_str += "\n\t[0 & !1] " + str(safra_states.index(transitions[i * 2 + 1][1]))
    if transitions[i * 2 + 1][2] is not None:
        print_str += " { " + str(transitions[i * 2 + 1][2]) + " }"
    print_str += "\n\t[!0&!1 | 0&1] " + str(safra_states.index(State([]))) + "\n"
    i += 1
print_str += "--END--"
print(print_str)
