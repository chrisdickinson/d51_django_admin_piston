from distutils.core import setup
import os, sys

setup(name="d51_django_admin_piston",
      version="0.0.1",
      description="Automatically add piston resources for all registered modeladmins",
      author="Chris Dickinson",
      author_email="chris@neversaw.us",
      url="http://github.com/chrisdickinson/d51_django_admin_piston",
      packages=["d51_django_admin_piston"],
      classifiers=["Development Status :: 3 - Alpha",
                   "Environment :: Web Environment",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: Common Development and Distribution License (CDDL)",
                   "License :: OSI Approved :: GNU Public License (GPL)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Framework :: Django",])

