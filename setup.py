from pathlib import Path
from setuptools import setup, find_packages

README = None
if Path('README.md').exists():
    with open('README.md','r') as f:
        README = f.read()

setup(
    name='keyframed',
    version='0.0.1',
    author='David Marx',
    long_description=README,
    install_requires=[
        'traces',
        'numexpr'
    ],
    extras_require={
        'dev': [
            'pytest'
    ]},
    packages=find_packages(
        where='src',
        include=['keyframed*'],
    ),
    package_dir = {"": "src"},
    license='MIT',
)
