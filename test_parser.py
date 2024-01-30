from unittest import TestCase

import parser


def readTestFile():
    with (open("test-data/test1.xml", 'r') as f):
        lines = f.readlines()
        res = ""
        for line in lines:
            res = res+line
        return res


class Test(TestCase):
    # test that we can parse the whole test file without error
    def test_parse_student(self):
        allXml = readTestFile()
        data = parser.process_data(allXml)
