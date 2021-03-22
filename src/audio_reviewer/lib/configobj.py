# encoding=utf-8
# configobj.py
# A config file reader/writer that supports nested sections in config files.
# Copyright (C) 2005-2006 Michael Foord, Nicola Larosa
# ConfigObj 4
# http://www.voidspace.org.uk/python/configobj.html
# This file is a "ripped" version, created specifically for this project. The  
# required Validator from validate.py has been copied and pasted here to remove
# the need for any non-builtin imports.  Additionally, comments (while
# excellent, and done correctly for once) are VERY long, and are being removed
# to reduce disk-space.  To view the comments, please find ConfigObj version 4
# from the link above, or just Google "Python ConfigObj."
# Released subject to the BSD License
# Please see http://www.voidspace.org.uk/python/license.shtml

import sys
import datetime
INTP_VER = sys.version_info[:2]
if INTP_VER < (2, 2):
    raise RuntimeError("Python v.2.2 or later needed")

import os, re
import compiler
from types import StringTypes
from warnings import warn
from codecs import BOM_UTF8, BOM_UTF16, BOM_UTF16_BE, BOM_UTF16_LE

# A dictionary mapping BOM to
# the encoding to decode with, and what to set the
# encoding attribute to.
BOMS = {
    BOM_UTF8: ('utf_8', None),
    BOM_UTF16_BE: ('utf16_be', 'utf_16'),
    BOM_UTF16_LE: ('utf16_le', 'utf_16'),
    BOM_UTF16: ('utf_16', 'utf_16'),
    }
# All legal variants of the BOM codecs.
# TODO-IGNORED: the list of aliases is not meant to be exhaustive, is there a
#   better way ?
BOM_LIST = {
    'utf_16': 'utf_16',
    'u16': 'utf_16',
    'utf16': 'utf_16',
    'utf-16': 'utf_16',
    'utf16_be': 'utf16_be',
    'utf_16_be': 'utf16_be',
    'utf-16be': 'utf16_be',
    'utf16_le': 'utf16_le',
    'utf_16_le': 'utf16_le',
    'utf-16le': 'utf16_le',
    'utf_8': 'utf_8',
    'u8': 'utf_8',
    'utf': 'utf_8',
    'utf8': 'utf_8',
    'utf-8': 'utf_8',
    }

# Map of encodings to the BOM to write.
BOM_SET = {
    'utf_8': BOM_UTF8,
    'utf_16': BOM_UTF16,
    'utf16_be': BOM_UTF16_BE,
    'utf16_le': BOM_UTF16_LE,
    None: BOM_UTF8
    }

# -- FINDME INSERTED HERE FINDME

StringTypes = (str, unicode)


_list_arg = re.compile(r'''
    (?:
        ([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*list\(
            (
                (?:
                    \s*
                    (?:
                        (?:".*?")|              # double quotes
                        (?:'.*?')|              # single quotes
                        (?:[^'",\s\)][^,\)]*?)  # unquoted
                    )
                    \s*,\s*
                )*
                (?:
                    (?:".*?")|              # double quotes
                    (?:'.*?')|              # single quotes
                    (?:[^'",\s\)][^,\)]*?)  # unquoted
                )?                          # last one
            )
        \)
    )
''', re.VERBOSE)    # two groups

_list_members = re.compile(r'''
    (
        (?:".*?")|              # double quotes
        (?:'.*?')|              # single quotes
        (?:[^'",\s=][^,=]*?)       # unquoted
    )
    (?:
    (?:\s*,\s*)|(?:\s*$)            # comma
    )
''', re.VERBOSE)    # one group

_paramstring = r'''
    (?:
        (
            (?:
                [a-zA-Z_][a-zA-Z0-9_]*\s*=\s*list\(
                    (?:
                        \s*
                        (?:
                            (?:".*?")|              # double quotes
                            (?:'.*?')|              # single quotes
                            (?:[^'",\s\)][^,\)]*?)       # unquoted
                        )
                        \s*,\s*
                    )*
                    (?:
                        (?:".*?")|              # double quotes
                        (?:'.*?')|              # single quotes
                        (?:[^'",\s\)][^,\)]*?)       # unquoted
                    )?                              # last one
                \)
            )|
            (?:
                (?:".*?")|              # double quotes
                (?:'.*?')|              # single quotes
                (?:[^'",\s=][^,=]*?)|       # unquoted
                (?:                         # keyword argument
                    [a-zA-Z_][a-zA-Z0-9_]*\s*=\s*
                    (?:
                        (?:".*?")|              # double quotes
                        (?:'.*?')|              # single quotes
                        (?:[^'",\s=][^,=]*?)       # unquoted
                    )
                )
            )
        )
        (?:
            (?:\s*,\s*)|(?:\s*$)            # comma
        )
    )
    '''

_matchstring = '^%s*' % _paramstring

# Python pre 2.2.1 doesn't have bool
try:
    bool
except NameError:
    def bool(val):
        if val:
            return 1
        else:
            return 0

def dottedQuadToNum(ip):
    # import here to avoid it when ip_addr values are not used
    import socket, struct
    
    try:
        return struct.unpack('!L',
            socket.inet_aton(ip.strip()))[0]
    except socket.error:
        # bug in inet_aton, corrected in Python 2.3
        if ip.strip() == '255.255.255.255':
            return 0xFFFFFFFFL
        else:
            raise ValueError('Not a good dotted-quad IP: %s' % ip)
    return

def numToDottedQuad(num):
    # import here to avoid it when ip_addr values are not used
    import socket, struct
    
    # no need to intercept here, 4294967295L is fine
    try:
        return socket.inet_ntoa(
            struct.pack('!L', long(num)))
    except (socket.error, struct.error, OverflowError):
        raise ValueError('Not a good numeric IP: %s' % num)

class ValidateError(Exception): pass
class VdtMissingValue(ValidateError): pass

class VdtUnknownCheckError(ValidateError):

    def __init__(self, value):
        ValidateError.__init__(
            self,
            'the check "%s" is unknown.' % value)

class VdtParamError(SyntaxError):

    def __init__(self, name, value):
        SyntaxError.__init__(
            self,
            'passed an incorrect value "%s" for parameter "%s".' % (
                value, name))

class VdtTypeError(ValidateError):

    def __init__(self, value):
        ValidateError.__init__(
            self,
            'the value "%s" is of the wrong type.' % value)

class VdtValueError(ValidateError):

    def __init__(self, value):
        ValidateError.__init__(
            self,
            'the value "%s" is unacceptable.' % value)

class VdtValueTooSmallError(VdtValueError):

    def __init__(self, value):
        ValidateError.__init__(
            self,
            'the value "%s" is too small.' % value)

class VdtValueTooBigError(VdtValueError):

    def __init__(self, value):
        ValidateError.__init__(
            self,
            'the value "%s" is too big.' % value)

class VdtValueTooShortError(VdtValueError):

    def __init__(self, value):
        ValidateError.__init__(
            self,
            'the value "%s" is too short.' % (value,))

class VdtValueTooLongError(VdtValueError):

    def __init__(self, value):
        ValidateError.__init__(
            self,
            'the value "%s" is too long.' %  (value,))

class Validator(object):

    # this regex does the initial parsing of the checks
    _func_re = re.compile(r'(.+?)\((.*)\)')

    # this regex takes apart keyword arguments
    _key_arg = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)$')


    # this regex finds keyword=list(....) type values
    _list_arg = _list_arg

    # this regex takes individual values out of lists - in one pass
    _list_members = _list_members

    # These regexes check a set of arguments for validity
    # and then pull the members out
    _paramfinder = re.compile(_paramstring, re.VERBOSE)
    _matchfinder = re.compile(_matchstring, re.VERBOSE)


    def __init__(self, functions=None):
        self.functions = {
            '': self._pass,
            'integer': is_integer,
            'float': is_float,
            'boolean': is_bool,
            'ip_addr': is_ip_addr,
            'string': is_string,
            'list': is_list,
            'int_list': is_int_list,
            'float_list': is_float_list,
            'bool_list': is_bool_list,
            'ip_addr_list': is_ip_addr_list,
            'string_list': is_string_list,
            'mixed_list': is_mixed_list,
            'pass': self._pass,
            'option': is_option,
        }
        if functions is not None:
            self.functions.update(functions)
        # tekNico: for use by ConfigObj
        self.baseErrorClass = ValidateError

    def check(self, check, value, missing=False):
        fun_match = self._func_re.match(check)
        if fun_match:
            fun_name = fun_match.group(1)
            arg_string = fun_match.group(2)
            arg_match = self._matchfinder.match(arg_string)
            if arg_match is None:
                # Bad syntax
                raise VdtParamError
            fun_args = []
            fun_kwargs = {}
            # pull out args of group 2
            for arg in self._paramfinder.findall(arg_string):
                # args may need whitespace removing (before removing quotes)
                arg = arg.strip()
                listmatch = self._list_arg.match(arg)
                if listmatch:
                    key, val = self._list_handle(listmatch)
                    fun_kwargs[key] = val
                    continue
                keymatch = self._key_arg.match(arg)
                if keymatch:
                    val = self._unquote(keymatch.group(2))
                    fun_kwargs[keymatch.group(1)] = val
                    continue
                #
                fun_args.append(self._unquote(arg))
        else:
            # allows for function names without (args)
            (fun_name, fun_args, fun_kwargs) = (check, (), {})
        #
        if missing:
            try:
                value = fun_kwargs['default']
            except KeyError:
                raise VdtMissingValue
            if value == 'None':
                value = None
        if value is None:
            return None
# tekNico: default must be deleted if the value is specified too,
# otherwise the check function will get a spurious "default" keyword arg
        try:
            del fun_kwargs['default']
        except KeyError:
            pass
        try:
            fun = self.functions[fun_name]
        except KeyError:
            raise VdtUnknownCheckError(fun_name)
        else:
            return fun(value, *fun_args, **fun_kwargs)

    def _unquote(self, val):
        if (len(val) > 2) and (val[0] in ("'", '"')) and (val[0] == val[-1]):
            val = val[1:-1]
        return val

    def _list_handle(self, listmatch):
        out = []
        name = listmatch.group(1)
        args = listmatch.group(2)
        for arg in self._list_members.findall(args):
            out.append(self._unquote(arg))
        return name, out

    def _pass(self, value):
        return value


def _is_num_param(names, values, to_float=False):
    fun = to_float and float or int
    out_params = []
    for (name, val) in zip(names, values):
        if val is None:
            out_params.append(val)
        elif isinstance(val, (int, long, float, StringTypes)):
            try:
                out_params.append(fun(val))
            except ValueError, e:
                raise VdtParamError(name, val)
        else:
            raise VdtParamError(name, val)
    return out_params

# built in checks
# you can override these by setting the appropriate name
# in Validator.functions
# note: if the params are specified wrongly in your input string,
#       you will also raise errors.

def is_integer(value, min=None, max=None):

    (min_val, max_val) = _is_num_param(('min', 'max'), (min, max))
    if not isinstance(value, (int, long, StringTypes)):
        raise VdtTypeError(value)
    if isinstance(value, StringTypes):
        # if it's a string - does it represent an integer ?
        try:
            value = int(value)
        except ValueError:
            raise VdtTypeError(value)
    if (min_val is not None) and (value < min_val):
        raise VdtValueTooSmallError(value)
    if (max_val is not None) and (value > max_val):
        raise VdtValueTooBigError(value)
    return value

def is_float(value, min=None, max=None):
    (min_val, max_val) = _is_num_param(
        ('min', 'max'), (min, max), to_float=True)
    if not isinstance(value, (int, long, float, StringTypes)):
        raise VdtTypeError(value)
    if not isinstance(value, float):
        # if it's a string - does it represent a float ?
        try:
            value = float(value)
        except ValueError:
            raise VdtTypeError(value)
    if (min_val is not None) and (value < min_val):
        raise VdtValueTooSmallError(value)
    if (max_val is not None) and (value > max_val):
        raise VdtValueTooBigError(value)
    return value

bool_dict = {
    True: True, 'on': True, '1': True, 'true': True, 'yes': True, 
    False: False, 'off': False, '0': False, 'false': False, 'no': False,
}

def is_bool(value):
    if isinstance(value, StringTypes):
        try:
            return bool_dict[value.lower()]
        except KeyError:
            raise VdtTypeError(value)
    # we do an equality test rather than an identity test
    # this ensures Python 2.2 compatibilty
    # and allows 0 and 1 to represent True and False
    if value == False:
        return False
    elif value == True:
        return True
    else:
        raise VdtTypeError(value)


def is_ip_addr(value):
    if not isinstance(value, StringTypes):
        raise VdtTypeError(value)
    value = value.strip()
    try:
        dottedQuadToNum(value)
    except ValueError:
        raise VdtValueError(value)
    return value

def is_list(value, min=None, max=None):
    (min_len, max_len) = _is_num_param(('min', 'max'), (min, max))
    try:
        num_members = len(value)
    except TypeError:
        raise VdtTypeError(value)
    if min_len is not None and num_members < min_len:
        raise VdtValueTooShortError(value)
    if max_len is not None and num_members > max_len:
        raise VdtValueTooLongError(value)
    return value

def is_string(value, min=None, max=None):
    if not isinstance(value, StringTypes):
        raise VdtTypeError(value)
    (min_len, max_len) = _is_num_param(('min', 'max'), (min, max))
    try:
        num_members = len(value)
    except TypeError:
        raise VdtTypeError(value)
    if min_len is not None and num_members < min_len:
        raise VdtValueTooShortError(value)
    if max_len is not None and num_members > max_len:
        raise VdtValueTooLongError(value)
    return value

def is_int_list(value, min=None, max=None):
    return [is_integer(mem) for mem in is_list(value, min, max)]

def is_bool_list(value, min=None, max=None):
    return [is_bool(mem) for mem in is_list(value, min, max)]

def is_float_list(value, min=None, max=None):
    return [is_float(mem) for mem in is_list(value, min, max)]

def is_string_list(value, min=None, max=None):
    if isinstance(value, StringTypes):
        raise VdtTypeError(value)
    return [is_string(mem) for mem in is_list(value, min, max)]

def is_ip_addr_list(value, min=None, max=None):
    return [is_ip_addr(mem) for mem in is_list(value, min, max)]

fun_dict = {
    'integer': is_integer,
    'float': is_float,
    'ip_addr': is_ip_addr,
    'string': is_string,
    'boolean': is_bool,
}

def is_mixed_list(value, *args):
    try:
        length = len(value)
    except TypeError:
        raise VdtTypeError(value)
    if length < len(args):
        raise VdtValueTooShortError(value)
    elif length > len(args):
        raise VdtValueTooLongError(value)
    try:
        return [fun_dict[arg](val) for arg, val in zip(args, value)]
    except KeyError, e:
        raise VdtParamError('mixed_list', e)

def is_option(value, *options):
    if not isinstance(value, StringTypes):
        raise VdtTypeError(value)
    if not value in options:
        raise VdtValueError(value)
    return value

def _test(value, *args, **keywargs):
    return (value, args, keywargs)

# -- FINDME INSERTED HERE FINDME

try:
    enumerate
except NameError:
    def enumerate(obj):
        i = -1
        for item in obj:
            i += 1
            yield i, item

#try:
#    True, False
#except NameError:
#    True, False = 1, 0


__version__ = '4.3.2'

__revision__ = '$Id: configobj.py 156 2006-01-31 14:57:08Z fuzzyman $'

__docformat__ = "restructuredtext en"

# NOTE: Does it make sense to have the following in __all__ ?
# NOTE: DEFAULT_INDENT_TYPE, NUM_INDENT_SPACES, MAX_INTERPOL_DEPTH
# NOTE: If used via ``from configobj import...``
# NOTE: They are effectively read only
__all__ = (
    '__version__',
    'DEFAULT_INDENT_TYPE',
    'NUM_INDENT_SPACES',
    'MAX_INTERPOL_DEPTH',
    'ConfigObjError',
    'NestingError',
    'ParseError',
    'DuplicateError',
    'ConfigspecError',
    'ConfigObj',
    'SimpleVal',
    'InterpolationError',
    'InterpolationDepthError',
    'MissingInterpolationOption',
    'RepeatSectionError',
    'UnreprError',
    'UnknownType',
    '__docformat__',
    'flatten_errors',
)

DEFAULT_INDENT_TYPE = ' '
NUM_INDENT_SPACES = 4
MAX_INTERPOL_DEPTH = 10

OPTION_DEFAULTS = {
    'interpolation': True,
    'raise_errors': False,
    'list_values': True,
    'create_empty': False,
    'file_error': False,
    'configspec': None,
    'stringify': True,
    # option may be set to one of ('', ' ', '\t')
    'indent_type': None,
    'encoding': None,
    'default_encoding': None,
    'unrepr': False,
    'write_empty_values': False,
}
__license__ = '''# ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; ;
# The contents of this file are subject to the PyTis Public License Version    ;
# 2.0 (the "License"); you may not use this file except in compliance with     ;
# the License. You may obtain a copy of the License at                         ;
#                                                                              ;
#     http://www.PyTis.com/License/                                            ;
#                                                                              ;
#     Copyright © %s Josh Lee                                                ;
#                                                                              ;
# Software distributed under the License is distributed on an "AS IS" basis,   ;
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License     ;
# for the specific language governing rights and limitations under the         ;
# License.                                                                     ;
#                                                                              ;
# ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;; ;

''' % datetime.datetime.now().year

def getObj(s):
    s = "a=" + s
    p = compiler.parse(s)
    return p.getChildren()[1].getChildren()[0].getChildren()[1]

class UnknownType(Exception):
    pass

class Builder:
    
    def build(self, o):
        m = getattr(self, 'build_' + o.__class__.__name__, None)
        if m is None:
            raise UnknownType(o.__class__.__name__)
        return m(o)
    
    def build_List(self, o):
        return map(self.build, o.getChildren())
    
    def build_Const(self, o):
        return o.value
    
    def build_Dict(self, o):
        d = {}
        i = iter(map(self.build, o.getChildren()))
        for el in i:
            d[el] = i.next()
        return d
    
    def build_Tuple(self, o):
        return tuple(self.build_List(o))
    
    def build_Name(self, o):
        if o.name == 'None':
            return None
        if o.name == 'True':
            return True
        if o.name == 'False':
            return False
        
        # An undefinted Name
        raise UnknownType('Undefined Name')
    
    def build_Add(self, o):
        real, imag = map(self.build_Const, o.getChildren())
        try:
            real = float(real)
        except TypeError:
            raise UnknownType('Add')
        if not isinstance(imag, complex) or imag.real != 0.0:
            raise UnknownType('Add')
        return real+imag
    
    def build_Getattr(self, o):
        parent = self.build(o.expr)
        return getattr(parent, o.attrname)
    
    def build_UnarySub(self, o):
        return -self.build_Const(o.getChildren()[0])
    
    def build_UnaryAdd(self, o):
        return self.build_Const(o.getChildren()[0])

def unrepr(s):
    if not s:
        return s
    return Builder().build(getObj(s))

class ConfigObjError(SyntaxError):
    def __init__(self, message='', line_number=None, line=''):
        self.line = line
        self.line_number = line_number
        self.message = message
        SyntaxError.__init__(self, message)

class NestingError(ConfigObjError): pass

class ParseError(ConfigObjError): pass

class DuplicateError(ConfigObjError): pass

class ConfigspecError(ConfigObjError): pass

class InterpolationError(ConfigObjError): pass

class InterpolationDepthError(InterpolationError):

    def __init__(self, option):
        InterpolationError.__init__(
            self,
            'max interpolation depth exceeded in value "%s".' % option)

class RepeatSectionError(ConfigObjError): pass

class MissingInterpolationOption(InterpolationError):

    def __init__(self, option):
        InterpolationError.__init__(
            self,
            'missing option "%s" in interpolation.' % option)

class UnreprError(ConfigObjError): pass


class Section(dict):

    _KEYCRE = re.compile(r"%\(([^)]*)\)s|.")

    def __init__(self, parent, depth, main, indict=None, name=None):
        if indict is None:
            indict = {}
        dict.__init__(self)
        # used for nesting level *and* interpolation
        self.parent = parent
        # used for the interpolation attribute
        self.main = main
        # level of nesting depth of this Section
        self.depth = depth
        # the sequence of scalar values in this Section
        self.scalars = []
        # the sequence of sections in this Section
        self.sections = []
        # purely for information
        self.name = name

        # for comments :-)
        self.comments = {}
        self.inline_comments = {}
        # for the configspec
        self.configspec = {}
        self._order = []
        self._configspec_comments = {}
        self._configspec_inline_comments = {}
        self._cs_section_comments = {}
        self._cs_section_inline_comments = {}
        # for defaults
        self.defaults = []
        #
        # we do this explicitly so that __setitem__ is used properly
        # (rather than just passing to ``dict.__init__``)
        for entry in indict:
            self[entry] = indict[entry]

    def __setattr__(self, attr, val):
      dict.__setattr__(self, attr, val)
      dict.__setitem__(self, attr, val)


    def __getattr__(self, attr):
      try:
        return dict.__getattr__(self,attr)
      except AttributeError:
        try:
          return self[attr]
        except KeyError:
          raise AttributeError, attr

    def _interpolate(self, value):
        depth = MAX_INTERPOL_DEPTH
        # loop through this until it's done
        while depth:
            depth -= 1
            if value.find("%(") != -1:
                value = self._KEYCRE.sub(self._interpolation_replace, value)
            else:
                break
        else:
            raise InterpolationDepthError(value)
        return value

    def _interpolation_replace(self, match):
        s = match.group(1)
        if s is None:
            return match.group()
        else:
            # switch off interpolation before we try and fetch anything !
            self.main.interpolation = False
            # try the 'DEFAULT' member of *this section* first
            val = self.get('DEFAULT', {}).get(s)
            # try the 'DEFAULT' member of the *parent section* next
            if val is None:
                val = self.parent.get('DEFAULT', {}).get(s)
            # last, try the 'DEFAULT' member of the *main section*
            if val is None:
                val = self.main.get('DEFAULT', {}).get(s)
            self.main.interpolation = True
            if val is None:
                raise MissingInterpolationOption(s)
            return val

    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        if self.main.interpolation and isinstance(val, StringTypes):
            return self._interpolate(val)
        return val

    def __setitem__(self, key, value, unrepr=False):
        if not isinstance(key, StringTypes):
            raise ValueError('The key "%s" is not a string.' % key)
        # add the comment
        if not self.comments.has_key(key):
            self.comments[key] = []
            self.inline_comments[key] = ''
        # remove the entry from defaults
        if key in self.defaults:
            self.defaults.remove(key)
        #
        if isinstance(value, Section):
            if not self.has_key(key):
                self.sections.append(key)
            dict.__setitem__(self, key, value)
        elif isinstance(value, dict) and not unrepr:
            # First create the new depth level,
            # then create the section
            if not self.has_key(key):
                self.sections.append(key)
            new_depth = self.depth + 1
            dict.__setitem__(
                self,
                key,
                Section(
                    self,
                    new_depth,
                    self.main,
                    indict=value,
                    name=key))
        else:
            if not self.has_key(key):
                self.scalars.append(key)
            if not self.main.stringify:
                if isinstance(value, StringTypes):
                    pass
                elif isinstance(value, (list, tuple)):
                    for entry in value:
                        if not isinstance(entry, StringTypes):
                            raise TypeError(
                                'Value is not a string "%s".' % entry)
                else:
                    raise TypeError('Value is not a string "%s".' % value)
            dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict. __delitem__(self, key)
        if key in self.scalars:
            self.scalars.remove(key)
        else:
            self.sections.remove(key)
        del self.comments[key]
        del self.inline_comments[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def update(self, indict):
        for entry in indict:
            self[entry] = indict[entry]

    def pop(self, key, *args):
        val = dict.pop(self, key, *args)
        if key in self.scalars:
            del self.comments[key]
            del self.inline_comments[key]
            self.scalars.remove(key)
        elif key in self.sections:
            del self.comments[key]
            del self.inline_comments[key]
            self.sections.remove(key)
        if self.main.interpolation and isinstance(val, StringTypes):
            return self._interpolate(val)
        return val

    def popitem(self):
        sequence = (self.scalars + self.sections)
        if not sequence:
            raise KeyError(": 'popitem(): dictionary is empty'")
        key = sequence[0]
        val =  self[key]
        del self[key]
        return key, val

    def clear(self):
        dict.clear(self)
        self.scalars = []
        self.sections = []
        self.comments = {}
        self.inline_comments = {}
        self.configspec = {}

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return self[key]

    def items(self):
        return zip((self.scalars + self.sections), self.values())

    def keys(self):
        return (self.scalars + self.sections)

    def values(self):
        return [self[key] for key in (self.scalars + self.sections)]

    def iteritems(self):
        return iter(self.items())

    def iterkeys(self):
        return iter((self.scalars + self.sections))

    __iter__ = iterkeys

    def itervalues(self):
        return iter(self.values())

    def __repr__(self):
        return '{%s}' % ', '.join([('%s: %s' % (repr(key), repr(self[key])))
            for key in (self.scalars + self.sections)])

    __str__ = __repr__

    # Extra methods - not in a normal dictionary

    def dict(self):
        newdict = {}
        for entry in self:
            this_entry = self[entry]
            if isinstance(this_entry, Section):
                this_entry = this_entry.dict()
            elif isinstance(this_entry, list):
                # create a copy rather than a reference
                this_entry = list(this_entry)
            elif isinstance(this_entry, tuple):
                # create a copy rather than a reference
                this_entry = tuple(this_entry)
            newdict[entry] = this_entry
        return newdict

    def merge(self, indict):
        for key, val in indict.items():
            if (key in self and isinstance(self[key], dict) and
                                isinstance(val, dict)):
                self[key].merge(val)
            else:   
                self[key] = val

    def rename(self, oldkey, newkey):
        if oldkey in self.scalars:
            the_list = self.scalars
        elif oldkey in self.sections:
            the_list = self.sections
        else:
            raise KeyError('Key "%s" not found.' % oldkey)
        pos = the_list.index(oldkey)
        #
        val = self[oldkey]
        dict.__delitem__(self, oldkey)
        dict.__setitem__(self, newkey, val)
        the_list.remove(oldkey)
        the_list.insert(pos, newkey)
        comm = self.comments[oldkey]
        inline_comment = self.inline_comments[oldkey]
        del self.comments[oldkey]
        del self.inline_comments[oldkey]
        self.comments[newkey] = comm
        self.inline_comments[newkey] = inline_comment

    def walk(self, function, raise_errors=True,
            call_on_sections=False, **keywargs):
        out = {}
        # scalars first
        for i in range(len(self.scalars)):
            entry = self.scalars[i]
            try:
                val = function(self, entry, **keywargs)
                # bound again in case name has changed
                entry = self.scalars[i]
                out[entry] = val
            except Exception:
                if raise_errors:
                    raise
                else:
                    entry = self.scalars[i]
                    out[entry] = False
        # then sections
        for i in range(len(self.sections)):
            entry = self.sections[i]
            if call_on_sections:
                try:
                    function(self, entry, **keywargs)
                except Exception:
                    if raise_errors:
                        raise
                    else:
                        entry = self.sections[i]
                        out[entry] = False
                # bound again in case name has changed
                entry = self.sections[i]
            # previous result is discarded
            out[entry] = self[entry].walk(
                function,
                raise_errors=raise_errors,
                call_on_sections=call_on_sections,
                **keywargs)
        return out

    def decode(self, encoding):
        warn('use of ``decode`` is deprecated.', DeprecationWarning)
        def decode(section, key, encoding=encoding, warn=True):
            val = section[key]
            if isinstance(val, (list, tuple)):
                newval = []
                for entry in val:
                    newval.append(entry.decode(encoding))
            elif isinstance(val, dict):
                newval = val
            else:
                newval = val.decode(encoding)
            newkey = key.decode(encoding)
            section.rename(key, newkey)
            section[newkey] = newval
        # using ``call_on_sections`` allows us to modify section names
        self.walk(decode, call_on_sections=True)

    def encode(self, encoding):
        warn('use of ``encode`` is deprecated.', DeprecationWarning)
        def encode(section, key, encoding=encoding):
            val = section[key]
            if isinstance(val, (list, tuple)):
                newval = []
                for entry in val:
                    newval.append(entry.encode(encoding))
            elif isinstance(val, dict):
                newval = val
            else:
                newval = val.encode(encoding)
            newkey = key.encode(encoding)
            section.rename(key, newkey)
            section[newkey] = newval
        self.walk(encode, call_on_sections=True)

    def istrue(self, key):
        warn('use of ``istrue`` is deprecated. Use ``as_bool`` method '
                'instead.', DeprecationWarning)
        return self.as_bool(key)

    def as_bool(self, key):
        val = self[key]
        if val == True:
            return True
        elif val == False:
            return False
        else:
            try:
                if not isinstance(val, StringTypes):
                    raise KeyError
                else:
                    return self.main._bools[val.lower()]
            except KeyError:
                raise ValueError('Value "%s" is neither True nor False' % val)

    def as_int(self, key):
        return int(self[key])

    def as_float(self, key):
        return float(self[key])
    

class ConfigObj(Section):
    _exists = None 

    def set_exists(self):
      if os.path.exists(self.filename):
        self._exists = True
      else:
        self._exists = False
    def get_exists(self):
      if self._exists is None:
        self.set_exists()
      return self._exists
    exists = property(get_exists, set_exists)

    _keyword = re.compile(r'''^ # line start
        (\s*)                   # indentation
        (                       # keyword
            (?:".*?")|          # double quotes
            (?:'.*?')|          # single quotes
            (?:[^'"=].*?)       # no quotes
        )
        \s*=\s*                 # divider
        (.*)                    # value (including list values and comments)
        $   # line end
        ''',
        re.VERBOSE)

    _sectionmarker = re.compile(r'''^
        (\s*)                     # 1: indentation
        ((?:\[\s*)+)              # 2: section marker open
        (                         # 3: section name open
            (?:"\s*\S.*?\s*")|    # at least one non-space with double quotes
            (?:'\s*\S.*?\s*')|    # at least one non-space with single quotes
            (?:[^'"\s].*?)        # at least one non-space unquoted
        )                         # section name close
        ((?:\s*\])+)              # 4: section marker close
        \s*(\#.*)?                # 5: optional comment
        $''',
        re.VERBOSE)

    # this regexp pulls list values out as a single string
    # or single values and comments
    # FIXME-IGRNORED: this regex adds a '' to the end of comma terminated lists
    #   workaround in ``_handle_value``
    _valueexp = re.compile(r'''^
        (?:
            (?:
                (
                    (?:
                        (?:
                            (?:".*?")|              # double quotes
                            (?:'.*?')|              # single quotes
                            (?:[^'",\#][^,\#]*?)    # unquoted
                        )
                        \s*,\s*                     # comma
                    )*      # match all list items ending in a comma (if any)
                )
                (
                    (?:".*?")|                      # double quotes
                    (?:'.*?')|                      # single quotes
                    (?:[^'",\#\s][^,]*?)|           # unquoted
                    (?:(?<!,))                      # Empty value
                )?          # last item in a list - or string value
            )|
            (,)             # alternatively a single comma - empty list
        )
        \s*(\#.*)?          # optional comment
        $''',
        re.VERBOSE)

    # use findall to get the members of a list value
    _listvalueexp = re.compile(r'''
        (
            (?:".*?")|          # double quotes
            (?:'.*?')|          # single quotes
            (?:[^'",\#].*?)       # unquoted
        )
        \s*,\s*                 # comma
        ''',
        re.VERBOSE)

    # this regexp is used for the value
    # when lists are switched off
    _nolistvalue = re.compile(r'''^
        (
            (?:".*?")|          # double quotes
            (?:'.*?')|          # single quotes
            (?:[^'"\#].*?)|     # unquoted
            (?:)                # Empty value
        )
        \s*(\#.*)?              # optional comment
        $''',
        re.VERBOSE)

    # regexes for finding triple quoted values on one line
    _single_line_single = re.compile(r"^'''(.*?)'''\s*(#.*)?$")
    _single_line_double = re.compile(r'^"""(.*?)"""\s*(#.*)?$')
    _multi_line_single = re.compile(r"^(.*?)'''\s*(#.*)?$")
    _multi_line_double = re.compile(r'^(.*?)"""\s*(#.*)?$')

    _triple_quote = {
        "'''": (_single_line_single, _multi_line_single),
        '"""': (_single_line_double, _multi_line_double),
    }

    # Used by the ``istrue`` Section method
    _bools = {
        'yes': True, 'no': False,
        'on': True, 'off': False,
        '1': True, '0': False,
        'true': True, 'false': False,
        }

    def __init__(self, infile=None, options=None, **kwargs):
        if infile is None:
            infile = []
        if options is None:
            options = {}
        else:
            options = dict(options)
        # keyword arguments take precedence over an options dictionary
        options.update(kwargs)
        # init the superclass
        Section.__init__(self, self, 0, self)
        #
        defaults = OPTION_DEFAULTS.copy()
        for entry in options.keys():
            if entry not in defaults.keys():
                raise TypeError('Unrecognised option "%s".' % entry)
        # TODO-IGNORED: check the values too.
        #
        # Add any explicit options to the defaults
        defaults.update(options)
        #
        # initialise a few variables
        self.filename = None
        self._errors = []
        self.raise_errors = defaults['raise_errors']
        self.interpolation = defaults['interpolation']
        self.list_values = defaults['list_values']
        self.create_empty = defaults['create_empty']
        self.file_error = defaults['file_error']
        self.stringify = defaults['stringify']
        self.indent_type = defaults['indent_type']
        self.encoding = defaults['encoding']
        self.default_encoding = defaults['default_encoding']
        self.BOM = False
        self.newlines = None
        self.write_empty_values = defaults['write_empty_values']
        self.unrepr = defaults['unrepr']
        #
        self.initial_comment = []
        self.final_comment = []
        #
        self._terminated = False
        #
        if isinstance(infile, StringTypes):
            self.filename = infile
            if os.path.isfile(infile):
                infile = open(infile).read() or []
            elif self.file_error:
                # raise an error if the file doesn't exist
                raise IOError('Config file not found: "%s".' % self.filename)
            else:
                # file doesn't already exist
                if self.create_empty:
                    # this is a good test that the filename specified
                    # isn't impossible - like on a non existent device
                    h = open(infile, 'w')
                    h.write('')
                    h.write("\n")
                    h.close()
                infile = []
        elif isinstance(infile, (list, tuple)):
            infile = list(infile)
        elif isinstance(infile, dict):
            # initialise self
            # the Section class handles creating subsections
            if isinstance(infile, ConfigObj):
                # get a copy of our ConfigObj
                infile = infile.dict()
            for entry in infile:
                self[entry] = infile[entry]
            del self._errors
            if defaults['configspec'] is not None:
                self._handle_configspec(defaults['configspec'])
            else:
                self.configspec = None
            return
        elif hasattr(infile, 'read'):
            # This supports file like objects
            infile = infile.read() or []
            # needs splitting into lines - but needs doing *after* decoding
            # in case it's not an 8 bit encoding
        else:
            raise TypeError('infile must be a filename,' \
                ' file like object, or list of lines.')
        #
        if infile:
            # don't do it for the empty ConfigObj
            infile = self._handle_bom(infile)
            # infile is now *always* a list
            #
            # Set the newlines attribute (first line ending it finds)
            # and strip trailing '\n' or '\r' from lines
            for line in infile:
                if (not line) or (line[-1] not in '\r\n'):
                    continue
                for end in ('\r\n', '\n', '\r'):
                    if line.endswith(end):
                        self.newlines = end
                        break
                break
            if infile[-1] and infile[-1] in '\r\n':
                self._terminated = True
            infile = [line.rstrip('\r\n') for line in infile]
        #
        self._parse(infile)
        # if we had any errors, now is the time to raise them
        if self._errors:
            info = "at line %s." % self._errors[0].line_number
            if len(self._errors) > 1:
                msg = ("Parsing failed with several errors.\nFirst error %s" %
                    info)
                error = ConfigObjError(msg)
            else:
                error = self._errors[0]
            # set the errors attribute; it's a list of tuples:
            # (error_type, message, line_number)
            error.errors = self._errors
            # set the config attribute
            error.config = self
            raise error
        # delete private attributes
        del self._errors
        #
        if defaults['configspec'] is None:
            self.configspec = None
        else:
            self._handle_configspec(defaults['configspec'])
    
    def __repr__(self):
        return 'ConfigObj({%s})' % ', '.join(
            [('%s: %s' % (repr(key), repr(self[key]))) for key in
            (self.scalars + self.sections)])
    
    def _handle_bom(self, infile):
        if ((self.encoding is not None) and
            (self.encoding.lower() not in BOM_LIST)):
            # No need to check for a BOM
            # the encoding specified doesn't have one
            # just decode
            return self._decode(infile, self.encoding)
        #
        if isinstance(infile, (list, tuple)):
            line = infile[0]
        else:
            line = infile
        if self.encoding is not None:
            # encoding explicitly supplied
            # And it could have an associated BOM
            # TODO-IGNORED: if encoding is just UTF16 - we ought to check for both
            # TODO-IGNORED: big endian and little endian versions.
            enc = BOM_LIST[self.encoding.lower()]
            if enc == 'utf_16':
                # For UTF16 we try big endian and little endian
                for BOM, (encoding, final_encoding) in BOMS.items():
                    if not final_encoding:
                        # skip UTF8
                        continue
                    if infile.startswith(BOM):
                        ### BOM discovered
                        ##self.BOM = True
                        # Don't need to remove BOM
                        return self._decode(infile, encoding)
                #
                # If we get this far, will *probably* raise a DecodeError
                # As it doesn't appear to start with a BOM
                return self._decode(infile, self.encoding)
            #
            # Must be UTF8
            BOM = BOM_SET[enc]
            if not line.startswith(BOM):
                return self._decode(infile, self.encoding)
            #
            newline = line[len(BOM):]
            #
            # BOM removed
            if isinstance(infile, (list, tuple)):
                infile[0] = newline
            else:
                infile = newline
            self.BOM = True
            return self._decode(infile, self.encoding)
        #
        # No encoding specified - so we need to check for UTF8/UTF16
        for BOM, (encoding, final_encoding) in BOMS.items():
            if not line.startswith(BOM):
                continue
            else:
                # BOM discovered
                self.encoding = final_encoding
                if not final_encoding:
                    self.BOM = True
                    # UTF8
                    # remove BOM
                    newline = line[len(BOM):]
                    if isinstance(infile, (list, tuple)):
                        infile[0] = newline
                    else:
                        infile = newline
                    # UTF8 - don't decode
                    if isinstance(infile, StringTypes):
                        return infile.splitlines(True)
                    else:
                        return infile
                # UTF16 - have to decode
                return self._decode(infile, encoding)
        #
        # No BOM discovered and no encoding specified, just return
        if isinstance(infile, StringTypes):
            # infile read from a file will be a single string
            return infile.splitlines(True)
        else:
            return infile

    def _a_to_u(self, string):
        if not self.encoding:
            return string
        else:
            return string.decode('ascii')

    def _decode(self, infile, encoding):
        if isinstance(infile, StringTypes):
            # can't be unicode
            # NOTE: Could raise a ``UnicodeDecodeError``
            return infile.decode(encoding).splitlines(True)
        for i, line in enumerate(infile):
            if not isinstance(line, unicode):
                # NOTE: The isinstance test here handles mixed lists of unicode/string
                # NOTE: But the decode will break on any non-string values
                # NOTE: Or could raise a ``UnicodeDecodeError``
                infile[i] = line.decode(encoding)
        return infile

    def _decode_element(self, line):
        if not self.encoding:
            return line
        if isinstance(line, str) and self.default_encoding:
            return line.decode(self.default_encoding)
        return line

    def _str(self, value):
        if not isinstance(value, StringTypes):
            return str(value)
        else:
            return value

    def _parse(self, infile):
        temp_list_values = self.list_values
        if self.unrepr:
            self.list_values = False
        comment_list = []
        done_start = False
        this_section = self
        maxline = len(infile) - 1
        cur_index = -1
        reset_comment = False
        while cur_index < maxline:
            if reset_comment:
                comment_list = []
            cur_index += 1
            line = infile[cur_index]
            sline = line.strip()
            # do we have anything on the line ?
            if not sline or sline.startswith('#'):
                reset_comment = False
                comment_list.append(line)
                continue
            if not done_start:
                # preserve initial comment
                self.initial_comment = comment_list
                comment_list = []
                done_start = True
            reset_comment = True
            # first we check if it's a section marker
            mat = self._sectionmarker.match(line)
            if mat is not None:
                # is a section line
                (indent, sect_open, sect_name, sect_close, comment) = (
                    mat.groups())
                if indent and (self.indent_type is None):
                    self.indent_type = indent[0]
                cur_depth = sect_open.count('[')
                if cur_depth != sect_close.count(']'):
                    self._handle_error(
                        "Cannot compute the section depth at line %s.",
                        NestingError, infile, cur_index)
                    continue
                #
                if cur_depth < this_section.depth:
                    # the new section is dropping back to a previous level
                    try:
                        parent = self._match_depth(
                            this_section,
                            cur_depth).parent
                    except SyntaxError:
                        self._handle_error(
                            "Cannot compute nesting level at line %s.",
                            NestingError, infile, cur_index)
                        continue
                elif cur_depth == this_section.depth:
                    # the new section is a sibling of the current section
                    parent = this_section.parent
                elif cur_depth == this_section.depth + 1:
                    # the new section is a child the current section
                    parent = this_section
                else:
                    self._handle_error(
                        "Section too nested at line %s.",
                        NestingError, infile, cur_index)
                #
                sect_name = self._unquote(sect_name)
                if parent.has_key(sect_name):
                    self._handle_error(
                        'Duplicate section name at line %s.',
                        DuplicateError, infile, cur_index)
                    continue
                # create the new section
                this_section = Section(
                    parent,
                    cur_depth,
                    self,
                    name=sect_name)
                parent[sect_name] = this_section
                parent.inline_comments[sect_name] = comment
                parent.comments[sect_name] = comment_list
                continue
            #
            # it's not a section marker,
            # so it should be a valid ``key = value`` line
            mat = self._keyword.match(line)
            if mat is None:
                # it neither matched as a keyword
                # or a section marker
                self._handle_error(
                    'Invalid line at line "%s".',
                    ParseError, infile, cur_index)
            else:
                # is a keyword value
                # value will include any inline comment
                (indent, key, value) = mat.groups()
                if indent and (self.indent_type is None):
                    self.indent_type = indent[0]
                # check for a multiline value
                if value[:3] in ['"""', "'''"]:
                    try:
                        (value, comment, cur_index) = self._multiline(
                            value, infile, cur_index, maxline)
                    except SyntaxError:
                        self._handle_error(
                            'Parse error in value at line %s.',
                            ParseError, infile, cur_index)
                        continue
                    else:
                        if self.unrepr:
                            comment = ''
                            try:
                                value = unrepr(value)
                            except Exception as e:
                                if type(e) == UnknownType:
                                    msg = 'Unknown name or type in value at line %s.'
                                else:
                                    msg = 'Parse error in value at line %s.'
                                self._handle_error(msg, UnreprError, infile,
                                    cur_index)
                                continue
                else:
                    if self.unrepr:
                        comment = ''
                        try:
                            value = unrepr(value)
                        except Exception as e:
                            if isinstance(e, UnknownType):
                                msg = 'Unknown name or type in value at line %s.'
                            else:
                                msg = 'Parse error in value at line %s.'
                            self._handle_error(msg, UnreprError, infile,
                                cur_index)
                            continue
                    else:
                        # extract comment and lists
                        try:
                            (value, comment) = self._handle_value(value)
                        except SyntaxError:
                            self._handle_error(
                                'Parse error in value at line %s.',
                                ParseError, infile, cur_index)
                            continue
                #
                key = self._unquote(key)
                if this_section.has_key(key):
                    self._handle_error(
                        'Duplicate keyword name at line %s.',
                        DuplicateError, infile, cur_index)
                    continue
                # add the key.
                # we set unrepr because if we have got this far we will never
                # be creating a new section
                this_section.__setitem__(key, value, unrepr=True)
                this_section.inline_comments[key] = comment
                this_section.comments[key] = comment_list
                continue
        #
        if self.indent_type is None:
            # no indentation used, set the type accordingly
            self.indent_type = ''
        #
        if self._terminated:
            comment_list.append('')
        # preserve the final comment
        if not self and not self.initial_comment:
            self.initial_comment = comment_list
        elif not reset_comment:
            self.final_comment = comment_list
        self.list_values = temp_list_values

    def _match_depth(self, sect, depth):
        while depth < sect.depth:
            if sect is sect.parent:
                # we've reached the top level already
                raise SyntaxError
            sect = sect.parent
        if sect.depth == depth:
            return sect
        # shouldn't get here
        raise SyntaxError

    def _handle_error(self, text, ErrorClass, infile, cur_index):
        line = infile[cur_index]
        cur_index += 1
        message = text % cur_index
        error = ErrorClass(message, cur_index, line)
        if self.raise_errors:
            # raise the error - parsing stops here
            raise error
        # store the error
        # reraise when parsing has finished
        self._errors.append(error)

    def _unquote(self, value):
        if (value[0] == value[-1]) and (value[0] in ('"', "'")):
            value = value[1:-1]
        return value

    def _quote(self, value, multiline=True):
        if multiline and self.write_empty_values and value == '':
            # Only if multiline is set, so that it is used for values not
            # keys, and not values that are part of a list
            return ''
        if multiline and isinstance(value, (list, tuple)):
            if not value:
                return ','
            elif len(value) == 1:
                return self._quote(value[0], multiline=False) + ','
            return ', '.join([self._quote(val, multiline=False)
                for val in value])
        if not isinstance(value, StringTypes):
            if self.stringify:
                value = str(value)
            else:
                raise TypeError('Value "%s" is not a string.' % value)
        squot = "'%s'"
        dquot = '"%s"'
        noquot = "%s"
        wspace_plus = ' \r\t\n\v\t\'"'
        tsquot = '"""%s"""'
        tdquot = "'''%s'''"
        if not value:
            return '""'
        if (not self.list_values and '\n' not in value) or not (multiline and
                ((("'" in value) and ('"' in value)) or ('\n' in value))):
            if not self.list_values:
                # we don't quote if ``list_values=False``
                quot = noquot
            # for normal values either single or double quotes will do
            elif '\n' in value:
                # will only happen if multiline is off - e.g. '\n' in key
                raise ConfigObjError('Value "%s" cannot be safely quoted.' %
                    value)
            elif ((value[0] not in wspace_plus) and
                    (value[-1] not in wspace_plus) and
                    (',' not in value)):
                quot = noquot
            else:
                if ("'" in value) and ('"' in value):
                    raise ConfigObjError(
                        'Value "%s" cannot be safely quoted.' % value)
                elif '"' in value:
                    quot = squot
                else:
                    quot = dquot
        else:
            # if value has '\n' or "'" *and* '"', it will need triple quotes
            if (value.find('"""') != -1) and (value.find("'''") != -1):
                raise ConfigObjError(
                    'Value "%s" cannot be safely quoted.' % value)
            if value.find('"""') == -1:
                quot = tdquot
            else:
                quot = tsquot
        return quot % value

    def _handle_value(self, value):
        # do we look for lists in values ?
        if not self.list_values:
            mat = self._nolistvalue.match(value)
            if mat is None:
                raise SyntaxError
            # NOTE: we don't unquote here
            return mat.groups()
        #
        mat = self._valueexp.match(value)
        if mat is None:
            # the value is badly constructed, probably badly quoted,
            # or an invalid list
            raise SyntaxError
        (list_values, single, empty_list, comment) = mat.groups()
        if (list_values == '') and (single is None):
            # change this if you want to accept empty values
            raise SyntaxError
        # NOTE: note there is no error handling from here if the regex
        # is wrong: then incorrect values will slip through
        if empty_list is not None:
            # the single comma - meaning an empty list
            return ([], comment)
        if single is not None:
            # handle empty values
            if list_values and not single:
                # FIXME-IGNORED: the '' is a workaround because our regex now matches
                #   '' at the end of a list if it has a trailing comma
                single = None
            else:
                single = single or '""'
                single = self._unquote(single)
        if list_values == '':
            # not a list value
            return (single, comment)
        the_list = self._listvalueexp.findall(list_values)
        the_list = [self._unquote(val) for val in the_list]
        if single is not None:
            the_list += [single]
        return (the_list, comment)

    def _multiline(self, value, infile, cur_index, maxline):
        quot = value[:3]
        newvalue = value[3:]
        single_line = self._triple_quote[quot][0]
        multi_line = self._triple_quote[quot][1]
        mat = single_line.match(value)
        if mat is not None:
            retval = list(mat.groups())
            retval.append(cur_index)
            return retval
        elif newvalue.find(quot) != -1:
            # somehow the triple quote is missing
            raise SyntaxError
        #
        while cur_index < maxline:
            cur_index += 1
            newvalue += '\n'
            line = infile[cur_index]
            if line.find(quot) == -1:
                newvalue += line
            else:
                # end of multiline, process it
                break
        else:
            # we've got to the end of the config, oops...
            raise SyntaxError
        mat = multi_line.match(line)
        if mat is None:
            # a badly formed line
            raise SyntaxError
        (value, comment) = mat.groups()
        return (newvalue + value, comment, cur_index)

    def _handle_configspec(self, configspec):
        # FIXME-IGNORED: Should we check that the configspec was created with the 
        #   correct settings ? (i.e. ``list_values=False``)
        if not isinstance(configspec, ConfigObj):
            try:
                configspec = ConfigObj(
                    configspec,
                    raise_errors=True,
                    file_error=True,
                    list_values=False)
            except ConfigObjError as e:
                # FIXME-IGNORED: Should these errors have a reference
                # to the already parsed ConfigObj ?
                raise ConfigspecError('Parsing configspec failed: %s' % e)
            except IOError as e:
                raise IOError('Reading configspec failed: %s' % e)
        self._set_configspec_value(configspec, self)

    def _set_configspec_value(self, configspec, section):
        if '__many__' in configspec.sections:
            section.configspec['__many__'] = configspec['__many__']
            if len(configspec.sections) > 1:
                # FIXME-IGNORED: can we supply any useful information here ?
                raise RepeatSectionError
        if hasattr(configspec, 'initial_comment'):
            section._configspec_initial_comment = configspec.initial_comment
            section._configspec_final_comment = configspec.final_comment
            section._configspec_encoding = configspec.encoding
            section._configspec_BOM = configspec.BOM
            section._configspec_newlines = configspec.newlines
            section._configspec_indent_type = configspec.indent_type
        for entry in configspec.scalars:
            section._configspec_comments[entry] = configspec.comments[entry]
            section._configspec_inline_comments[entry] = (
                configspec.inline_comments[entry])
            section.configspec[entry] = configspec[entry]
            section._order.append(entry)
        for entry in configspec.sections:
            if entry == '__many__':
                continue
            section._cs_section_comments[entry] = configspec.comments[entry]
            section._cs_section_inline_comments[entry] = (
                configspec.inline_comments[entry])
            if not section.has_key(entry):
                section[entry] = {}
            self._set_configspec_value(configspec[entry], section[entry])

    def _handle_repeat(self, section, configspec):
        try:
            section_keys = configspec.sections
            scalar_keys = configspec.scalars
        except AttributeError:
            section_keys = [entry for entry in configspec 
                                if isinstance(configspec[entry], dict)]
            scalar_keys = [entry for entry in configspec 
                                if not isinstance(configspec[entry], dict)]
        if '__many__' in section_keys and len(section_keys) > 1:
            # FIXME-IGNORED: can we supply any useful information here ?
            raise RepeatSectionError
        scalars = {}
        sections = {}
        for entry in scalar_keys:
            val = configspec[entry]
            scalars[entry] = val
        for entry in section_keys:
            val = configspec[entry]
            if entry == '__many__':
                scalars[entry] = val
                continue
            sections[entry] = val
        #
        section.configspec = scalars
        for entry in sections:
            if not section.has_key(entry):
                section[entry] = {}
            self._handle_repeat(section[entry], sections[entry])

    def _write_line(self, indent_string, entry, this_entry, comment):
        # NOTE: the calls to self._quote here handles non-StringType values.
        if not self.unrepr:
            val = self._decode_element(self._quote(this_entry))
        else:
            val = repr(this_entry)
        return '%s%s%s%s%s' % (
            indent_string,
            self._decode_element(self._quote(entry, multiline=False)),
            self._a_to_u(' = '),
            val,
            self._decode_element(comment))

    def _write_marker(self, indent_string, depth, entry, comment):
        return '%s%s%s%s%s' % (
            indent_string,
            self._a_to_u('[' * depth),
            self._quote(self._decode_element(entry), multiline=False),
            self._a_to_u(']' * depth),
            self._decode_element(comment))

    def _handle_comment(self, comment):
        if not comment:
            return ''
        if self.indent_type == '\t':
            start = self._a_to_u('\t')
        else:
            start = self._a_to_u(' ' * NUM_INDENT_SPACES)
        if not comment.startswith('#'):
            start += _a_to_u('# ')
        return (start + comment)

    def _compute_indent_string(self, depth):
        if self.indent_type == '':
            # no indentation at all
            return ''
        if self.indent_type == '\t':
            return '\t' * depth
        if self.indent_type == ' ':
            return ' ' * NUM_INDENT_SPACES * depth
        raise SyntaxError

    # Public methods

    def write(self, outfile=None, section=None):
        if self.indent_type is None:
            # this can be true if initialised from a dictionary
            self.indent_type = DEFAULT_INDENT_TYPE
        #
        out = []
        cs = self._a_to_u('#')
        csp = self._a_to_u('# ')
        if section is None:
            int_val = self.interpolation
            self.interpolation = False
            section = self
            for line in self.initial_comment:
                line = self._decode_element(line)
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith(cs):
                    line = csp + line
                out.append(line)
        #
        indent_string = self._a_to_u(
            self._compute_indent_string(section.depth))
        for entry in (section.scalars + section.sections):
            if entry in section.defaults:
                # don't write out default values
                continue
            for comment_line in section.comments[entry]:
                comment_line = self._decode_element(comment_line.lstrip())
                if comment_line and not comment_line.startswith(cs):
                    comment_line = csp + comment_line
                out.append(indent_string + comment_line)
            this_entry = section[entry]
            comment = self._handle_comment(section.inline_comments[entry])
            #
            if isinstance(this_entry, dict):
                # a section
                out.append(self._write_marker(
                    indent_string,
                    this_entry.depth,
                    entry,
                    comment))
                out.extend(self.write(section=this_entry))
            else:
                out.append(self._write_line(
                    indent_string,
                    entry,
                    this_entry,
                    comment))
        #
        if section is self:
            for line in self.final_comment:
                line = self._decode_element(line)
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith(cs):
                    line = csp + line
                out.append(line)
            self.interpolation = int_val
        #
        if section is not self:
            return out
        #
        if (self.filename is None) and (outfile is None):
            # output a list of lines
            # might need to encode
            # NOTE: This will *screw* UTF16, each line will start with the BOM
            if self.encoding:
                out = [l.encode(self.encoding) for l in out]
            if (self.BOM and ((self.encoding is None) or
                (BOM_LIST.get(self.encoding.lower()) == 'utf_8'))):
                # Add the UTF8 BOM
                if not out:
                    out.append('')
                out[0] = BOM_UTF8 + out[0]
            return out
        #
        # Turn the list to a string, joined with correct newlines
        output = (self._a_to_u(self.newlines or os.linesep)
            ).join(out)
        if self.encoding:
            output = output.encode(self.encoding)
        if (self.BOM and ((self.encoding is None) or
            (BOM_LIST.get(self.encoding.lower()) == 'utf_8'))):
            # Add the UTF8 BOM
            output = BOM_UTF8 + output
        if outfile is not None:
            pass
            #outfile.write(output.replace("\n", "\r\n"))
        else:
            h = open(self.filename, 'wb')
            #h.write(output.replace("\n", "\r\n"))
            h.write(output)
            h.write("\n")
            h.close()

    def validate(self, validator, preserve_errors=False, copy=False,
        section=None):
        if section is None:
            if self.configspec is None:
                raise ValueError( 'No configspec supplied.')
            if preserve_errors:
                if VdtMissingValue is None:
                    raise ImportError('Missing validate module.')
            section = self
        #
        spec_section = section.configspec
        if copy and hasattr(section, '_configspec_initial_comment'):
            section.initial_comment = section._configspec_initial_comment
            section.final_comment = section._configspec_final_comment
            section.encoding = section._configspec_encoding
            section.BOM = section._configspec_BOM
            section.newlines = section._configspec_newlines
            section.indent_type = section._configspec_indent_type
        if '__many__' in section.configspec:
            many = spec_section['__many__']
            # dynamically assign the configspecs
            # for the sections below
            for entry in section.sections:
                self._handle_repeat(section[entry], many)
        #
        out = {}
        ret_true = True
        ret_false = True
        order = [k for k in section._order if k in spec_section]
        order += [k for k in spec_section if k not in order]
        for entry in order:
            if entry == '__many__':
                continue
            if (not entry in section.scalars) or (entry in section.defaults):
                # missing entries
                # or entries from defaults
                missing = True
                val = None
                if copy and not entry in section.scalars:
                    # copy comments
                    section.comments[entry] = (
                        section._configspec_comments.get(entry, []))
                    section.inline_comments[entry] = (
                        section._configspec_inline_comments.get(entry, ''))
                #
            else:
                missing = False
                val = section[entry]
            try:
                check = validator.check(spec_section[entry],
                                        val,
                                        missing=missing
                                        )
            except validator.baseErrorClass as e:
                if not preserve_errors or isinstance(e, VdtMissingValue):
                    out[entry] = False
                else:
                    # preserve the error
                    out[entry] = e
                    ret_false = False
                ret_true = False
            else:
                ret_false = False
                out[entry] = True
                if self.stringify or missing:
                    # if we are doing type conversion
                    # or the value is a supplied default
                    if not self.stringify:
                        if isinstance(check, (list, tuple)):
                            # preserve lists
                            check = [self._str(item) for item in check]
                        elif missing and check is None:
                            # convert the None from a default to a ''
                            check = ''
                        else:
                            check = self._str(check)
                    if (check != val) or missing:
                        section[entry] = check
                if not copy and missing and entry not in section.defaults:
                    section.defaults.append(entry)
        #
        # Missing sections will have been created as empty ones when the
        # configspec was read.
        for entry in section.sections:
            # FIXME-IGNORED: this means DEFAULT is not copied in copy mode
            if section is self and entry == 'DEFAULT':
                continue
            if copy:
                section.comments[entry] = section._cs_section_comments[entry]
                section.inline_comments[entry] = (
                    section._cs_section_inline_comments[entry])
            check = self.validate(validator, preserve_errors=preserve_errors,
                copy=copy, section=section[entry])
            out[entry] = check
            if check == False:
                ret_true = False
            elif check == True:
                ret_false = False
            else:
                ret_true = False
                ret_false = False
        #
        if ret_true:
            return True
        elif ret_false:
            return False
        else:
            return out

    def save(self):
        return self.write()




class SimpleVal(object):
    
    def __init__(self):
        self.baseErrorClass = ConfigObjError
    
    def check(self, check, member, missing=False):
        if missing:
            raise self.baseErrorClass
        return member

# Check / processing functions for options
def flatten_errors(cfg, res, levels=None, results=None):
    if levels is None:
        # first time called
        levels = []
        results = []
    if res is True:
        return results
    if res is False:
        results.append((levels[:], None, False))
        if levels:
            levels.pop()
        return results
    for (key, val) in res.items():
        if val == True:
            continue
        if isinstance(cfg.get(key), dict):
            # Go down one level
            levels.append(key)
            flatten_errors(cfg[key], val, levels, results)
            continue
        results.append((levels[:], key, val))
    #
    # Go up one level
    if levels:
        levels.pop()
    #
    return results

"""*A programming language is a medium of expression.* - Paul Graham"""

def fload(fname):
    fpath = os.path.abspath(fname)

    if not os.path.isdir(os.path.dirname(fpath)) or \
        not os.path.exists(os.path.dirname(fpath)):
        os.makedirs(os.path.abspath(os.path.dirname(fpath)))

    return load(fname, True)

def load(fname, write=False):
    fpath = os.path.abspath(fname)
    if not os.path.isdir(os.path.dirname(fpath)) or \
        not os.path.exists(os.path.dirname(fpath)):
        raise OSError( "Directory of config file does not exist, you may " \
                       "create it now or you may call fload, to forceably " \
                       "do what is nessacary to create this file.")

    if (not os.path.isfile(fname) or not os.path.exists(fname)) and write:
        f = open(fpath,'w+')
        f.write('')
        f.close()

    if not os.path.isfile(fname) or not os.path.exists(fname):
        raise OSError("File not found: %s" % fname)

    return ConfigObj(fname)

