#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020 Pradyumna Paranjape
# This file is part of psprint.
#
# psprint is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# psprint is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with psprint.  If not, see <https://www.gnu.org/licenses/>.
#
'''
Information- Prepended Print object
'''

from sys import stdout
from types import GeneratorType
from typing import Dict, List, Optional, Tuple, Union

from .ansi import ANSI
from .errors import BadMark
from .mark_types import InfoMark


class PrintSpace():
    """
    Fancy Print class that also prints the type of message

    Args:
        conf: parsed configuration
        name: name of configuration file (to report errors)

    Attributes:
        pref_max: int: maximum length of prefix string
        info_style; dict: pre-configured prefix styles
        info_index: list: keys of `info_style` mapped to int
        print_kwargs: dict : library of kwargs_accepted by print_function
        switches: dict: user-customizations: pad, short, bland, disabled

            pad: bool: prefix is padded to start text at the same level
            short: bool: display short, 1 character- prefix
            bland: bool: do not show ANSI color/styles for prefix/text
            disabled: bool: behave like python default print_function

    """
    def __init__(self,
                 conf: Dict[str, dict] = None,
                 /,
                 name: str = None) -> None:
        # Standard info styles
        self.switches = {
            'pad': False,
            'short': False,
            'bland': False,
            'disabled': False
        }
        self.print_kwargs = {
            'file': stdout,
            'sep': "\t",
            'end': "\n",
            'flush': False
        }
        self.pref_max = None
        self.info_style: Dict[str, InfoMark] = {}
        self.info_index: List[str] = []
        if conf is not None:
            self.set_opts(conf, name or 'unnamed config file')

    def __repr__(self) -> str:
        """
        Returns:
            Formatted summary of info_style
        """
        outstr = '\npref\tlong\tshort\ttext\n\n'
        outstr += "\n".join((f"{k}:{v}" for k, v in self.info_style.items()))
        return outstr

    def __contains__(self, mark: Union[str, InfoMark]) -> bool:
        """
        is mark defined?
        """
        if isinstance(mark, str):
            return mark in self.info_style.keys()
        return mark in self.info_style.values()

    def __getitem__(self, mark: Union[int, str]) -> InfoMark:
        """
        Returns:
            Infomark corresponding to mark
        """
        if isinstance(mark, str):
            return self.info_style[mark]
        if isinstance(mark, int):
            if not 0 <= mark < len(self.info_index):
                mark = 0
            return self.info_style[self.info_index[mark]]
        raise KeyError(mark)

    def set_opts(self, conf: Dict[str, dict], /, name: str) -> None:
        """
        configuration from rcfile

        Args:
            conf: parsed configuration
            name: name of configuration file (to report errors)

        Raises:
            BadMark

        """
        if not conf:
            return
        info_index: Optional[Dict[str, str]] = None
        for mark, settings in conf.items():
            if mark == "FLAGS":
                # switches / flags
                self.pref_max = settings.get("pref_max", None)

                # update psprint switches
                self.switches.update(
                    dict(
                        filter(lambda x: x[0] in self.switches,
                               settings.items())))

                # update __builtin__,print kwargs
                self.print_kwargs.update(
                    dict(filter(lambda x: x[0] in self.print_kwargs,
                                settings)))

                # standard output file
                fname = settings.get("file", None)  # Discouraged
                if fname is not None:  # pragma: no cover
                    self.print_kwargs['file'] = open(fname, "a")

            elif mark == 'order':
                info_index = settings
            else:
                # New mark definition
                try:
                    self.edit_style(mark=mark, **settings)
                except (ValueError, TypeError):  # pragma: no cover
                    raise BadMark(str(mark), name) from None
        if info_index is not None:
            self.info_index = list(
                filter(lambda x: x in self.info_style, info_index))

    def edit_style(self,
                   pref: str,
                   index_int: int = None,
                   mark: str = None,
                   **kwargs) -> str:
        """
        Edit loaded style

        Args:
            pref: str: prefix string long [length < 10 characters]
            index_int: Index number that will call this InfoMark
            mark: Mark string that will call this ``InfoMark``
            **kwargs:
                * pref_s: str: prefix string short [1 character]
                * code:

                    * color: {[0-15],[[l]krgybmcw],[[light] <color_name>]}
                    * gloss: {[0-3],[rcdb],{reset,normal,dim,bright}}

                * for-

                    * pref_color: color of of prefix
                    * pref_gloss: gloss of prefix
                    * pref_bgcol: background color of prefix
                    * text_color: color of of text
                    * text_gloss: gloss of text
                    * text_bgcol: background color of text

        Returns
            Summary of new (updated) ``PrintSpace``

        """
        # correct pref
        if mark is None:
            mark = pref[:4]
        kwargs['pref'] = pref
        if index_int is None or \
           not 0 <= index_int <= len(self.info_index):
            self.info_index.append(mark)
        else:
            self.info_index.insert(index_int, mark)
        self.info_style[mark] = InfoMark(pref_max=self.pref_max, **kwargs)
        return str(self)

    def remove_style(self, mark: str = None, index_int: int = None) -> str:
        """
        Args:
            mark: is popped out of defined styles
            index_int: is used to locate index_str if it is not provided

        Returns
            Summary of new (updated) ``PrintSpace``

        """
        if mark is None:
            if index_int is not None:
                if index_int < len(self.info_style):
                    mark = self.info_index.pop(index_int)
        if mark is None:
            raise SyntaxError('''
            At least one of ``mark`` and ``index_int`` should be provided
            ''')
        del self.info_style[mark]
        return str(self)

    def _which_mark(self,
                    mark: Union[str, int, InfoMark] = None,
                    **kwargs) -> InfoMark:
        """
        Define a mark based on arguments supplied

            * may be a pre-defined mark OR
            * mark defined on the fly

        Args:
            mark: mark that identifies a defined prefix
            **kwargs:
                * pref: str: prefix string long [length < 10 characters]
                * pref_s: str: prefix string short [1 character]
                * code:

                    * color: {[0-15],[[l]krgybmcw],[[light] <color_name>]}
                    * gloss: {[0-3],[rcdb],{reset,normal,dim,bright}}

                * for-

                    * pref_color: color of of prefix
                    * pref_gloss: gloss of prefix
                    * pref_bgcol: background color of prefix
                    * text_color: color of of text
                    * text_gloss: gloss of text
                    * text_bgcol: background color of text

        """
        base_mark: InfoMark = self.info_style['cont']
        if mark is not None:
            # mark was supplied
            if isinstance(mark, InfoMark):
                # ready-made mark was served
                base_mark = mark
            elif isinstance(mark, (str, int)):
                # mark supplied as index int
                base_mark = self[mark]
            else:
                raise BadMark(mark=str(mark), config="**kwargs")
        if any(arg in kwargs for arg in [
                'pref',
                'pref_s',
                'pref_color',
                'pref_gloss',
                'pref_bgcol',
                'text_color',
                'text_gloss',
                'text_bgcol',
        ]):
            return InfoMark(parent=base_mark, pref_max=self.pref_max, **kwargs)
        return base_mark

    def _iter_print(self,
                    args,
                    mark: Union[str, int, InfoMark] = None,
                    **kwargs):
        itertag = {
            GeneratorType: 'generator:',
            list: 'list:',
            dict: 'dict:',
            tuple: 'tuple:'
        }
        self.psprint(itertag[type(args)], mark=mark, **kwargs)
        if isinstance(args, (list, tuple, GeneratorType)):
            # make this more general
            args = {index: value for index, value in enumerate(args)}
        if 'pref' in kwargs:
            del kwargs['pref']
        kwargs['indent'] = kwargs.get('indent', 0) + 1
        for key, value in args.items():
            self.psprint(value, mark='list', pref=key, **kwargs)

    def psfmt(self,
              *args,
              mark: Union[str, int, InfoMark] = None,
              sep: str = None,
              **kwargs) -> Union[List[str], str]:
        """
        Prefix String represenattion.

        Args:
            *args: passed to print_function for printing
            mark: pre-configured `InfoMark` defaults:

                * cont or 0 or anything else: nothing
                * info or 1: [INFO]
                * act  or 2: [ACTION]
                * list or 3: [LIST]
                * warn or 4: [WARNING]
                * error:or 5: [ERROR]
                * bug:  or 6 [DEBUG]
                * `Other marks defined in .psprintrc`

            sep: If not ``None``, return `*args` joined by separator.

            **kwargs:
                * pref: str: prefix string long [length < 10 characters]
                * pref_s: str: prefix string short [1 character]
                * code:

                    * color: {[0-15],[[l]krgybmcw],[[light] <color_name>]}
                    * gloss: {[0-3],[rcdb],{reset,normal,dim,bright}}

                * for-

                    * pref_color: color of of prefix
                    * pref_gloss: gloss of prefix
                    * pref_bgcol: background color of prefix
                    * text_color: color of of text
                    * text_gloss: gloss of text
                    * text_bgcol: background color of text

                * pad: bool: prefix is padded to start text at the same level
                * short: bool: display short, 1 character- prefix
                * bland: bool: do not show ANSI color/styles for prefix/text
                * disabled: bool: behave like python default print_function

        Raises:

            BadMark: mark couldn't be interpreted

        Returns:

            * PSPRINT-like represented args. When `these` args is printed
              using standard print, PSPRINT-like output appears.
            * If a sep is provided, it is used to join args and return a string

        """
        switches = {
            key: {
                **self.switches,
                **kwargs
            }[key]
            for key in self.switches
        }

        args_l = list('  ' * kwargs.get('indent', 0) + str(arg)
                      for arg in args)  # typecast
        if switches['disabled'] or not args:
            if sep is not None:
                return sep.join(args_l)
            return args_l

        mark = self._which_mark(mark=mark, **kwargs)

        # add prefix to *args[0]
        if not switches.get('bland'):  # pragma: no cover
            args_l[0] = str(mark.text) + str(args_l[0])
            args_l[-1] = str(args_l[-1]) + ANSI.RESET_ALL
        args_l[0] = mark.pref.to_str(**switches) + str(args_l[0])
        if sep is not None:
            return sep.join(args_l)
        return args_l

    def psprint(self,
                *args,
                mark: Union[str, int, InfoMark] = None,
                **kwargs) -> None:
        """
        Prefix String PRINT

        - Iterates through if the only argument supplied is

          - ``GeneratorType``
          - ``tuple``
          - ``list``
          - ``dict``

        Args:
            *args: passed to print_function for printing
            mark: pre-configured `InfoMark` defaults:

                * cont or 0 or anything else: nothing
                * info or 1: [INFO]
                * act  or 2: [ACTION]
                * list or 3: [LIST]
                * warn or 4: [WARNING]
                * error:or 5: [ERROR]
                * bug:  or 6 [DEBUG]
                * `Other marks defined in .psprintrc`

            **kwargs:
                * pref: str: prefix string long [length < ``pref_max``]
                * pref_s: str: prefix string short [1 character]
                * code:

                    * color: {[0-15],[[l]krgybmcw],[[light] <color_name>]}
                    * gloss: {[0-3],[rcdb],{reset,normal,dim,bright}}

                * for-

                    * pref_color: color of of prefix
                    * pref_gloss: gloss of prefix
                    * pref_bgcol: background color of prefix
                    * text_color: color of of text
                    * text_gloss: gloss of text
                    * text_bgcol: background color of text

                * pad: bool: prefix is padded to start text at the same level
                * short: bool: display short, 1 character- prefix
                * bland: bool: do not show ANSI color/styles for prefix/text
                * disabled: bool: behave like python default print_function
                * indent: indent level of print statement
                * file: IO: passed to print function
                * sep: str: passed to print function
                * end: str: passed to print function
                * flush: bool: passed to print function

        Raises:
            BadMark: mark couldn't be interpreted

        """
        # Extract print-kwargs
        print_kwargs = {
            key: {
                **self.print_kwargs,
                **kwargs
            }[key]
            for key in self.print_kwargs
        }

        if len(args) == 1 and isinstance(args[0],
                                         (dict, GeneratorType, list, tuple)):
            self._iter_print(args[0], mark=mark, **kwargs)
        else:
            print(*self.psfmt(*args, mark=mark, **kwargs), **print_kwargs)
