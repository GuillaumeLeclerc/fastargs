import unittest

from fastargs import Config, set_current_config, get_current_config, Section, Param
from fastargs.validation import Anything, Str, Int, Float, And, Or, InRange
from fastargs.decorators import param, section

class TestDecorators(unittest.TestCase):
    def setUp(self):
        set_current_config((Config()))

    def test_read_value(self):
        Section('sec1.sec').params(
            p1=Param(int),
            p2=Param(float)
        )

        @param('sec1.sec.p1')
        @param('sec1.sec.p2')
        def compute(p1, p2):
            return p1 + p2

        get_current_config().collect({
            'sec1.sec': {
                'p1': 1,
                'p2': 3
            }
        })

        self.assertEqual(compute(), 4)


    def test_default_in_config(self):
        Section('sec1.sec').params(
            p1=Param(int, default=1),
            p2=Param(float, default=3.0)
        )

        @param('sec1.sec.p1')
        @param('sec1.sec.p2')
        def compute(p1, p2):
            return p1 + p2

        self.assertEqual(compute(), 4)

    def test_default_in_func(self):
        Section('sec1.sec').params(
            p1=Param(int),
            p2=Param(float)
        )

        @param('sec1.sec.p1')
        @param('sec1.sec.p2')
        def compute(p1=1, p2=3.0):
            return p1 + p2

        self.assertEqual(compute(), 4)

    def test_section(self):
        Section('sec1.sec').params(
            p1=Param(int),
            p2=Param(float)
        )

        @section('sec1.sec')
        @param('p1')
        @param('p2')
        def compute(p1=1, p2=3.0):
            return p1 + p2

        self.assertEqual(compute(), 4)

    def test_multiple_sections(self):
        Section('sec2.sec').params(
            p1=Param(int),
            p2=Param(float)
        )

        @section('sec2.sec')
        @param('p1')
        @section('sec2')
        @param('sec.p2')
        def compute(p1=1, p2=3.0):
            return p1 + p2

        self.assertEqual(compute(), 4)

    def test_overriding(self):
        Section('sec1.sec').params(
            p1=Param(int),
            p2=Param(float)
        )

        @param('sec1.sec.p1')
        @param('sec1.sec.p2')
        def compute(p1, p2):
            return p1 + p2

        get_current_config().collect({
            'sec1.sec': {
                'p1': 1,
                'p2': 3
            }
        })

        self.assertEqual(compute(p2=7), 8)


if __name__ == '__main__':
    unittest.main()
