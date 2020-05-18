#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

import os
import pathlib

from PyPDF2 import PdfFileMerger


def merge_pdf():
    cwd = pathlib.Path.cwd()
    paths = []
    pdfs = []

    for root, dirs, files in os.walk('{}/fonts'.format(cwd)):
        for name in files:
            source = os.path.join(root, name)

            if source.split('.')[1] == 'pdf':
                pdfs.append(source)

    amount = 500
    counter = 0

    steps = int(len(pdfs) / amount)

    for step in range(0, steps):
        end = step * amount + amount
        start = len(pdfs[:end - amount])

        if step == steps - 1:
            paths.append(pdfs[start:])
        else:
            paths.append(pdfs[start:end])

        merger = PdfFileMerger()

        for index, path in enumerate(paths[step]):
            merger.append(path)
            print(index + counter, path)

        counter = counter + index

        merger.write('step-{}.pdf'.format(step))
        merger.close()


if __name__ == '__main__':
    merge_pdf()
