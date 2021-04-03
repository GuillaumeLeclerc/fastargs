import argparse
import unittest
from unittest.mock import patch
import tempfile
import sys
from os import path
import json
import os

import yaml

from fastargs import (Config, set_current_config, get_current_config, Section,
                      Param)
from fastargs.validation import (Anything, Str, Int, Float, And, Or, InRange,
                                 Module)
from fastargs.exceptions import MissingValueError, ValidationError

sys.path.append(path.dirname(path.realpath(__file__)))

class TestSources(unittest.TestCase):
    def setUp(self):
        set_current_config((Config()))

    def test_env_vars(self):
        Section('envtest').params(
            v1=Param(int)
        )

        os.environ['envtest.v1'] = "17"
        cfg = get_current_config()
        #
        # This is not defined before you collect
        self.assertIsNone(cfg['envtest.v1'])
        cfg.collect_env_variables()
        self.assertEqual(cfg['envtest.v1'], 17)
        os.environ['envtest.v1'] = "18"
        #
        # It doesn't change if you don't collect
        self.assertEqual(cfg['envtest.v1'], 17)
        cfg.collect_env_variables()
        self.assertEqual(cfg['envtest.v1'], 18)

    def test_json(self, assume_known=True):
        Section('test.json').params(
            p1=Param(float),
            p2=Param(float)
        )

        cfg = get_current_config()

        tfolder = tempfile.TemporaryDirectory()
        with tfolder as tmp:
            path = os.path.join(tmp, 'something')
            content = {
                'test': {'json': {'p1': 17}},
                'test.json.p2': 11
            }
            with open(path, 'w') as handle:
                json.dump(content, handle)

            if assume_known:
                cfg.collect_json(path)
            else:
                cfg.collect_config_file(path)
        tfolder.cleanup()

        self.assertEqual(cfg['test.json.p1'], 17)
        self.assertEqual(cfg['test.json.p2'], 11)

    def test_yaml(self, assume_known=True):
        Section('test.yaml').params(
            p1=Param(float),
            p2=Param(float)
        )

        cfg = get_current_config()

        tfolder = tempfile.TemporaryDirectory()
        with tfolder as tmp:
            path = os.path.join(tmp, 'something')
            content = {
                'test': {'yaml': {'p1': 15}},
                'test.yaml.p2': 18
            }

            dumped = yaml.dump(content)

            with open(path, 'w') as handle:
                handle.write(dumped)

            if assume_known:
                cfg.collect_yaml(path)
            else:
                cfg.collect_config_file(path)
        tfolder.cleanup()

        self.assertEqual(cfg['test.yaml.p1'], 15)
        self.assertEqual(cfg['test.yaml.p2'], 18)

    def test_any_format(self):
        self.test_yaml(assume_known=False)
        self.setUp()
        self.test_json(assume_known=False)

    def test_priority(self):
        Section('prio').params(
            p1=Param(float),
            p2=Param(float),
            p3=Param(float)
        )

        cfg = get_current_config()

        tfolder = tempfile.TemporaryDirectory()
        with tfolder as tmp:
            path = os.path.join(tmp, 'something')
            content = {
                'prio.p1': 1,
                'prio.p2': 1,
                'prio.p3': 1,
            }

            dumped = yaml.dump(content)

            with open(path, 'w') as handle:
                handle.write(dumped)

            cfg.collect_config_file(path)
        tfolder.cleanup()

        os.environ['prio.p2'] = '2'
        os.environ['prio.p3'] = '2'
        cfg.collect_env_variables()

        cfg.collect({
            'prio.p3': 3
        })

        self.assertEqual(cfg['prio.p1'], 1)
        self.assertEqual(cfg['prio.p2'], 2)
        self.assertEqual(cfg['prio.p3'], 3)


    def test_argparse(self):
        Section('sec1.test', 'mydesc2').params(
            p1=Param(float)
        )

        Section('sec2.titi').params(
            p1=Param(float, 'mydesc1'),
            p2=Param(int, required=True)
        )

        tfolder = tempfile.TemporaryDirectory()

        with tfolder as tmp:
            path = os.path.join(tmp, 'something')
            content = {
                'sec1.test.p1': 1,
                'sec2.titi.p1': 1,
                'sec2.titi.p2': 1,
            }

            dumped = yaml.dump(content)

            with open(path, 'w') as handle:
                handle.write(dumped)

            cfg = get_current_config()
            parser = argparse.ArgumentParser(description='Test lib')
            os.environ['sec2.titi.p2'] = '3'
            with patch('sys.argv', ['pp', '--sec2.titi.p1=2', '-C', path]):
                cfg.augment_argparse(parser)
                cfg.collect_argparse_args(parser)

        tfolder.cleanup()

        self.assertEqual(cfg['sec1.test.p1'], 1)
        self.assertEqual(cfg['sec2.titi.p1'], 2)
        self.assertEqual(cfg['sec2.titi.p2'], 3)

        self.assertIn('sec1.test.p1', parser.epilog)
        self.assertIn('mydesc1', parser.epilog)
        self.assertIn('mydesc2', parser.epilog)

    def test_modules_visible_in_help(self):
        Section('module.import').params(
            module=Param(Module(), required=True)
        )

        cfg = get_current_config()
        parser = argparse.ArgumentParser(description='Test lib')
        os.environ['sec2.titi.p2'] = '3'
        with patch('sys.argv', ['pp', '--module.import.module=test_module.with_params']):
            cfg.augment_argparse(parser)

        self.assertIn('imported_section.blah.p1', parser.epilog)
        sys.modules.pop('test_module.with_params')


if __name__ == '__main__':
    unittest.main()
