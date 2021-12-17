"""
Here is where we will keep a few things that will make printing stuff out
on a terminal a bit nicer.
"""


class TermColor(object):
    color_codes = {'purple': '\033[95m',
                   'cyan': '\033[96m',
                   'darkcyan': '\033[36m',
                   'blue': '\033[94m',
                   'green': '\033[92m',
                   'yellow': '\033[93m',
                   'red': '\033[91m',
                   'bold': '\033[1m',
                   'underline': '\033[4m',
                   'end': '\033[0m'}

    @classmethod
    def change(cls, str_in, color):
        """
        Surround our string with terminal codes that will change its
        color and then change it back
        """
        return '{}{}{}'.format(cls.color_codes[color.lower()], str_in,
                               cls.color_codes['end'])
