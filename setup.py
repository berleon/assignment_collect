
from distutils.core import setup

setup(
    name='assignment_collect',
    version='1.0',
    description='Tool to orangise assignments over git.',
    author='Leon Sixt',
    author_email='git@leon-sixt.de',
    packages=['assignment_collect'],
    scripts=[
        'scripts/run_in_dirs',
        'scripts/open_notebook',
        'scripts/run_notebook',
        'scripts/nb_strip_output.py',
    ],
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'clone_all = assignment_collect.clone_all:main',
            'collect_points = assignment_collect.collect_points:main',
            'complete_student_data = assignment_collect.complete_student_data:main',
            'assignment = assignment_collect.assignment:main',
        ]
    },
)
