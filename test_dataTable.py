import unittest
from dataTable import DataTable, nrow, ncol, list_reduce


class TestDataTable(unittest.TestCase):
    def test_nrow(self):
        testTable = DataTable(
            [
                [0, 0.0, "test1"],
                [-1, -1.0, "test2"],
                [1, 1.0, "test3"],
                [-10, -10.0, "test4"],
                [10, 10.0, "test5"]
            ],
            columns=['ints', 'floats', 'strings'])
        self.assertEquals(nrow(testTable), 5)

    def test_ncol(self):
        testTable = DataTable(
            [
                [0, 0.0, "test1"],
                [-1, -1.0, "test2"],
                [1, 1.0, "test3"],
                [-10, -10.0, "test4"],
                [10, 10.0, "test5"]
            ],
            columns=['ints', 'floats', 'strings'])
        self.assertEquals(ncol(testTable), 3)

    def test_list_reduce(self):
        # Create data to test
        testListOfLists = [
            [0, 0.0, "test1"],
            [-1, -1.0, "test2"],
            [1, 1.0, "test3"],
            [-10, -10.0, "test4"],
            [10, 10.0, "test5"]
        ]
        testTable = DataTable(testListOfLists, columns=['ints', 'floats', 'strings'])

        # List tests
        self.assertEquals(list_reduce(4), 4)
        self.assertEquals(list_reduce([4]), 4)
        self.assertEquals(list_reduce([[4]]), 4)
        self.assertEquals(list_reduce([[4, 5]]), [4, 5])
        self.assertEquals(list_reduce([[4], [5]]), [4, 5])

        # Test DataTables
        self.assertEquals(list_reduce(testListOfLists), list_reduce(testTable))
        self.assertEquals(list_reduce(testTable['ints']),
                          list_reduce([value[0] for value in testListOfLists]))
        self.assertEquals(list_reduce(testTable['ints']),
                          list_reduce([[value[0] for value in testListOfLists]]))
        self.assertEquals(list_reduce(testTable[1]), list_reduce(testListOfLists[0]))
        self.assertEquals(list_reduce(testTable[1]), list_reduce([testListOfLists[0]]))

    def test_getitem(self):
        # Create data to test
        testTable = DataTable([
            [0, 0.0, "test1"],
            [-1, -1.0, "test2"],
            [1, 1.0, "test3"],
            [-10, -10.0, "test4"],
            [10, 10.0, "test5"]
        ], columns=['ints', 'floats', 'strings'])

        # Tests against self
        self.assertTrue(testTable == testTable)
        self.assertTrue(testTable[1] == testTable[1])
        self.assertTrue(testTable['strings'] == testTable['strings'])
        self.assertTrue(testTable['strings'][1] == testTable[1]['strings'])

if __name__ == '__main__':
    unittest.main(verbosity=10)
