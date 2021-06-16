class State:
    def __init__(self, items):
        self.possible_states = []
        self.substates = []
        self.node = 1
        for i in items:
            self.possible_states.append(i)
        self.possible_states.sort()

    def __eq__(self, other):
        if isinstance(other, State):
            if other.possible_states == self.possible_states:
                if self.substates == other.substates:
                    return True
                for item in self.substates:
                    if item not in other.substates:
                        return False
                for item in other.substates:
                    if item not in self.substates:
                        return False
                return True
        return False

    def empty(self):
        if not self.possible_states:
            return True
        else:
            return False

    def addSubstate(self, number_list):
        if isinstance(number_list, list):
            for st in self.substates:
                to_remove = []
                for number in number_list:
                    if number in st.possible_states:
                        to_remove.append(number)
                for number in to_remove:
                    number_list.remove(number)
                if not number_list:
                    return
            for number in number_list:
                if number not in self.possible_states:
                    self.possible_states.append(number)
            self.possible_states.sort()
            self.substates.append(State(number_list))
        elif isinstance(number_list, int):
            self.addSubstate([number_list])
        else:
            raise TypeError

    def transition(self, label, transitions, acc):
        substates = []
        for substate in self.substates:
            if isinstance(substate, State):
                substates.append(substate.transition(label, transitions, acc))
            else:
                raise TypeError
        new_possible_states = []
        for st in self.possible_states:
            for trans in transitions[st]:
                if trans[0] == label and trans[1] not in new_possible_states:
                    new_possible_states.append(trans[1])
        new_state = State(new_possible_states)
        for item in substates:
            new_state.substates.append(item)
        for number in new_state.possible_states:
            if number == acc:
                new_state.addSubstate([number])
        return new_state

    def horizontalMerge(self):
        all_substate_number = []
        for substate in self.substates:
            if isinstance(substate, State):
                i = 0
                while i < len(substate.possible_states):
                    if substate.possible_states[i] in all_substate_number:
                        del substate.possible_states[i]
                    else:
                        all_substate_number.append(substate.possible_states[i])
                        i += 1
                substate.horizontalMerge()
            else:
                raise TypeError

    def verticalMerge(self):
        merged = -1
        reached_acc = []
        for substate in self.substates:
            if isinstance(substate, State):
                for number in substate.possible_states:
                    if number not in reached_acc:
                        reached_acc.append(number)
            else:
                raise TypeError
        reached_acc.sort()
        if reached_acc == self.possible_states:
            self.substates = []
            if self.possible_states:
                return self.node
            else:
                return -1
        else:
            i = 0
            while i < len(self.substates):
                if len(self.substates[i].possible_states) == 0:
                    del self.substates[i]
                else:
                    i += 1
            for substate in self.substates:
                returned_value = substate.verticalMerge()
                if returned_value != -1 and (merged == -1 or merged > returned_value):
                    merged = returned_value
            return merged

    def getNumberOfStates(self):
        n = 1
        for state in self.substates:
            n += state.getNumberOfStates()
        return n

    def setNode(self, number):
        self.node = number

    def setChildren(self, number, layer):
        todo = [self.substates]
        i = 0
        while layer > 1:
            todo.append([])
            for state in todo[i]:
                for subst in state.substates:
                    todo[i+1].append(subst)
            i += 1
            layer -= 1
            if not todo[i]:
                return number
        for state in todo[i]:
            state.setNode(number)
            number += 1
        return number

    def getMissing(self, number, layer):
        todo = [self.substates]
        i = 0
        while layer > 1:
            todo.append([])
            for state in todo[i]:
                for subst in state.substates:
                    todo[i + 1].append(subst)
            i += 1
            layer -= 1
            if not todo[i]:
                return number
        for state in todo[i]:
            if number < state.node:
                return number
            elif not state.possible_states:
                return state.node
            else:
                number += 1
        return number
