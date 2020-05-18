#!/usr/bin/env python3

import os
import pathlib

from magic import from_file


def read_file(p):
    with open(p, 'r') as f:
        return f.read()


def write_file(p, t, i):
    with open(p, t) as f:
        f.write(i)


def file_exists(p):
    if os.path.isfile(p):
        return True

    return False


def makedir(p):
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)


def file_name(p):
    name = os.path.splitext(os.path.basename(p))[0]

    return name


def file_extension(p):
    name = os.path.splitext(os.path.basename(p))[1]

    return name


def file_path(p):
    cwd = pathlib.Path.cwd()
    path = os.path.join(cwd, *p.split('/'))

    return path


def file_type(p):
    type = from_file(p, mime=True)

    return type
