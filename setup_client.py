from setuptools import setup, find_packages

from setup import __version__, NAME_CLIENT, long_description, load_requirements

setup(
    name=NAME_CLIENT,
    version=__version__,
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
    packages=find_packages(where='src_client', exclude=['tests', ]),
    package_dir={'': 'src_client'},
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            '{0} = {0}.__main__:main'.format(NAME_CLIENT),
        ]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=load_requirements('requirements.txt'),
)
