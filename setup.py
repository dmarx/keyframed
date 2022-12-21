from pathlib import Path
from setuptools import setup, find_packages

README = None
if Path('README.md').exists():
    with open('README.md','r') as f:
        README = f.read()

st = """
Keyframed is a time series data type that allows users to store and retrieve data at specified time indices. The motivation for this library is to facilitate object-oriented parameterization of generative animations.
""".strip()
        
setup(
    name='keyframed',
    version='0.0.4',
    author='David Marx',
    long_description=README,
    long_description_content_type='text/markdown',
    short_description=st,
    install_requires=[
        'traces',
        'numexpr',
        'loguru',
        'scipy',
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
