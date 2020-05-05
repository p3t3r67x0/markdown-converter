#!/usr/bin/env python3

import gi
import os
import re
import math
import cairo
import pathlib
import argparse
import requests
import subprocess
import pypandoc
import logging
import uuid

from magic import from_file
from PIL import Image, UnidentifiedImageError
from requests.exceptions import ConnectionError, HTTPError
from urllib.parse import urlparse, unquote
from gi.repository.GLib import Error

gi.require_version('Rsvg', '2.0')

from gi.repository import Rsvg  # noqa: E402


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('converter')


def readfile(p):
    with open(p, 'r') as f:
        return f.read()


def write_file(p, t, i):
    with open(p, t) as f:
        f.write(i)


def download(p):
    res = requests.get(p)

    try:
        res.raise_for_status()
    except HTTPError as e:
        logger.error(e)
        return None
    except ConnectionError as e:
        logger.error(e)
        return None

    return res.content


def file_exists(p):
    if os.path.isfile(p):
        return True

    return False


def pixeltomm(p):
    value = math.floor(p * 25.4) / 112

    return value


def workingdir():
    dir = pathlib.Path().absolute()

    return dir


def makedir(p):
    pathlib.Path(p).mkdir(parents=True, exist_ok=True)


def file_name(p):
    name = os.path.splitext(os.path.basename(p))[0]

    return name


def file_extension(p):
    name = os.path.splitext(os.path.basename(p))[1]

    return name


def file_path(p):
    dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(dir, *p.split('/'))

    return path


def file_type(p):
    type = from_file(p, mime=True)

    return type


def image_open(p):
    try:
        image = Image.open(p)
    except FileNotFoundError:
        return None
    except UnidentifiedImageError:
        return None

    return image


def image_dimensions(p):
    image = image_open(p)

    if not image:
        return None

    width, height = image.size
    dimensions = [width, height]

    return dimensions


def convert_gif_image(p, o):
    image = image_open(p)

    if not image:
        return None

    image.save(o)

    image = image_open(o)

    if not image:
        return None

    width, height = image.size
    dimensions = [width, height]

    return dimensions


def convert_svg_image(p, o):
    handle = Rsvg.Handle()

    try:
        svg = handle.new_from_file(p)
    except Error as e:
        logger.error(e)
        return None

    width = svg.props.width
    height = svg.props.height

    svg_surface = cairo.SVGSurface(None, width, height)
    svg_context = cairo.Context(svg_surface)
    svg_context.save()
    svg.render_cairo(svg_context)
    svg_context.restore()
    svg_surface.write_to_png(o)

    dimensions = [width, height]

    return dimensions


def argparser():
    parser = argparse.ArgumentParser(description='Process a markdown file.')

    parser.add_argument('--dry', action='store_true',
                        required=False, help='set flag for dry run')
    parser.add_argument('--input', dest='input',
                        required=True, help='define input file')
    parser.add_argument('--output', dest='output',
                        required=True, help='define output file_name')
    parser.add_argument('--format', dest='format',
                        required=True, help='define input format')

    args = parser.parse_args()

    return args


def convert_other(i, t, f):
    resource = pypandoc.convert_file(i, t, format=f)

    return resource


def convert_markdown(i, f):
    if f == 'gfm':
        f = 'html'
    elif f == 'rst':
        f = 'md'

    latex_body = pypandoc.convert_file(i, 'latex', format=f)
    latex_header = readfile('header.tex')
    latex_doc = '{document}'

    latex = '{0}\n\\begin{2}\n\n{1}\n\\end{2}'.format(
        latex_header, latex_body, latex_doc
    )

    return latex


def replace_rule(latex):
    rule_pattern = re.compile(r'\\rule\{0.5\\linewidth\}')
    rule_replace = r'\\par\\noindent\\rule{\\textwidth}'
    latex = re.sub(rule_pattern, rule_replace, latex)

    return latex


def replace_verbatim(latex):
    verbatim_pattern = re.compile(r'\\begin{Verbatim}')
    verbatim_replace = r'\\begin{Verbatim}[breaklines=true]'
    latex = re.sub(verbatim_pattern, verbatim_replace, latex)

    return latex


def replace_quote(latex):
    quote_begin_replace = r'\\begin{quoting}'
    quote_end_replace = r'\\end{quoting}'

    quote_begin_pattern = re.compile(r'\\begin\{quote\}')
    quote_end_pattern = re.compile(r'\\end\{quote\}')

    latex = re.sub(quote_begin_pattern, quote_begin_replace, latex)
    latex = re.sub(quote_end_pattern, quote_end_replace, latex)

    return latex


def find_all_images(latex):
    img_url_pattern = re.compile(
        r'\\(includegraphics){([a-zA-Z0-9$-_@.&+!*\(\), ]+)}')

    images = re.findall(img_url_pattern, latex)

    return images


def extract_image_path(raw_image_url):
    image_file = urlparse(raw_image_url).path

    image_source_path = file_path('/assets/{}{}'.format(
        str(uuid.uuid4()), file_extension(image_file)))

    return image_source_path


def image_relative_data(image_source_path, image_target_path):
    allowed_file_types = ['image/gif', 'image/svg']

    if file_type(image_source_path) not in allowed_file_types:
        image_relative_path = './assets/{}{}'.format(
            file_name(image_source_path),
            file_extension(image_source_path))

        image_relative_string = '{{./assets/{}{}}}'.format(
            file_name(image_target_path),
            file_extension(image_target_path))
    else:
        image_relative_path = './assets/{}.png'.format(
            file_name(image_target_path))

        image_relative_string = '{{./assets/{}.png}}'.format(
            file_name(image_target_path))

    return image_relative_path, image_relative_string


def check_convert_image(image_source_path, image_target_path):
    dimensions = None

    image_target_path = file_path('/assets/{}.png'.format(
        file_name(image_target_path)))

    if file_type(image_source_path) == 'image/svg':
        dimensions = convert_svg_image(
            image_source_path, image_target_path)

    elif file_type(image_source_path) == 'image/gif':
        dimensions = convert_gif_image(
            image_source_path, image_target_path)

    return dimensions


def check_convert_pixel(dimensions):
    width = pixeltomm(dimensions[0])

    if width <= 170:
        return True

    return False


def check_allowed_types(image_source_path, image_target_path, latex):
    allowed_file_types = ['image/svg', 'image/jpeg',
                          'image/bmp', 'image/png', 'image/gif']

    logger.info('identified mimetype: {}'.format(file_type(image_source_path)))

    image_path, image_relative_string = image_relative_data(
        image_source_path, image_target_path)

    if file_type(image_source_path) not in allowed_file_types:
        img_pattern = re.compile(
            r'\\(includegraphics{})'.format(image_relative_string))
        latex = re.sub(img_pattern, '', latex)

    return latex, image_path, image_relative_string


def replace_image(image_source_path, image_target_path, raw_image_url, latex):
    allowed_file_types = ['image/svg', 'image/jpeg',
                          'image/bmp', 'image/png', 'image/gif']

    latex, image_path, image_relative_string = check_allowed_types(
        image_source_path, image_target_path, latex)

    latex = latex.replace(raw_image_url, image_path)

    # remove includegraphics when image is not in allowed_file_types
    if file_type(image_source_path) not in allowed_file_types:
        img_pattern = re.compile(
            r'({{\\includegraphics{{{0}}}}})'.format(image_path))
        latex = re.sub(img_pattern, '', latex)

    dimensions = check_convert_image(image_source_path, image_target_path)

    if not dimensions:
        dimensions = image_dimensions(image_path)

    if not dimensions:
        logger.error('could not get dimensions from image')
    else:
        logger.info('identified dimensions width: {}px and height {}px'.format(
            dimensions[0], dimensions[1]))

    img_pattern = re.compile(
        r'\\(includegraphics{})'.format(image_relative_string))

    # when dimensions not empty and when image width less or equal 170
    if dimensions and check_convert_pixel(dimensions):
        img_replace = r'\\includegraphics[width={0}mm, height={1}mm]{2}'.format(
            pixeltomm(dimensions[0]), pixeltomm(dimensions[1]),
            image_relative_string)
    else:
        img_replace = r'\\includegraphics[width=0.95\\textwidth]{}'.format(
            image_relative_string)

    latex = re.sub(img_pattern, img_replace, latex)

    return latex


def iterate_image_strings(images, latex):
    for image in images:
        raw_image_url = image[1]
        logger.info('raw image url: {}'.format(raw_image_url))

        # TODO: need to prepend base url
        if not raw_image_url.startswith('http'):
            raw_image_url = raw_image_url

        image_source_path = extract_image_path(raw_image_url)

        image_target_path = file_path('/assets/{}{}'.format(
            file_name(image_source_path),
            file_extension(image_source_path)))

        logger.info('image source path: {}'.format(image_source_path))
        logger.info('image target path: {}'.format(image_target_path))

        resource = download(unquote(raw_image_url).replace('\\', ''))

        if resource:
            write_file(image_source_path, 'wb', resource)

        latex = replace_image(image_source_path, image_target_path,
                              raw_image_url, latex)

        logging.info(f'sequence run has finished returning\n')

    return latex


def convert_latex(target):
    subprocess.call('xelatex -interaction nonstopmode -output-directory {} {}'.format(
        file_path('/output'), file_path('/output/{}.tex'.format(target))),
        shell=True)


def replace_urls(url, latex):
    scheme = urlparse(url).scheme
    netloc = urlparse(url).netloc
    path = urlparse(url).path

    url = '{}://{}{}'.format(scheme, netloc, path)

    url_pattern = re.compile(r'(\/([a-zA-Z0-9\-\_]*\.[a-zA-Z0-9]*))$')
    base = re.sub(url_pattern, r'', url)

    logger.info('identified base url: {}'.format(base))

    href_pattern = re.compile(r'(\\href)\{((\/|\./)([a-zA-Z0-9\?\/\.\-=]*))\}')
    latex = re.sub(href_pattern, r'\1{{{}/\4}}'.format(base), latex)

    img_pattern = re.compile(
        r'(\\includegraphics)(\[[a-zA-Z0-9\\=,\s\.]*\])?\{((\/|\./)([a-zA-Z0-9\?\/\.\-=]*))\}')  # noqa: E501
    latex = re.sub(img_pattern, r'\1{{{}/\5}}'.format(base), latex)

    return latex


def main():
    args = argparser()

    source = args.input
    format = args.format

    makedir(file_path('/output'))
    makedir(file_path('/assets'))

    if args.format == 'gfm':
        resource = convert_other(source, 'html', format)
        source = file_path('/output/{}.html'.format(args.output))
        logger.info('writing {}'.format(source))
        write_file(source, 'w', resource)
    elif args.format == 'rst':
        resource = convert_other(source, 'md', format)
        source = file_path('/output/{}.md'.format(args.output))
        logger.info('writing {}'.format(source))
        write_file(source, 'w', resource)

    latex = convert_markdown(source, format)
    latex = replace_urls(args.input, latex)
    latex = replace_rule(latex)
    latex = replace_quote(latex)
    latex = replace_verbatim(latex)
    images = find_all_images(latex)

    latex = iterate_image_strings(images, latex)
    target = file_path('/output/{}.tex'.format(args.output))
    logger.info('writing {}'.format(target))
    write_file(target, 'w', latex)

    if not args.dry:
        convert_latex(args.output)


if __name__ == '__main__':
    main()
