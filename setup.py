from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-scaffold',
    version='0.0.0',
    description='Django build command to generate your app',
    packages=find_packages(),
    include_package_data=True,
)
