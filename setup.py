#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='django-agent-trust',
    version='1.0.1',
    description="A framework for managing agent trust, such as public vs. private computers.",
    author="Peter Sagerson",
    author_email='psagers@ignorare.net',
    url='https://github.com/django-otp/django-agent-trust',
    project_urls={
        "Documentation": 'https://django-agent-trust-official.readthedocs.io/',
        "Source": 'https://github.com/django-otp/django-agent-trust',
    },
    license='BSD',

    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'django >= 2.2',
    ],

    classifiers=[
        'Programming Language :: Python :: 3',
        "Programming Language :: Python :: 3 :: Only",
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
