# coding=utf-8
from distutils.core import setup

setup(
    name='Inter',
    version='0.0.1',
    packages=['system'],
    url='https://github.com/gdude2002/Inter',
    license='',
    author='Gareth Coles',
    author_email='gdude2002@pageserved.com',
    description='Inter-server communication for Minecraft',
    requires=["PyYaml", "yapsy", "Zope.interface", "twisted", "psycopg2"]
)
