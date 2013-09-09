#!/usr/bin/env python

from setuptools import setup


setup(
    name='django-agent-trust',
    version='0.1.7',
    description="A framework for managing agent trust, such as public vs. private computers.",
    long_description=open('README').read(),
    author='Peter Sagerson',
    author_email='psagersDjwublJf@ignorare.net',
    packages=[
        'django_agent_trust',
        'django_agent_trust.tests',
    ],
    url='https://bitbucket.org/psagers/django-agent-trust',
    license='BSD',
    install_requires=[
        'six',
        'django>=1.4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
