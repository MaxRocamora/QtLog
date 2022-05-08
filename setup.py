import os
import io
from qtlog.version import version
from setuptools import setup, find_packages

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
here = os.path.abspath(os.path.dirname(__file__))
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except (IOError, OSError):
    long_description = ""

setup(
    name='qt-log',
    version=version,
    description='Qt Custom UI Log for Maya/Houdini',
    author='Maximiliano Rocamora',
    author_email='maxirocamora@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/MaxRocamora/QtLog',
    license='GNU GENERAL PUBLIC LICENSE',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: Freely Distributable",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires='>=3.7'
)
