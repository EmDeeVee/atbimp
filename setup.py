
from setuptools import setup, find_packages
from atbimp.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='atbimp',
    version=VERSION,
    description='Will allow you to import ATB csv files and list transactions',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Marc@Thing',
    author_email='MarcDiederik007@gmail.com',
    url='https://github.com/johndoe/myapp/',
    license='Apache License',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'atbimp': ['templates/*']},
    include_package_data=True,
    entry_points="""
        [console_scripts]
        atbimp = atbimp.main:main
    """,
)
