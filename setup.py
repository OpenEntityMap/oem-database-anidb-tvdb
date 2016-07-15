from ConfigParser import SafeConfigParser
from setuptools import setup
import os

CURRENT_DIR = os.path.dirname(__file__)

MODULE_NAME = 'oem_database_anidb_tvdb'
MODULE_DIR = os.path.join(CURRENT_DIR, MODULE_NAME)

PACKAGE_NAME = 'oem-database-anidb-tvdb'


def build_config():
    config = {
        'name': PACKAGE_NAME,
        'version': '1.16.4',

        'author': 'Dean Gardiner',
        'author_email': 'me@dgardiner.net',

        'classifiers': [
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Topic :: Database'
        ],

        'packages': [MODULE_NAME]
    }

    # Configure specific format
    fmt, fmt_module_name = get_parameters()

    if fmt and fmt_module_name:
        print('Using configuration:')
        print(' - fmt: %r' % fmt)
        print(' - fmt_module_name: %r' % fmt_module_name)

        # Update name
        config['name'] = config['name'] + '.' + fmt
        config['packages'] = [fmt_module_name]

        # Define package data
        config['package_data'] = {
            fmt_module_name: ['*.json'] + find_files(
                fmt,
                os.path.join(CURRENT_DIR, fmt_module_name)
            ),
        }
    else:
        # Define package data
        config['package_data'] = {
            MODULE_NAME: ['*.json'] + find_files(),
        }

    return config


def find_files(fmt=None, module_dir=MODULE_DIR):
    result = []

    for root, dirs, files in os.walk(module_dir):
        for name in files:
            ext = name[name.index('.') + 1:]

            if fmt is not None and ext != fmt:
                continue

            result.append(os.path.relpath(
                os.path.join(root, name),
                module_dir
            ))

    return result


def get_parameters():
    # Read parameters from "setup.cfg" (if available)
    if os.path.exists(os.path.join(CURRENT_DIR, 'setup.cfg')):
        config = SafeConfigParser()
        config.read(os.path.join(CURRENT_DIR, 'setup.cfg'))

        if config.has_section('oem-database'):
            fmt = config.get('oem-database', 'fmt')
            fmt_module_name = config.get('oem-database', 'fmt_module_name')

            if fmt == 'full':
                return None, None

            return fmt, fmt_module_name

    # Read parameters from environment
    return (
        os.environ.get('FORMAT'),
        os.environ.get('FORMAT_MODULE_NAME')
    )


if __name__ == '__main__':
    # Process setup commands
    setup(**build_config())
