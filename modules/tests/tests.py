#!/usr/bin/env python3

from modules.utils.file_utils import read_file


def test_read_file():
    data = read_file('modules/tests/files/hello_world.md')

    assert data == '# Hello World\n'
