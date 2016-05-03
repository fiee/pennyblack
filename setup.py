#! /usr/bin/env python
# -*- encoding: utf-8 -*-
import os
from setuptools import setup

import pennyblack
setup(
    name='pennyblack',
    version=pennyblack.__version__,
    description='django based newsletter toolkit (fiëé fork)',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    author='Marc Egli et al.',
    author_email='egli@allink.ch',
    url='http://github.com/fiee/pennyblack/',
    license='BSD License',
    platforms=['OS Independent'],
    packages=[
        'pennyblack',
        'pennyblack.content',
        'pennyblack.management',
        'pennyblack.management.commands',
        'pennyblack.models',
        'pennyblack.module',
        'pennyblack.module.subscriber',
        'pennyblack.templatetags',
    ],
    # package_data={'pennyblack':'templates/*.html'},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Communications :: Email',
    ],
    requires=[
        'FeinCMS(>=1.3.0)',
        'Django(>=1.3)',
        'pydns(>=2.3.4)',  # current: 2.3.6
        'pyspf(>=2.0.5)',  # current: 2.0.11
        'pil',
    ],
    include_package_data=True,
)
