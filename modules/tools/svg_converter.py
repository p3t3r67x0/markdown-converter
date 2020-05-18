#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import re
import pathlib
import argparse
import svgwrite

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from svgpathtools import SaxDocument, svg2paths, wsvg
from svgwrite.container import Group

from utils.file_utils import read_file, file_name


def replace_unicode():
    cwd = pathlib.Path.cwd()

    string = read_file('{}/output/README.md'.format(cwd))

    pattern = re.compile(r'([^\x00-\x7F])')
    output = re.findall(pattern, string)
    print(output)

    for i in output:
        print('{:x}'.format(ord(i)).upper())


def generate_pdf(source):
    cwd = pathlib.Path.cwd()
    name = file_name(source)

    target = os.path.join(
        '{}/fonts'.format(cwd),
        '{}.pdf'.format(name.split('.')[0].upper()))

    drawing = svg2rlg(source)
    renderPDF.drawToFile(drawing, target)
    print('converting svg to pdf', target)


def bounding_box(path):
    bbs = []

    for p in path:
        bbs.append(p.bbox())

    try:
        xmins, xmaxs, ymins, ymaxs = list(zip(*bbs))
    except Exception as e:
        print(e)
        return

    xmin = min(xmins)
    xmax = max(xmaxs)
    ymin = min(ymins)
    ymax = max(ymaxs)

    return xmin, xmax, ymin, ymax


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
            print('coverting', target)


def convert_font():
    cwd = pathlib.Path.cwd()

    for root, dirs, files in os.walk('{}/exports'.format(cwd)):
        for name in files:
            source = os.path.join(root, name)
            target = 'fonts/{}.min.svg'.format(name.split('.')[0])
            print(source)

            try:
                paths, attr = svg2paths(source)
            except Exception as e:
                print(e)
                continue

            try:
                xmin, xmax, ymin, ymax = bounding_box(paths)
            except Exception as e:
                print(e)
                continue

            dx = xmax - xmin
            dy = ymax - ymin

            viewbox = '{} {} {} {}'.format(xmin, ymin, dx, dy)

            attr = {
                'viewBox': viewbox,
                'preserveAspectRatio': 'xMidYMid meet'
            }

            wsvg(paths=paths, svg_attributes=attr, filename=source)

            doc = SaxDocument(source)
            d = doc.get_pathd_and_matrix()[0]
            g = Group()

            dwg = svgwrite.Drawing(target)
            dwg.viewbox(minx=xmin, miny=ymin, width=dx, height=dy)
            dwg.add(g)
            g.scale(sx=1, sy=-1)
            g.translate(tx=0, ty=-dy - ymin * 2)
            g.add(dwg.path(d))
            dwg.save()

            generate_pdf(target)


def argparser():
    parser = argparse.ArgumentParser(description='Utility methods.')

    parser.add_argument('--pdf', action='store_true',
                        required=False, help='set flag for pdf generation')
    parser.add_argument('--input', dest='input',
                        required=True, help='define input file')
    parser.add_argument('--output', dest='output',
                        required=True, help='define output file_name')
    parser.add_argument('--format', dest='format',
                        required=True, help='define input format')

    args = parser.parse_args()

    return args


def main():
    args = argparser()

    generate_pdf(args.input, args.output)


if __name__ == '__main__':
    main()
