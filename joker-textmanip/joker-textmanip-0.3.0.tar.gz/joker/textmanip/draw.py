#!/usr/bin/env python3
# coding: utf-8


def make_title_box(title, comment='#', width=50):
    """
    # +--------------------------------------------------+
    # |                                                  |
    # |                  Title is here                   |
    # |                                                  |
    # +--------------------------------------------------+
    """
    lines = list()
    lines.append('+{}+'.format('-' * width))
    lines.append('|{}|'.format(' ' * width))
    lines.append('|{}|'.format(title.center(width)))
    lines.append('|{}|'.format(' ' * width))
    lines.append('+{}+'.format('-' * width))
    return ['{} {}'.format(comment, s) for s in lines]


def mkbox(prog, args):
    import argparse
    desc = 'draw title box'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    aa = parser.add_argument
    aa('-c', '--comment', default='#', metavar='SYMBOL',
       help='comment symbol, e.g. # or //')
    aa('-w', '--width', type=int, default=50, help='width of the box')
    aa('title', nargs='?', default='Welcome', help='text in the box')
    aa('title_words', nargs='*', help=argparse.SUPPRESS)
    ns = parser.parse_args(args)
    title = ' '.join([ns.title] + ns.title_words)
    for line in make_title_box(title, ns.comment, ns.width):
        print(line)

