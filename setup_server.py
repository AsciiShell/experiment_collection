from pkg_resources import parse_requirements
from setuptools import setup


def load_requirements(filename: str) -> list:
    requirements = []
    with open(filename, 'r') as f:
        for requirement in parse_requirements(f.read()):
            extras = '[{}]'.format(','.join(requirement.extras)) if requirement.extras else ''
            requirements.append('{}{}{}'.format(requirement.name, extras, requirement.specifier))
    return requirements


def load_description(filename: str = 'README.md'):
    with open(filename, 'rt') as f:
        return f.read()


__version__ = '0.2.7'
NAME_SERVER = 'experiment_collection_server'

setup(
    name=NAME_SERVER,
    version=__version__,
    description='Experiment collection',
    long_description=load_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/AsciiShell/experiment_collection',
    author='AsciiShell (Aleksey Podchezertsev)',
    author_email='dev@asciishell.ru',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
    ],
    keywords=['python3'],
    packages=['experiment_collection_core', 'experiment_collection_server', 'experiment_collection_server.db', ],
    package_dir={'': 'src'},
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            '{0} = {0}.__main__:main'.format(NAME_SERVER),
        ]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=load_requirements('requirements_server.txt'),
)
