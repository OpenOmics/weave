from setuptools import setup
from pathlib import Path
import os


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('workflow')

with open('src/Dmux/__meta__.py') as meta:
    dunder = {}
    exec(compile(meta.read(), '__meta__.py', 'exec'), dunder)

reqs = open('requirements.txt').readlines()

setup(
    name=dunder['__name__'],
    version=dunder['__version__'],
    install_requires=reqs,
    python_requires='>3.6.0',
    packages=['Dmux'],
    package_dir={"": "src"},
    include_package_data=True,
    package_data={'': ['workflow/**/*', 'profiles/**/*', 'config/*.json']},
    scripts=['bin/dmux', 'bin/dmux.py'],
)