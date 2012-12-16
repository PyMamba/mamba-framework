# -*- test-case-name: mamba.utils.test.test_output -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# Ses LICENSE for more details

"""
.. module:: output
    :platform: Unix, Windows
    :synopsys: Output facilities, inspired on Gentoo portage

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

havecolor = 1

esc_seq = '\x1b['

codes = {
    'normal': '{}0m'.format(esc_seq),
    'reset': '{}39;49;00m'.format(esc_seq),
    'bold': '{}01m'.format(esc_seq),
    'underline': '{}04m'.format(esc_seq),
    'overline': '{}06m'.format(esc_seq)
}

# Colors from /etc/init.d/functions.sh
_styles = {
    'NORMAL': ('normal',),
    'GOOD': ('green',),
    'WARN': ('yellow',),
    'BAD': ('red',),
    'HILITE': ('teal',),
    'BRACKET': ('blue',)
}

ansi_codes = []
for x in xrange(30, 38):
    ansi_codes.append('%im' % x)
    ansi_codes.append('%i;01m' % x)

rgb_ansi_colors = [
    '0x000000', '0x555555', '0xAA0000', '0xFF5555', '0x00AA00',
    '0x55FF55', '0xAA5500', '0xFFFF55', '0x0000AA', '0x5555FF',
    '0xAA00AA', '0xFF55FF', '0x00AAAA', '0x55FFFF', '0xAAAAAA',
    '0xFFFFFF'
]

for x in xrange(len(rgb_ansi_colors)):
    codes[rgb_ansi_colors[x]] = '{}{}'.format(esc_seq, ansi_codes[x])

codes.update({
    'black': codes['0x000000'],
    'darkgray': codes['0x555555'],
    'red': codes['0xFF5555'],
    'darkred': codes['0xAA0000'],
    'green': codes['0x55FF55'],
    'darkgreen': codes['0x00AA00'],
    'yellow': codes['0xFFFF55'],
    'brown': codes['0xAA5500'],
    'blue': codes['0x5555FF'],
    'darkblue': codes['0x0000AA'],
    'fuchsia': codes['0xFF55FF'],
    'purple': codes['0xAA00AA'],
    'turquoise': codes['0x55FFFF'],
    'teal': codes['0x00AAAA'],
    'white': codes['0xFFFFFF'],
    'lightgray': codes['0xAAAAAA']
})

codes.update({
    'darkteal': codes['turquoise'],
    # Some terminals have darkyellow instead of brown.
    'darkyellow': codes['brown']
})


def resetColor():
    return codes.get('reset')


def style_to_ansi_code(style):
    """
    :param style: A style name
    :type style: string
    :returns: A string containing one or more ansi escape codes that are
              used to render the given style.
    :type return: string
    """
    ret = ''
    for attr_name in _styles[style]:
        # allow stuff that has found it's way through ansi_code_pattern
        ret += codes.get(attr_name, attr_name)

    return ret


def colorize(color_key, text):
    global havecolor
    if havecolor:
        if color_key in codes:
            return codes[color_key] + text + codes['reset']
        elif color_key in _styles:
            return style_to_ansi_code(color_key) + text + codes['reset']
        else:
            return text
    else:
        return text


def create_color_func(color):
    def closure(*args):
        newargs = [color] + list(args)
        return colorize(*newargs)

    return closure


for color, value in codes.iteritems():
    if color in ['normal', 'reset', 'underline', 'overline']:
        continue

    globals()[color] = create_color_func(color)
