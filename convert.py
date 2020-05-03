#!/usr/bin/env python3

import gi
import os
import re
import math
import cairo
import pathlib
import requests
import pypandoc

from urllib.parse import urlparse
from requests.exceptions import HTTPError
from gi.repository.GLib import Error

gi.require_version('Rsvg', '2.0')

from gi.repository import Rsvg  # noqa: E402


def readfile(p):
    with open(p, 'r') as f:
        return f.read()


def writefile(p, t, i):
    with open(p, t) as f:
        f.write(i)


def download(p):
    res = requests.get(p)

    try:
        res.raise_for_status()
    except HTTPError:
        return None

    return res.content


def fileexists(p):
    if os.path.isfile(p):
        return True

    return False


def pixeltomm(p):
    value = math.floor(p * 25.4) / 96

    return value


def workingdir():
    dir = pathlib.Path().absolute()

    return dir


def filename(p):
    name = os.path.basename(p).split('.')[0]

    return name


def file_path(p):
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, *p.split('/'))

    return path


def convert_image(p, o):
    handle = Rsvg.Handle()

    try:
        svg = handle.new_from_file(p)
    except Error:
        return

    unscaled_width = svg.props.width
    unscaled_height = svg.props.height

    svg_surface = cairo.SVGSurface(None, unscaled_width, unscaled_height)
    svg_context = cairo.Context(svg_surface)
    svg_context.save()
    svg.render_cairo(svg_context)
    svg_context.restore()
    svg_surface.write_to_png(o)

    dimensions = [unscaled_width, unscaled_height]

    return dimensions


def main():
    latex_body = pypandoc.convert_file('README.md', 'latex', format='md')
    latex_header = readfile('header.tex')
    latex_doc = '{document}'

    latex = '{0}\n\\begin{2}{1}\n\\end{2}'.format(
        latex_header, latex_body, latex_doc
    )

    verbatim_pattern = re.compile(r'\\begin{Verbatim}')
    url_pattern = re.compile(
        r'\\(includegraphics){(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]| \
        (?:%[0-9a-fA-F][0-9a-fA-F]))+)}')

    verbatim_replace = r'\\begin{Verbatim}[breaklines=true]'
    latex = re.sub(verbatim_pattern, verbatim_replace, latex)

    urls = re.findall(url_pattern, latex)

    for url in urls:
        parsed = urlparse(url[1])
        path = parsed.path
        file = os.path.basename(path)
        latex = latex.replace(url[1], './assets/{}.png'.format(filename(file)))

        if not fileexists('{}/assets/{}'.format(workingdir(), file)):
            file_path_str = file_path('/assets/{}'.format(file))

            resource = download(url[1])

            if not resource:
                continue

            writefile(file_path_str, 'wb', resource)

            outputpath = '{}/assets/{}.png'.format(workingdir(), filename(file))
            dimensions = convert_image(file_path_str, outputpath)

            outputfile = '{{./assets/{}.png}}'.format(filename(file))
            img_pattern = re.compile(r'\\(includegraphics{0})'.format(outputfile))

            if dimensions:
                img_replace = r'\\includegraphics[width={0}mm, height={1}mm]{2}'.format(
                    pixeltomm(dimensions[0]), pixeltomm(dimensions[1]), outputfile)
            else:
                img_replace = r'\\includegraphics[width=\\textwidth]{0}'.format(outputfile)

            latex = re.sub(img_pattern, img_replace, latex)

            print(dimensions)

    writefile(file_path('/output/markdown.tex'), 'w', latex)


if __name__ == '__main__':
    main()
