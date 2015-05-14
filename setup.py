#!/usr/bin/env python
import gitgitlab
from setuptools import setup, find_packages

install_requires = ['GitPython>=1.0.1', 'argparse', 'opster==4.1', 'libsaas==0.4']

setup(
    name="git-gitlab",
    scripts=['bin/git-gitlab'],
    version=gitgitlab.__version__,
    description="Git extensions",
    author=gitgitlab.__author__,
    author_email=gitgitlab.__contact__,
    url=gitgitlab.__homepage__,
    platforms=["any"],
    license="BSD",
    packages=find_packages(),
    install_requires=install_requires,
    zip_safe=False,
    classifiers=[
        # Picked from
        #    http://pypi.python.org/pypi?:action=list_classifiers
        #"Development Status :: 1 - Planning",
        "Development Status :: 2 - Pre-Alpha",
        #"Development Status :: 3 - Alpha",
        #"Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        #"Development Status :: 6 - Mature",
        #"Development Status :: 7 - Inactive",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Software Development :: Version Control",
    ]
)
