from setuptools import setup, find_packages 
from pathlib import Path


with open('src/Dmux/__meta__.py') as meta:
    dunder = {}
    exec(compile(meta.read(), '__meta__.py', 'exec'), dunder)

reqs = open('requirements.txt').readlines()

def recursive_list_all_files(top_dir):
    _files = list(Path(top_dir).rglob('*'))
    ignore_these = ('__pycache__',)
    _files = [
        x for x in _files 
        if x.name not in ignore_these and \
            all([_ign not in x.parents for _ign in ignore_these]) and \
            all([not _par.name.startswith('.') for _par in x.parents]) and \
            not x.name.startswith('.')
    ]
    return list(map(str, _files))

setup(
    name=dunder['__name__'],
    version=dunder['__version__'],
    install_requires=reqs,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "Dmux": ["profiles/**"]
    },
    scripts=['bin/dmux', 'bin/dmux.py']
)   