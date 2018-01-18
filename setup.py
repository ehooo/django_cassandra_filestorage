from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

import django_cassandra_filestorage as meta

setup(name='django-cassandra-filestorage',
      description='Support for storage files in Cassandra.',
      version='.'.join(map(str, meta.__version__)),
      author=meta.__author__,
      author_email=meta.__contact__,
      url=meta.__homepage__,
      license=meta.__license__,
      keywords='django cassandra backend filestorage storage cloud remote',
      classifiers=[
          "Framework :: Django",
          "Environment :: Web Environment",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2.7",
          "License :: OSI Approved :: Apache Software License",
      ],
      packages=find_packages())
