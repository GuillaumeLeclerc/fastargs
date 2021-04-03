import unittest
import io
from os import path
import sys
from unittest.mock import patch

from fastargs import Config, set_current_config, get_current_config, Section, Param
from fastargs.validation import (Anything, Str, Int, Float, And, Or, InRange,
                                 Module, ImportedObject)
from fastargs.exceptions import MissingValueError, ValidationError

sys.path.append(path.dirname(path.realpath(__file__)))

class TestValidation(unittest.TestCase):
    def setUp(self):
        set_current_config((Config()))

    def test_conversion(self):
        Section('sec').params(
            int=Param(Int(), 'test int'),
            fl=Param(Float(), 'test float'),
            int2=Param(Int(), 'test int')
        )

        cfg = get_current_config().collect({
            'sec.int': '69',
            'sec.int2': 4.20,
            'sec.fl': '4.20'
        })

        self.assertEqual(cfg['sec.int'], 69)
        self.assertEqual(cfg['sec.int2'], 4)
        self.assertEqual(cfg['sec.fl'], 4.20)

    def test_required(self):
        Section('sec').params(
            req=Param(Int(), 'required_param', required=True),
            noreq=Param(Int(), 'non required param', required=False),
        )

        cfg = get_current_config().collect({})

        errors = cfg.validate(mode='errordict')
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[('sec', 'req')], MissingValueError)
        self.assertIsNone(cfg['sec.noreq'])


    def test_default(self):
        Section('sec').params(
            noreq=Param(Int(), 'non required param', default=8, required=False)
        )

        cfg = get_current_config().collect({})

        errors = cfg.validate(mode='errordict')
        self.assertEqual(len(errors), 0)
        self.assertEqual(cfg['sec.noreq'], 8)

    def test_basic_types(self):
        Section('sec').params(
            i=Param(Int(), 'test int'),
            f=Param(Float(), 'test float'),
            s=Param(Str(), 'test string'),
            a=Param(Anything(), 'test anyting'),
            r=Param(InRange(0, 5), 'test inrange'),
            r2=Param(InRange(0, 5), 'test inrange2')
        )

        cfg = get_current_config().collect({
            'sec': {
                'i': 5,
                'f': 17.3,
                's': "hello",
                'a': (25, "hihi"),
                'r': 3,
                'r2': 2,
            }
        })

        self.assertEqual(len(cfg.validate(mode='errordict')), 0)

        cfg.collect({
            'sec': {
                'i': "blop",
                'f': "hoho",
                's': (2, 3),
                'a': (25, "hihi"),
                'r': 17,
                'r2': -1
            }
        })

        errors = cfg.validate(mode='errordict')

        for k in ['i', 'f', 's', 'r', 'r2']:
            self.assertIsInstance(errors[('sec', k)], ValidationError)

        self.assertNotIn(('sec', 'a'), errors)


    def test_and(self):
        Section('sec').params(
            p=Param(And(int, InRange(0, 20), InRange(10, 30))),
        )

        correct_values = [str(x) for x in range(10, 21)]
        incorrect_values = [str(x) for x in [-10, 5, 25]]

        for value in correct_values:
            cfg = get_current_config().collect({
                'sec.p': value
            })
            self.assertEqual(len(cfg.validate(mode='errordict')), 0)

        for value in incorrect_values:
            cfg = get_current_config().collect({
                'sec.p': value
            })
            self.assertIsInstance(cfg.validate(mode='errordict')[('sec', 'p')],
                                  ValidationError)


    def test_and_or(self):
        Section('sec').params(
            p=Param(And(int, Or(InRange(0, 10), InRange(20, 30)))),
        )

        correct_values = [str(x) for x in range(0, 11)]
        correct_values += [str(x) for x in range(20, 31)]
        incorrect_values = [str(x) for x in [-10, 15, 35]]

        for value in correct_values:
            cfg = get_current_config().collect({
                'sec.p': value
            })
            self.assertEqual(len(cfg.validate(mode='errordict')), 0)

        for value in incorrect_values:
            cfg = get_current_config().collect({
                'sec.p': value
            })
            self.assertIsInstance(cfg.validate(mode='errordict')[('sec', 'p')],
                                  ValidationError)
        pass

    def test_bad_default(self):
        Section('sec').params(
            bad_param=Param(int, default="Hello")
        )

        errors = get_current_config().validate(mode='errordict')
        self.assertIsInstance(errors[('sec', 'bad_param')], ValidationError)

    def test_bad_checker(self):
        self.assertRaises(TypeError, Param, (Param,), {'default': "hello"})


    def test_help(self):

        self.assertEqual(str(Param(int)), 'an int')
        self.assertEqual(str(Param(float)), 'a float')
        self.assertEqual(str(Param(str)), 'a string')
        self.assertEqual(str(Param(Anything())), 'anything')
        self.assertEqual(str(Param(InRange(15, 17))), 'between 15 and 17')
        self.assertEqual(str(Param(Or(InRange(2, 3),InRange(15, 17)))),
                         'between 2 and 3 or between 15 and 17')
        self.assertEqual(str(Param(And(InRange(2, 3),InRange(15, 17)))),
                         'between 2 and 3 and between 15 and 17')

    def test_exit(self):
        Section('sec').params(
            req=Param(Int(), 'required_param', required=True),
            noreq=Param(Int(), 'non required param', required=False),
        )

        cfg = get_current_config().collect({})

        data = {'called': False}

        def fake_exit():
            data['called'] = True

        fakeio = io.StringIO("")

        with patch('sys.exit', fake_exit):
            with patch('sys.stderr', fakeio):
                cfg.validate()

        printed_data = fakeio.getvalue()

        self.assertIn('sec.req', printed_data)
        self.assertNotIn('sec.noreq', printed_data)
        self.assertTrue(data['called'])

    def test_no_exit(self):
        Section('sec').params(
            req=Param(Int(), 'required_param', required=True),
            noreq=Param(Int(), 'non required param', required=False),
        )

        cfg = get_current_config().collect({'sec.req': 15})

        data = {'called': False}

        def fake_exit():
            data['called'] = True

        fakeio = io.StringIO("")

        with patch('sys.exit', fake_exit):
            with patch('sys.stderr', fakeio):
                cfg.validate()

        printed_data = fakeio.getvalue()

        self.assertEqual(len(printed_data), 0)
        self.assertFalse(data['called'])

    def test_module(self):
        Section('module.import').params(
            module=Param(Module(), required=True)
        )

        cfg = get_current_config().collect({
            'module.import.module': 'test_module.file1'
        })

        loaded_module = cfg['module.import.module']

        self.assertEqual(loaded_module.testme(), 42)
        sys.modules.pop('test_module.file1')


    def test_params_in_imported_module(self):
        Section('module.import').params(
            module=Param(Module(), required=True)
        )

        cfg = get_current_config().collect({
            'module.import.module': 'test_module.with_params',
            'imported_section.blah.p1': 42.5
        })

        self.assertEqual(cfg['imported_section.blah.p1'], 42.5)
        sys.modules.pop('test_module.with_params')

    def test_imported_object(self):
        Section('module.import').params(
            obj=Param(ImportedObject(), required=True)
        )

        cfg = get_current_config().collect({
            'module.import.obj': 'test_module.file1.testme'
        })

        loaded_function = cfg['module.import.obj']

        self.assertEqual(loaded_function(), 42)
        sys.modules.pop('test_module.file1')






if __name__ == '__main__':
    unittest.main()
