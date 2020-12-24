from pkg_resources import parse_requirements


def load_requirements(filename: str) -> list:
    requirements = []
    with open(filename, 'r') as f:
        for requirement in parse_requirements(f.read()):
            extras = '[{}]'.format(','.join(requirement.extras)) if requirement.extras else ''
            requirements.append(
                '{}{}{}'.format(requirement.name, extras, requirement.specifier)
            )
    return requirements


def load_description(filename: str = 'README.md'):
    with open(filename, 'rt') as f:
        return f.read()


__version__ = '0.2.0'
NAME_CLIENT = 'experiment_collection'
NAME_SERVER = 'experiment_collection_server'
long_description = load_description()

if __name__ == '__main__':
    print('Use setup_client or setup_server')
