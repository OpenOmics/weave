from setuptools import setup, find_packages    

with open('src/Dmux/__meta__.py') as meta:
    dunder = {}
    exec(compile(meta.read(), '__meta__.py', 'exec'), dunder)

reqs = open('requirements.txt').readlines()

setup(
    name=dunder['__name__'],
    version=dunder['__version__'],
    install_requires=reqs,
    package_dir={'Dmux': 'src/Dmux'},
    scripts=['bin/dmux']
)