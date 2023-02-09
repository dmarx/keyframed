from pathlib import Path
from setuptools import setup, find_packages

README = None
if Path('README.md').exists():
    with open('README.md','r') as f:
        README = f.read()

st = """
Simple, expressive, pythonic datatypes for manipulating curves parameterized by keyframes and interpolators. The motivation for this library is to facilitate object-oriented parameterization of generative animations.
""".strip()
        
setup(
    name='keyframed',
    version='0.3.5',
    author='David Marx',
    long_description=README,
    long_description_content_type='text/markdown',
    short_description=st,
    install_requires=[
        'sortedcontainers',
        'omegaconf',
    ],
    extras_require={
        'dev': [
            'pytest',
            'loguru'
    ]},
    packages=find_packages(
        where='src',
        include=['keyframed*'],
    ),
    package_dir = {"": "src"},
    license='MIT',
)
