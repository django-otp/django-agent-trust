#!/usr/bin/env python

from setuptools import setup


setup(
    name='django-agent-trust',
    version='0.1.9',
    description="A framework for managing agent trust, such as public vs. private computers.",
    long_description=open('README').read(),
    author='Peter Sagerson',
    author_email='psagersDjwublJf@ignorare.net',
    packages=[
        'django_agent_trust',
        'django_agent_trust.test',
    ],
    url='https://bitbucket.org/psagers/django-agent-trust',
    license='BSD',
    install_requires=[
        'django>=1.4',
    ],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
