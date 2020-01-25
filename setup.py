#
#   pyforwarder a raw socket proxy with optional SSL/TLS termination and trace capability
#   Copyright (C) 2018-2020 Marc Bertens-Nguyen m.bertens@pe2mbs.nl
#
#   This library is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Library General Public License GPL-2.0-only
#   as published by the Free Software Foundation; either version 2 of the
#   License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#   Library General Public License for more details.
#
#   You should have received a copy of the GNU Library General Public
#   License GPL-2.0-only along with this library; if not, write to the
#   Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301 USA
#
# Always prefer setuptools over distutils
import setuptools
from forwarder.version import __version__, __author__, __copyright__, __email__, __url__

with open( "README.md", "r") as stream:
    long_description = stream.read()

setuptools.setup(
    name="forwarder", # Replace with your own username
    version=__version__,
    author=__author__,
    author_email=__email__,
    description="forwarder a raw socket proxy with optional SSL/TLS termination and trace capability",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__url__,
    keywords = "forward proxy TCP UDP SSL/TLS",
    packages=setuptools.find_packages(),
    project_urls={
        "Bug Tracker": __url__ + '/íssues',
        "Documentation": __url__+ '/wiki',
        "Source Code": __url__,
    },
    install_requires = [ 'pyyaml' ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Communications",
        "Topic :: Education :: Testing",
        "Topic :: Internet",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Software Development",
        "Topic :: Utilities",
        "Natural Language :: English",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "pyforwarder = forwarder.__main__:start"
        ]
    },
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": [ "*.md" ],
        # And include any *.msg files found in the "hello" package, too:
        "forwarder": [ "*.yaml" ],
    }
)