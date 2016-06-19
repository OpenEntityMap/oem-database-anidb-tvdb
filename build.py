from ConfigParser import SafeConfigParser
from argparse import ArgumentParser
from copy import deepcopy
from subprocess import Popen
import argparse
import os
import shutil

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
MODULE_NAME = 'oem_database_anidb_tvdb'

DEFAULT_FORMATS = [
    # Complete
    None,

    # JSON
    'json', 'min.json', 'pre.json',

    # MessagePack
    'mpack', 'min.mpack'
]


def initialize_environment(fmt=None):
    fmt_module_name = get_module_name(fmt)

    build_path = os.path.join('.build', (fmt or 'full').replace('.', '_'))

    if os.path.exists(build_path):
        shutil.rmtree(build_path)

    os.makedirs(build_path)

    print('Initializing build environment for %s...' % (fmt or 'full'))

    # Initialize build environment
    shutil.copy2('setup.cfg', os.path.join(build_path, 'setup.cfg'))
    shutil.copy2('setup.py', os.path.join(build_path, 'setup.py'))

    def tree_filter(src, names):
        ignore = []

        for name in names:
            if name == 'package.json':
                continue

            if '.' not in name:
                continue

            ext = name[name.index('.') + 1:]

            if fmt is not None and ext != fmt:
                ignore.append(name)

        return ignore

    print(' - Copying %r to %r' % (MODULE_NAME, os.path.join(build_path, fmt_module_name)))

    shutil.copytree(
        MODULE_NAME,
        os.path.join(build_path, fmt_module_name),
        ignore=tree_filter
    )

    # Update "setup.cfg"
    config = SafeConfigParser()
    config.read(os.path.join(build_path, 'setup.cfg'))

    if not config.has_section('oem-database'):
        config.add_section('oem-database')

    config.set('oem-database', 'fmt', fmt or 'full')
    config.set('oem-database', 'fmt_module_name', fmt_module_name)

    with open(os.path.join(build_path, 'setup.cfg'), 'w') as fp:
        config.write(fp)

    print(' - Done')
    return build_path


def build(fmt, build_path):
    # Build environment for format
    env = deepcopy(os.environ)

    if fmt is not None:
        env['FORMAT'] = fmt
        env['FORMAT_MODULE_NAME'] = get_module_name(fmt)

    # Run command for `fmt`
    process = Popen(
        ['python', 'setup.py', command],
        cwd=build_path,
        env=env
    )

    process.wait()

    # Copy artifacts to root directory
    copy_artifacts_dist(build_path)

    # Delete build directory
    shutil.rmtree(build_path)


def copy_artifacts_dist(build_path):
    source_path = os.path.join(build_path, 'dist')
    target_path = os.path.join(CURRENT_DIR, 'dist')

    if not os.path.exists(source_path):
        return

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    for name in os.listdir(source_path):
        path = os.path.join(source_path, name)

        shutil.copy2(path, os.path.join(target_path, name))


def get_module_name(fmt):
    if fmt is None or fmt == 'full':
        return MODULE_NAME

    return MODULE_NAME + '_' + fmt.replace('.', '_')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--format', action='append')
    parser.add_argument('--command')

    args = parser.parse_args()

    # Parse `format` parameter
    fmts = args.format

    if not fmts:
        fmts = DEFAULT_FORMATS

    # Parse `command` parameter
    command = args.command

    if not command:
        exit(1)

    # Run format commands
    for fmt in fmts:
        if fmt == 'full':
            fmt = None

        build_path = initialize_environment(fmt)

        # Run build for `fmt`
        build(fmt, build_path)
