#!/usr/bin/env python3

import os
import pathlib

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF


def generate_emojies():
    cwd = pathlib.Path.cwd()

    for root, dirs, files in os.walk('{}/emojies/svg'.format(cwd)):
        for name in files:
            source = os.path.join(root, name)
            target = os.path.join(
                '{}/emojies'.format(cwd),
                '{}.pdf'.format(name.split('.')[0].upper()))

            drawing = svg2rlg(source)
            renderPDF.drawToFile(drawing, target)
            print('coverting', drawing, target)


def main():
    generate_emojies()


if __name__ == '__main__':
    main()
