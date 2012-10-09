#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='django-agent-trust',
    version='0.1.5',
    description="A framework for managing agent trust, such as public vs. private computers.",
    long_description=open('README').read(),
    author='Peter Sagerson',
    author_email='psagersDjwublJf@ignorare.net',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    url='https://bitbucket.org/psagers/django-agent-trust',
    license='BSD',
    install_requires=[
        'django>=1.4',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
) 
