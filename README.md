# fastargs

Python library for argument and configuration management.

The goal of this library is to enable easy configuration of large code bases with many parameters. It should be particulary useful in machine learning applications with many hyper-parameters scattered across multiple files and components.

## Usage

### Install

1. PIP: `pip install fastargs`
2. Github: `pip install git+https://github.com/GuillaumeLeclerc/fastargs.git `

### Example
Simple full example available: https://github.com/GuillaumeLeclerc/fastargs/blob/main/examples/full_simple_example.py

### Declare the arguments

As demonstrated here you can declare your parameters in multiple files over your project. To make your code more readable it is recommended to declare the parameters as close as from where they are used.

In `train.py`:
```python
from fastargs import Section, Param
from fastargs.validation import InRange, And

Section("training.optimizer", "Optimizer parameters").params(
  learning_rate=Param(float, required=True),  # One can use simple type declaration
  momentum=Param(And(float, InRange(min=0)), default=0)  # Or more constrained validation rules
)

# The training code (see later sections on how to read the params)
```
In `dataloading.py`:
```python
from fastargs import Section, Param
from fastargs.validation import InRange, And

Section("data.loading", "Optimizer parameters").params(
  batch_size=Param(And(int, InRange(min=1)), required=True),
  num_workers=Param(And(int, InRange(min=0)), default=0)
)

# Data loading code
```

### Populate the arguments

Arguments can be defined from multiple sources (see below). They are not exclusive and can be mix and matched.
If a new source is added it overrides the previous one if a given argument was already defined.

In `main.py`:
```python
import argparse

# Import the rest of your code that declares the arguments
from fastargs import get_current_config

config = get_current_config()

# Option 1: From code
# -------------------

config.collect({
  'training.optimizer.learning_rate': 0.01,  # One can specify the path to arguments with dot notation
  'training.optimizer.momentum': 0.9,
  'data': {
    'loading': {
      'batch_size': 512  # One can have the structure explicit
    }
    'loading.num_workers': 10  # Or even a mix of both
  }
})


# Option 2: From a config file (yaml, json)
# -----------------------------------------

# Similarly one can use dot notation for arguments or use explicit structure (as shown in Option 1)
config.collect_config_file('./config.yaml')
config.collect_config_file('./config.json')


# Option 3: From env variables
# ----------------------------

# One can declare the env variables this way (bash)
# training.optimizer.momentum=0.9 python main.py
# OR
# export training.optimizer.momentum=0.9
# python main.py

config.collect_env_variables()


# Option 4: using argparse
# ------------------------

parser = argparse.ArgumentParser(description='fastargs demo')
config.augment_argparse(parser)
config.collect_argparse_args(parser)

# This will integrate fastargs with argparse
# It will:
# - Add a CLI argument for each fastargs argument
# - Generate a user friendly --help message
# - Allow the user to pass config files through CLI arguments and collect them aumatically for you
# - collect env variables
#
# Priority for duplicated parameters is: env variable, cli argument, config files from last to first
```

### Validating the arguments

Arguments are validated as you access them (see next section). However if you want to check all arguments at once you can do it too.

```python

# Option 1
# --------

errors = config.validate(mode='errordict')
# This will return you a dict where the keys are the parameters
# and the value the corresponding errors

# Option 2
# --------

config.validate(mode='stderr')
# If errors are found it will print a nice table summarizing all the errors 
# for the user and quit the program to let him fill the invalid/missing arguments

```

### Summary of parameters

You can produce a summary of the arguments defined:

```python
config.summary() 
# by default it will be written to stderr but you can change that by passing a file
# to the function
```

### Accessing arguments

#### Option 1: Explicitely

```python
# One can read individual arguments

config['training.optimizer.learning_rate']

# Or gather all arguments in a single object
arguments = config.get()
print(arguments.training.optimizer.learning_rate)
```

#### Option 2: Through decorators

It is possible to automatically feed arguments to functions without having to explicitely use the API of `fastargs`.


```python
from fastargs.decorators import param, section

@param('training.optimizer.learning_rate')
@param('training.optimizer.momentum')
def train_my_model(model, learning_rate, momentum):
  ### train your model
  
# To avoid repeating long path we offer the @section decorator

@section('training.optimizer')
@param('learning_rate')
@param('momentum')
def train_my_model(model, learning_rate, momentum):
  ### train your model
  
# Note that if one does:
train_my_model(model, learning_rate=10)
# the learning from the config will be ignored (but momentum will be since it wasn't explicitely overriden)

```
