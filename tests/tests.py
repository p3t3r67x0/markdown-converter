#!/usr/bin/env python3

from module.converter import read_file


def test_read_file():
    data = read_file('tests/files/hello_world.md')

    assert data == '# Hello World\n'
