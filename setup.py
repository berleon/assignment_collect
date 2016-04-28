
from distutils.core import setup

setup(
    name='assignment_collect',
    version='1.0',
    description='Assignment collection tool',
    author='Leon Sixt',
    author_email='git@leon-sixt.de',
    packages=['assignment_collect'],
    scripts=[
        'scripts/run_in_dirs',
        'scripts/open_notebook',
        'scripts/run_notebook',
    ],
    entry_points={
        'console_scripts': [
            'clone_all = assignment_collect.clone_all:main',
            'collect_points = assignment_collect.collect_points:main'
        ]
    },
)
