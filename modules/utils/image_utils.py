#!/usr/bin/env python3

import gi
import math
import cairo
import requests
import logging

from PIL import Image, UnidentifiedImageError
from requests.exceptions import ConnectionError, HTTPError
from gi.repository.GLib import Error

gi.require_version('Rsvg', '2.0')

from gi.repository import Rsvg  # noqa: E402


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('converter')


def download(u):
    res = requests.get(u, timeout=1)

    try:
        res.raise_for_status()
    except HTTPError as e:
        logger.error(e)
        return None
    except ConnectionError as e:
        logger.error(e)
        return None

    return res.content


def pixeltomm(p):
    value = math.floor(p * 25.4) / 112

    return value


def image_open(p):
    try:
        image = Image.open(p)
    except FileNotFoundError as e:
        logger.error(e)
        return None
    except UnidentifiedImageError as e:
        logger.error(e)
        return None

    return image


def image_dimensions(p):
    image = image_open(p)
    maxwidth = 782
    maxheight = 567

    if not image:
        return None

    width, height = image.size

    if width >= maxwidth:
        ratio = min(maxwidth / width, maxheight / height)
        width = width * ratio
        height = height * ratio

    dimensions = [width, height]

    return dimensions


def convert_gif_image(p, o):
    image = image_open(p)

    if not image:
        return None

    logger.info('writing png file {}'.format(o))

    if image.is_animated:
        logger.info('gif image has {} animated frames'.format(image.n_frames))

        image.seek(image.n_frames - 1)
        image.save(o, 'PNG')
    else:
        image.save(o, 'PNG')

    dimensions = image_dimensions(o)

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

    svg_surface = cairo.SVGSurface(None, width * 2, height * 2)
    svg_context = cairo.Context(svg_surface)
    svg_context.scale(2, 2)
    svg.render_cairo(svg_context)
    svg_surface.write_to_png(o)

    dimensions = image_dimensions(o)
    dimensions = [dimensions[0] / 2, dimensions[1] / 2]

    return dimensions
