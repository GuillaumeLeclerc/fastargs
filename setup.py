from setuptools import find_packages
from distutils.core import setup
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    long_description = ''

setup(
    name='fastargs',
    packages=find_packages('.'),
    version='0.1.0',
    license='MIT',
    description='Management library for parameters/configuration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Guillaume Leclerc',
    author_email='leclerc@mit.edu',
    url='https://github.com/GuillaumeLeclerc/fastargs',
    download_url='https://github.com/GuillaumeLeclerc/fastargs',
    keywords=['configuration', 'yaml', 'json', 'parameters',
              'hyper-parameters', 'management', 'decorators'],
    install_requires=[
        'pyyaml',
        'terminaltables'
    ],
    # https://pypi.org/classifiers/
    classifiers=['Development Status :: 3 - Alpha', 'Environment :: Console']
)
