#!/usr/bin/env python3

import re
import emoji
import argparse
import subprocess
import pypandoc
import logging
import random
import uuid

from urllib.parse import urlparse, unquote
from string import ascii_lowercase

from modules.utils.file_utils import (read_file, write_file, makedir,
                                      file_name, file_extension, file_path,
                                      file_type)

from modules.utils.image_utils import (download, pixeltomm, image_dimensions,
                                       convert_gif_image, convert_svg_image)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('converter')


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
    latex_header = read_file('header.tex')
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


def replace_unicode(latex):
    pattern = re.compile(r'([^\x00-\x7F])')
    items = re.findall(pattern, latex)
    unicode_chars = set()

    if len(items) > 0:
        logger.info('found unicodes: {}'.format(items))

    for item in items:
        unicodes = []

        for char in item:
            item_name = random_word()

            if not len(item) > 1:
                unicodes.append(r'{:x}'.format(ord(char)).upper())
                unicode_chars.add(
                    r'\\def\\{1}{{\\scalerel*{{\\includegraphics{{./fonts/{0}.pdf}}}}{{0}}}}'.format('-'.join(unicodes), item_name))  # noqa: E501
                latex = re.sub(
                    item, r'\\texorpdfstring{{\\large\\protect\\{0}}}{{}}'.format(item_name), latex)  # noqa: E501

    latex = re.sub(r'\\unicodechars\{\}', '\n'.join(unicode_chars), latex)

    return latex


def find_all_images(latex):
    img_url_pattern = re.compile(
        r'(\\includegraphics)(\[[a-zA-Z0-9\%\@\\=\,\s\.]*\])?\{((https?://)[a-zA-Z0-9\&\\%\@\?\/\.\-=]*)\}')  # noqa: E501

    images = re.findall(img_url_pattern, latex)

    return images


def extract_image_path(raw_image_url):
    image_file = urlparse(raw_image_url).path

    image_source_path = file_path('/assets/{}{}'.format(
        str(uuid.uuid4()), file_extension(image_file)))

    return image_source_path


def image_relative_data(image_source_path, image_target_path):
    allowed_file_types = ['image/gif', 'image/svg', 'image/svg+xml']

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
    svg_file_types = ['image/svg+xml', 'image/svg']
    dimensions = None

    image_target_path = file_path('/assets/{}.png'.format(
        file_name(image_target_path)))

    if file_type(image_source_path) in svg_file_types:
        dimensions = convert_svg_image(
            image_source_path, image_target_path)

    elif file_type(image_source_path) == 'image/gif':
        dimensions = convert_gif_image(
            image_source_path, image_target_path)

    return dimensions


def check_allowed_types(image_source_path, image_target_path, latex):
    allowed_file_types = ['image/svg+xml', 'image/svg', 'image/jpeg',
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
    allowed_file_types = ['image/svg+xml', 'image/svg', 'image/jpeg',
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
        r'(\\includegraphics)(\[[a-zA-Z0-9\@\\=,\s\.]*\])?({0})'.format(
            image_relative_string))

    if dimensions:
        img_replace = r'\\includegraphics[width={0}mm,height={1}mm]{2}'.format(
            pixeltomm(dimensions[0]),
            pixeltomm(dimensions[1]),
            image_relative_string)
    else:
        img_replace = r'\\includegraphics[width=9in,height=5in]{}'.format(
            image_relative_string)

    latex = re.sub(img_pattern, img_replace, latex)

    return latex


def iterate_image_strings(images, latex):
    for image in images:
        raw_image_url = image[2]
        logger.info('raw image url: {}'.format(raw_image_url))

        image_source_path = extract_image_path(raw_image_url)

        image_target_path = file_path('/assets/{}{}'.format(
            file_name(image_source_path),
            file_extension(image_source_path)))

        logger.info('image source path: {}'.format(image_source_path))
        logger.info('image target path: {}'.format(image_target_path))

        resource = download(unquote(raw_image_url).replace('\\', ''))

        if resource:
            logger.info('writing {}'.format(image_source_path))
            write_file(image_source_path, 'wb', resource)

        latex = replace_image(image_source_path, image_target_path,
                              raw_image_url, latex)

        logger.info('image sequence run has finished returning\n')

    return latex


def convert_latex(target):
    subprocess.call('xelatex -interaction nonstopmode -output-directory {} {}'.format(  # noqa: E501
        file_path('/output'), file_path('/output/{}.tex'.format(target))),
        shell=True)


def replace_urls(url, latex):
    scheme = urlparse(url).scheme
    netloc = urlparse(url).netloc
    path = urlparse(url).path

    url = '{}://{}{}'.format(scheme, netloc, path)

    url_pattern = re.compile(r'(\/([a-zA-Z0-9\@\-\_]*\.[a-zA-Z0-9]*))$')
    base = re.sub(url_pattern, r'', url)

    caption_pattern = re.compile(r'(\\caption)\{(.*)?\}')
    latex = re.sub(caption_pattern, '', latex)

    centering_pattern = re.compile(r'(\\centering)')
    latex = re.sub(centering_pattern, '', latex)

    text_pattern = re.compile(
        r'(\\texttt)\{(.*)?\}')
    latex = re.sub(text_pattern, r'\\hltt{\2}', latex)

    attr_pattern = re.compile(
        r'(\\includegraphics)(\[[a-zA-Z0-9\@\\=,\s\.]*\])?')
    latex = re.sub(attr_pattern, r'\1', latex)

    href_pattern = re.compile(
        r'(\\href)\{((\/|\./)([a-zA-Z0-9\@\?\/\.\-=]*))\}')
    latex = re.sub(href_pattern, r'\1{{{}/\4}}'.format(base), latex)

    img_pattern = re.compile(
        r'(\\includegraphics)(\[[a-zA-Z0-9\@\\=,\s\.]*\])?\{((?!https?)(\/|\.\/)?([a-zA-Z0-9\\&\@\?\/\.\-=]+))\}')  # noqa: E501
    latex = re.sub(img_pattern, r'\1{{{}/\5}}'.format(base), latex)

    logger.info('identified base url: {}'.format(base))

    return latex


def random_word():
    VOWELS = ['a', 'e', 'i', 'o', 'u']
    CONSONANTS = [c for c in ascii_lowercase if c not in VOWELS]

    random_range = random.randint(8, 12)
    word = ''

    for i in range(random_range):
        word += random.choice(VOWELS) + random.choice(CONSONANTS)
    return word


def _collect_emoji_chars():
    emoji_chars = set()

    emoji_data = getattr(emoji, 'EMOJI_DATA', None)
    if isinstance(emoji_data, dict):
        emoji_chars.update(emoji_data.keys())

    alias_maps = [
        getattr(emoji, attr, None)
        for attr in (
            'EMOJI_ALIAS_UNICODE_ENGLISH',
            'EMOJI_ALIAS_UNICODE',
            'EMOJI_UNICODE_ENGLISH',
            'EMOJI_UNICODE',
        )
    ]

    for mapping in alias_maps:
        if isinstance(mapping, dict):
            emoji_chars.update(mapping.values())

    return sorted(emoji_chars, key=len, reverse=True)


def replace_emoji(latex):
    emoji_chars = _collect_emoji_chars()
    if not emoji_chars:
        return latex

    unicode_chars = set()
    emojies = []

    emoji_pattern = re.compile('|'.join(
        re.escape(u) for u in emoji_chars))
    emojies = re.findall(emoji_pattern, latex)

    if len(emojies) > 0:
        logger.info('found emojies: {}'.format(emojies))

    for item in emojies:
        unicodes = []

        for char in item:
            item_name = random_word()

            if not len(item) > 1:
                unicodes.append(r'{:x}'.format(ord(char)).upper())
                unicode_chars.add(
                    r'\\def\\{1}{{\\scalerel*{{\\includegraphics{{./emojies/{0}.pdf}}}}{{0}}}}'.format('-'.join(unicodes), item_name))  # noqa: E501
                latex = re.sub(
                    item, r'\\texorpdfstring{{\\large\\protect\\{0}}}{{}}'.format(item_name), latex)  # noqa: E501

    latex = re.sub(r'\\newunicodechar\{\}', '\n'.join(unicode_chars), latex)

    return latex


def initialize():
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
    latex = replace_emoji(latex)
    latex = replace_quote(latex)
    latex = replace_unicode(latex)
    latex = replace_verbatim(latex)
    images = find_all_images(latex)

    latex = iterate_image_strings(images, latex)
    target = file_path('/output/{}.tex'.format(args.output))
    logger.info('writing {}'.format(target))
    write_file(target, 'w', latex)

    if not args.dry:
        convert_latex(args.output)
