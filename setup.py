import os
from setuptools import setup, find_packages
#from SVInsight import __version__ as version

with open('README.md', 'r') as f:
    long_description = f.read()


setup(
    name='SVInsight',
    version='0.3.2',
    license='MIT',
    description='SVInsight - A python package for calculating an exploratory social vulnerability index',
    author='M. Preisser, P. Passalacqua, R. P. Bixler',
    author_email='mattpreisser@gmail.com',
    url='https://github.com/mdp0023/SVInsight/',
    packages= find_packages(exclude=['*.tests']),
    package_data = {'' : ['*.txt', '*.npz']},
    long_description = long_description,
    long_description_content_type='text/markdown',
    classifiers=[],
    install_requires=['census',
                    'factor_analyzer',
                    'geopandas',
                    'numpy',
                    'pandas',
                    'PyYAML',
                    'scikit_learn']
)