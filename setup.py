from setuptools import setup, find_packages    

with open('src/Dmux/__meta__.py') as meta:
    dunder = {}
    exec(compile(meta.read(), '__meta__.py', 'exec'), dunder)

reqs = open('requirements.txt').readlines()

setup(
    name=dunder['__name__'],
    version=dunder['__version__'],
    install_requires=reqs,
    packages=find_packages(exclude=['test']),
    scripts=['bin/dmux']
)