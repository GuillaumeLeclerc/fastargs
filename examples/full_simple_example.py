import argparse

from fastargs import Section, Param, get_current_config
from fastargs.validation import InRange, And
from fastargs.decorators import param

Section("module1.params", "Optimizer parameters").params(
  a=Param(float, required=True),
  b=Param(And(float, InRange(min=0)), default=0)
)

Section("module2.settings", "Optimizer parameters").params(
  c=Param(And(int, InRange(min=1)), required=True),
)

parser = argparse.ArgumentParser(description='fastargs demo')
config = get_current_config()
# This will allow user to pass arguments through CLI arguments + config files
# This will generate a nice help page if --help is passed
config.augment_argparse(parser)
config.collect_argparse_args(parser)


# This will generate a nice table with potential missing arguments
config.validate(mode='stderr')

config.summary()


@param('module1.params.a')
@param('module1.params.b')
@param('module2.settings.c')
def my_code(a, b, c):
    return (a + b) * c

# The arguments will be read from the config
print(my_code())

# Unless you override some explicitely
print(my_code(a=7))
