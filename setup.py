import os

try:
    from setuptools import setup
    from setuptools import find_packages
    packages = find_packages()
except ImportError:
    from distutils.core import setup
    packages = [x.strip('./').replace('/', '.') for x in os.popen('find -name "__init__.py" | xargs -n1 dirname').read().strip().split('\n')]

setup(
    name='perfharness',
    version='1.0',
    packages=packages,
    install_requires=[
        'sqlalchemy',
        'psutil',
        'distro; sys_platform == "linux"',
        'parsedatetime',
    ],
    extras_require={
        "viz": [
            "matplotlib",
            "pandas",
        ]
    }
)
