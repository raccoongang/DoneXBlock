"""Setup for done XBlock."""

import os
from setuptools import setup


def package_data(pkg, roots):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for root in roots:
        for dirname, _, files in os.walk(os.path.join(pkg, root)):
            for fname in files:
                data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='done-xblock',
    version='1.0',
    description='done XBlock',   # TODO: write a better description.
    packages=[
        'done',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'done = done:DoneXBlock',
        ]
    },
    package_data=package_data("done", ["static", "translations", "public"]),
)