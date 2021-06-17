import unittest
from lib.State import State


class StatesTests(unittest.TestCase):
    def setUp(self):
        pass


class TestEq(StatesTests):
    def testEq(self):
        state1 = State([1, 2, 4, 7])
        state2 = State([1, 3, 5, 8])
        self.assertNotEqual(state1, state2)
        state3 = State([1, 2, 4, 7])
        self.assertEqual(state1, state3)

    def testEqUnordered(self):
        state1 = State([1, 2, 3])
        state2 = State([2, 1, 3])
        self.assertEqual(state1, state2)

    def testSubstates(self):
        state1 = State([1, 2, 3])
        subState1a = State([1, 2])
        subState1b = State([3])
        state1.substates.append(subState1a)
        state1.substates.append(subState1b)
        state2 = State([3, 2, 1])
        self.assertNotEqual(state1, state2)
        subState2a = State([2, 1])
        subState2b = State([3])
        state2.substates.append(subState2b)
        state2.substates.append(subState2a)
        self.assertEqual(state1, state2)
        state3 = State([1, 2, 3])
        subState3a = State([1, 3])
        subState3b = State([2])
        state3.substates.append(subState3a)
        state3.substates.append(subState3b)
        self.assertNotEqual(state1, state3)

    def testThirdLayerEq(self):
        state1 = State([1, 2, 3])
        subState1a = State([1, 2])
        subState1b = State([3])
        subState1aa = State([1])
        subState1ab = State([2])
        subState1a.substates.append(subState1ab)
        subState1a.substates.append(subState1aa)
        state1.substates.append(subState1a)
        state1.substates.append(subState1b)
        state2 = State([3, 2, 1])
        subState2a = State([2, 1])
        subState2b = State([3])
        subState2aa = State([1])
        subState2ab = State([2])
        subState2a.substates.append(subState2aa)
        subState2a.substates.append(subState2ab)
        state2.substates.append(subState2b)
        state2.substates.append(subState2a)
        self.assertEqual(state1, state2)
        state3 = State([1, 2, 3])
        subState3a = State([1, 2])
        subState3b = State([3])
        state3.substates.append(subState3a)
        state3.substates.append(subState3b)
        self.assertNotEqual(state1, state3)


class TestIn(StatesTests):
    def testInOneLayer(self):
        state1 = State([0, 1])
        state2 = State([1])
        state3 = State([1, 2])
        states = [state1, state2]
        self.assertTrue(State([0, 1]) in states)
        self.assertTrue(state2 in states)
        self.assertFalse(state3 in states)

    def testInMoreLayers(self):
        state1 = State([0, 1, 2])
        state1.substates.append(State([1]))
        state1.substates.append(State([0]))
        states = [State([0, 1]), state1]
        self.assertTrue(State([1]) in state1.substates)
        self.assertFalse(State([1]) in states)
        state2 = State([0, 1])
        state2.substates.append(State([0]))
        self.assertFalse(state2 in states)


class TestAddSubstate(StatesTests):
    def testAddSubstateAlreadyIn(self):
        state1 = State([0, 1, 2, 3])
        state1.substates.append(State([0]))
        state1.substates.append(State([1, 2]))
        state1.addSubstate([1, 2, 3])
        self.assertEqual(len(state1.substates), 3)
        self.assertEqual(len(state1.substates[2].possible_states), 1)


class TestTransitions(StatesTests):
    def testSimpleTransition(self):
        state = State([0, 1, 2, 3])
        transitions = [[(0, 2)], [(1, 1), (1, 2), (0, 4)], [], [(0, 0)], [(0, 3)]]
        state_expected = State([2, 4, 0])
        self.assertEqual(state_expected, state.transition(0, transitions, None))
        state.addSubstate([0, 2])
        state.addSubstate([1])
        state_expected.addSubstate([2])
        state_expected.addSubstate([4])
        self.assertEqual(state_expected, state.transition(0, transitions, None))


class TestMerge(StatesTests):
    def testHorizontal(self):
        state = State([0, 1, 2, 3, 4])
        state.addSubstate([0, 1, 2])
        state.addSubstate([1, 2, 3, 4])
        state.addSubstate([0, 4])
        state_expected = State([0, 1, 2, 3, 4])
        state_expected.addSubstate([0, 1, 2])
        state_expected.addSubstate([3, 4])
        state.horizontalMerge()
        self.assertEqual(state, state_expected)

    def testVertical(self):
        state = State([0, 1, 2, 3, 4])
        state.addSubstate([0, 1, 2])
        state.substates[0].addSubstate([0, 1])
        self.assertFalse(state.verticalMerge())
        state_expected = State([0, 1, 2, 3, 4])
        state_expected.addSubstate([0, 1, 2])
        state_expected.substates[0].addSubstate([0, 1])
        self.assertEqual(state, state_expected)
        state.substates[0].addSubstate([2])
        self.assertTrue(state.verticalMerge())
        del state_expected.substates[0].substates[0]
        self.assertEqual(state, state_expected)
        state.addSubstate([3, 4])
        self.assertTrue(state.verticalMerge())
        del state_expected.substates[0]
        self.assertEqual(state, state_expected)


if __name__ == '__main__':
    unittest.main()
