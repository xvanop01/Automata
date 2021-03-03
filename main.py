import re

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
    print(final)
    i += 1
