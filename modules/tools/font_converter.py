#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

import sys
import fontforge


def convert_truetype_svg():
    fontfile = sys.argv[1]

    try:
        font = fontforge.open(fontfile)
    except EnvironmentError:
        sys.exit(1)

    font.selection.all()
    font.correctDirection()
    font.removeOverlap()
    font.simplify()
    font.round()

    for glyph in font:
        file_name = '{:x}'.format(font[glyph].unicode).upper()
        file_path = 'exports/{}.svg'.format(file_name)

        if font[glyph].unicode < 0:
            continue

        font[glyph].export(file_path, True)
        print(file_path)


if __name__ == '__main__':
    convert_truetype_svg()
