import unittest
import io

from fastargs import Config, set_current_config, get_current_config, Section, Param
from fastargs.validation import Anything

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        set_current_config((Config()))

    def test_can_declare_params(self):
        Section('test', 'This is a test section').params(
            p1=Param(Anything(), ),
            p2=Param(Anything(), ),
        )

    def test_can_collect_config(self):
        Section('test', 'This is a test section').params(
            p1=Param(Anything(), ),
            p2=Param(Anything(), ),
        )

        cfg = get_current_config()
        cfg.collect({'test.p1': 42})
        self.assertEqual(cfg['test.p1'], 42)
        self.assertIsNone(cfg['test.p2'])

    def test_multiple_sections(self):
        Section('first.sec', 'test_sec1').params(
            param=Param(Anything())
        )

        Section('second.sec', 'test_sec2').params(
            param=Param(Anything()),
            notdef=Param(Anything())
        )
        cfg = get_current_config().collect({
            'first': {
                'sec': {
                    'param': "happy"
                }
            },
            'second.sec.param': "sad"
        })
        self.assertEqual(cfg[('first', 'sec', 'param')], "happy")
        self.assertEqual(cfg['first.sec.param'], "happy")
        self.assertEqual(cfg['second.sec.param'], "sad")
        self.assertIsNone(cfg['second.sec.notdef'])

        args = cfg.get()
        self.assertEqual(args.first.sec.param, "happy")
        self.assertEqual(args.second.sec.param, "sad")
        self.assertIsNone(args.second.sec.notdef)


    def test_overriden(self):
        Section('first.sec', 'test_sec1').params(
            param=Param(Anything())
        )

        Section('second.sec', 'test_sec2').params(
            param=Param(Anything()),
            param2=Param(Anything())
        )

        get_current_config().collect({
            'first.sec.param': 1,
            'second.sec.param': 2,
            'second.sec.param2': 3,
        })

        get_current_config().collect({
            'first.sec': {
                'param': "over"
            }
        })

        args = get_current_config().get()
        self.assertEqual(args.first.sec.param, "over")
        self.assertEqual(args.second.sec.param, 2)
        self.assertEqual(args.second.sec.param2, 3)


    def test_params_updated(self):
        Section('first.sec', 'test_sec1').params(
            param=Param(Anything())
        )

        cfg = get_current_config().collect({'first.sec.param': 42})
        self.assertEqual(cfg['first.sec.param'], 42)
        cfg = get_current_config().collect({'first.sec.param': 43})
        args = cfg.get()
        self.assertEqual(args.first.sec.param, 43)

    def test_summary(self):
        Section('first.sec', 'test_sec1').params(
            param1=Param(Anything(), required=True),
            param2=Param(Anything(), default="3"),
            param3=Param(Anything(), required=False)
        )

        stream = io.StringIO()

        cfg = get_current_config().collect({
            'first.sec.param1': 42
        })

        cfg.summary(stream)
        output = stream.getvalue()

        self.assertIn('first.sec.param1', output)
        self.assertIn('42', output)
        self.assertIn('first.sec.param2', output)
        self.assertIn('3', output)
        self.assertNotIn('first.sec.param3', output)


if __name__ == '__main__':
    unittest.main()
