# _*_ coding: utf-8 _*_
from setuptools import setup
setup(
  name="josh",
  version='1.0.0',
  url='https://github.com/andrleite/josh',
  author='Andre Leite',
  author_email='andrleite@gmai.com',
  description='AWS Job Scheduler',
  packages=['josh', 'tests'],
  test_suite='tests',
)