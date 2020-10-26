from pkg_resources import parse_requirements
from setuptools import find_packages, setup


def load_requirements(filename: str) -> list:
    requirements = []
    with open(filename, 'r') as f:
        for requirement in parse_requirements(f.read()):
            extras = '[{}]'.format(','.join(requirement.extras)) if requirement.extras else ''
            requirements.append(
                '{}{}{}'.format(requirement.name, extras, requirement.specifier)
            )
    return requirements


module_name = 'experiment_collection'

with open('README.md', 'rt') as f:
    long_description = f.read()

setup(
    name=module_name,
    version='0.1.6',
    description='Experiment collection',
    long_description=long_description,
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
    packages=find_packages(exclude=['tests']),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            '{0} = {0}.__main__:main'.format(module_name),
        ]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=load_requirements('requirements.txt'),
)
