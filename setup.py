import os
from setuptools import setup, find_packages

setup(
    name='SVInsight',
    version='0.2.7',
    license='MIT',
    description='SVInsight - A python package for calculating an exploratory social vulnerability index',
    author='M. Preisser, P. Passalacqua, R. P. Bixler',
    author_email='mattpreisser@gmail.com',
    url='https://github.com/mdp0023/SVInsight/',
    packages= find_packages(exclude=['*.tests']),
    package_data = {'' : ['*.txt', '*.npz']},
    long_description = 'See preojct webpage for details',
    classifiers=[],
    install_requires=['census',
                    'factor_analyzer',
                    'geopandas',
                    'numpy',
                    'pandas',
                    'PyYAML',
                    'scikit_learn']
)