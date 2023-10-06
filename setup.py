from setuptools import setup, find_packages 
from pathlib import Path


with open('src/Dmux/__meta__.py') as meta:
    dunder = {}
    exec(compile(meta.read(), '__meta__.py', 'exec'), dunder)

reqs = open('requirements.txt').readlines()

setup(
    name=dunder['__name__'],
    version=dunder['__version__'],
    install_requires=reqs,
    python_requires='>3.6.0',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "Dmux": ["profiles/**", "workflows/**"]
    },
    scripts=['bin/dmux', 'bin/dmux.py']
)