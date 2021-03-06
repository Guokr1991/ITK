# Copyright 2014-2015 Insight Software Consortium.
# Copyright 2004-2008 Roman Yakovenko.
# Distributed under the Boost Software License, Version 1.0.
# See http://www.boost.org/LICENSE_1_0.txt

"""
Defines C++ parser configuration classes.

"""

import os
import copy
import platform
import subprocess
import warnings
from .. import utils


class parser_configuration_t(object):

    """
    C++ parser configuration holder

    This class serves as a base class for the parameters that can be used
    to customize the call to a C++ parser.

    This class also allows users to work with relative files paths. In this
    case files are searched in the following order:

       1. current directory
       2. working directory
       3. additional include paths specified by the user

    """

    def __init__(
            self,
            working_directory='.',
            include_paths=None,
            define_symbols=None,
            undefine_symbols=None,
            cflags="",
            compiler=None,
            xml_generator="gccxml",
            keep_xml=False,
            compiler_path=None,
            flags=None):

        object.__init__(self)
        self.__working_directory = working_directory

        if not include_paths:
            include_paths = []
        self.__include_paths = include_paths

        if not define_symbols:
            define_symbols = []
        self.__define_symbols = define_symbols

        if not undefine_symbols:
            undefine_symbols = []
        self.__undefine_symbols = undefine_symbols

        self.__cflags = cflags

        self.__compiler = compiler

        self.__xml_generator = xml_generator

        self.__keep_xml = keep_xml

        if flags is None:
            flags = []
        self.__flags = flags

        # If no compiler path was set and we are using castxml, set the path
        self.__compiler_path = create_compiler_path(
            xml_generator, compiler_path)

    def clone(self):
        raise NotImplementedError(self.__class__.__name__)

    @property
    def working_directory(self):
        return self.__working_directory

    @working_directory.setter
    def working_directory(self, working_dir):
        self.__working_directory = working_dir

    @property
    def include_paths(self):
        """list of include paths to look for header files"""
        return self.__include_paths

    @property
    def define_symbols(self):
        """list of "define" directives """
        return self.__define_symbols

    @property
    def undefine_symbols(self):
        """list of "undefine" directives """
        return self.__undefine_symbols

    @property
    def compiler(self):
        """get compiler name to simulate"""
        return self.__compiler

    @compiler.setter
    def compiler(self, compiler):
        """set compiler name to simulate"""
        self.__compiler = compiler

    @property
    def xml_generator(self):
        """get xml_generator (gccxml or castxml)"""
        return self.__xml_generator

    @xml_generator.setter
    def xml_generator(self, xml_generator):
        """set xml_generator (gccxml or castxml)"""
        self.__xml_generator = xml_generator

    @property
    def keep_xml(self):
        """Are xml files kept after errors."""
        return self.__keep_xml

    @keep_xml.setter
    def keep_xml(self, keep_xml):
        """Set if xml files kept after errors."""
        self.__keep_xml = keep_xml

    @property
    def flags(self):
        """Optional flags for pygccxml."""
        return self.__flags

    @flags.setter
    def flags(self, flags):
        """Optional flags for pygccxml."""
        if flags is None:
            flags = []
        self.__flags = flags

    @property
    def compiler_path(self):
        """Get the path for the compiler."""
        return self.__compiler_path

    @compiler_path.setter
    def compiler_path(self, compiler_path):
        """Set the path for the compiler."""
        self.__compiler_path = compiler_path

    @property
    def cflags(self):
        "additional flags to pass to compiler"
        return self.__cflags

    @cflags.setter
    def cflags(self, val):
        self.__cflags = val

    def append_cflags(self, val):
        self.__cflags = self.__cflags + ' ' + val

    def __ensure_dir_exists(self, dir_path, meaning):
        if os.path.isdir(dir_path):
            return
        if os.path.exists(self.working_directory):
            raise RuntimeError(
                '%s("%s") does not exist!' % (meaning, dir_path))
        else:
            raise RuntimeError(
                '%s("%s") should be "directory", not a file.' %
                (meaning, dir_path))

    def raise_on_wrong_settings(self):
        """validates the configuration settings and raises RuntimeError on
        error"""
        self.__ensure_dir_exists(self.working_directory, 'working directory')
        for idir in self.include_paths:
            self.__ensure_dir_exists(idir, 'include directory')


class xml_generator_configuration_t(parser_configuration_t):
    """
    Configuration object to collect parameters for invoking gccxml or castxml.

    This class serves as a container for the parameters that can be used
    to customize the call to gccxml or castxml.

    """

    def __init__(
            self,
            gccxml_path='',
            xml_generator_path='',
            working_directory='.',
            include_paths=None,
            define_symbols=None,
            undefine_symbols=None,
            start_with_declarations=None,
            ignore_gccxml_output=False,
            cflags="",
            compiler=None,
            xml_generator="gccxml",
            keep_xml=False,
            compiler_path=None,
            flags=None):

        parser_configuration_t.__init__(
            self,
            working_directory=working_directory,
            include_paths=include_paths,
            define_symbols=define_symbols,
            undefine_symbols=undefine_symbols,
            cflags=cflags,
            compiler=compiler,
            xml_generator=xml_generator,
            keep_xml=keep_xml,
            compiler_path=compiler_path,
            flags=flags)

        if gccxml_path != '':
            self.__gccxml_path = gccxml_path
        self.__xml_generator_path = xml_generator_path

        if not start_with_declarations:
            start_with_declarations = []
        self.__start_with_declarations = start_with_declarations

        self.__ignore_gccxml_output = ignore_gccxml_output

    def clone(self):
        return copy.deepcopy(self)

    @property
    def gccxml_path(self):
        """
        Gccxml binary location

        """

        warnings.warn(
            "gccxml_path is deprecated. \n" +
            "Please use xml_generator_path instead.", DeprecationWarning)
        return self.__gccxml_path

    @gccxml_path.setter
    def gccxml_path(self, new_path):
        warnings.warn(
            "gccxml_path is deprecated. \n" +
            "Please use xml_generator_path instead.", DeprecationWarning)
        self.__gccxml_path = new_path

    @property
    def xml_generator_path(self):
        """
        XML generator binary location

        """

        return self.__xml_generator_path

    @xml_generator_path.setter
    def xml_generator_path(self, new_path):
        self.__xml_generator_path = new_path

    @property
    def start_with_declarations(self):
        """list of declarations gccxml should start with, when it dumps
        declaration tree"""
        return self.__start_with_declarations

    @property
    def ignore_gccxml_output(self):
        """set this property to True, if you want pygccxml to ignore any
            error warning that comes from gccxml"""
        return self.__ignore_gccxml_output

    @ignore_gccxml_output.setter
    def ignore_gccxml_output(self, val=True):
        self.__ignore_gccxml_output = val

    def raise_on_wrong_settings(self):
        super(xml_generator_configuration_t, self).raise_on_wrong_settings()
        if os.path.isfile(self.xml_generator_path):
            return
        if os.name == 'nt':
            gccxml_name = 'gccxml' + '.exe'
            environment_var_delimiter = ';'
        elif os.name == 'posix':
            gccxml_name = 'gccxml'
            environment_var_delimiter = ':'
        else:
            raise RuntimeError(
                'unable to find out location of the xml generator')
        may_be_gccxml = os.path.join(self.xml_generator_path, gccxml_name)
        if os.path.isfile(may_be_gccxml):
            self.xml_generator_path = may_be_gccxml
        else:
            for path in os.environ['PATH'].split(environment_var_delimiter):
                xml_generator_path = os.path.join(path, gccxml_name)
                if os.path.isfile(xml_generator_path):
                    self.xml_generator_path = xml_generator_path
                    break
            else:
                msg = (
                    'xml_generator_path("%s") should exists or to be a ' +
                    'valid file name.') % self.xml_generator_path
                raise RuntimeError(msg)

gccxml_configuration_example = \
    """
[gccxml]
#path to gccxml executable file - optional, if not provided, os.environ['PATH']
#variable is used to find it
gccxml_path=(deprecated)
xml_generator_path=
#gccxml working directory - optional, could be set to your source code
directory
working_directory=
#additional include directories, separated by ';'
include_paths=
#gccxml has a nice algorithms, which selects what C++ compiler to emulate.
#You can explicitly set what compiler it should emulate.
#Valid options are: g++, msvc6, msvc7, msvc71, msvc8, cl.
compiler=
# gccxml or castxml
xml_generator=
# Do we keep xml files or not after errors
keep_xml=
# Set the path to the compiler
compiler_path=
"""


def load_xml_generator_configuration(configuration, **defaults):
    """
    loads CastXML or GCC-XML configuration from an `.ini` file or any other
    file class
    :class:`configparser.ConfigParser` is able to parse.

    :param configuration: configuration could be
                          string(configuration file path) or instance
                          of :class:`configparser.ConfigParser` class

    :rtype: :class:`.xml_generator_configuration_t`

    Configuration file skeleton::

       [gccxml]
       #path to gccxml or castxml executable file - optional, if not provided,
       os.environ['PATH']
       #variable is used to find it
       gccxml_path=(deprecated)
       xml_generator_path=
       #gccxml working directory - optional, could be set to your source
       code directory
       working_directory=
       #additional include directories, separated by ';'
       include_paths=
       #gccxml has a nice algorithms, which selects what C++ compiler
       to emulate.
       #You can explicitly set what compiler it should emulate.
       #Valid options are: g++, msvc6, msvc7, msvc71, msvc8, cl.
       compiler=
       # gccxml or castxml
       xml_generator=
       # Do we keep xml files or not after errors
       keep_xml=
       # Set the path to the compiler
       compiler_path=

    """

    parser = configuration
    if utils.is_str(configuration):
        try:
            from configparser import ConfigParser
        except ImportError:
            from ConfigParser import SafeConfigParser as ConfigParser
        parser = ConfigParser()
        parser.read(configuration)

    # Create a new empty configuration
    cfg = xml_generator_configuration_t()

    values = defaults
    if not values:
        values = {}

    if parser.has_section('gccxml'):
        for name, value in parser.items('gccxml'):
            if value.strip():
                values[name] = value

    for name, value in values.items():
        if isinstance(value, str):
            value = value.strip()
        if name == 'gccxml_path':
            cfg.gccxml_path = value
        if name == 'xml_generator_path':
            cfg.xml_generator_path = value
        elif name == 'working_directory':
            cfg.working_directory = value
        elif name == 'include_paths':
            for p in value.split(';'):
                p = p.strip()
                if p:
                    cfg.include_paths.append(p)
        elif name == 'compiler':
            cfg.compiler = value
        elif name == 'xml_generator':
            cfg.xml_generator = value
        elif name == 'keep_xml':
            cfg.keep_xml = value
        elif name == 'cflags':
            cfg.cflags = value
        elif name == 'flags':
            cfg.flags = value
        elif name == 'compiler_path':
            cfg.compiler_path = value
        else:
            print('\n%s entry was ignored' % name)

    # If no compiler path was set and we are using castxml, set the path
    # Here we overwrite the default configuration done in the cfg because
    # the xml_generator was set through the setter after the creation of a new
    # emppty configuration object.
    cfg.compiler_path = create_compiler_path(
        cfg.xml_generator, cfg.compiler_path)

    return cfg


def create_compiler_path(xml_generator, compiler_path):
    """
    Try to guess a path for the compiler.

    Only needed with castxml on Mac or Linux.

    """

    if xml_generator == 'castxml' and compiler_path is None:
        if platform.system() != 'Windows':
            # On windows there is no need for the compiler path
            p = subprocess.Popen(
                ['which', 'clang++'], stdout=subprocess.PIPE)
            compiler_path = p.stdout.read().decode("utf-8").rstrip()
            # No clang found; use gcc
            if compiler_path == '':
                compiler_path = '/usr/bin/c++'

    return compiler_path

# Keep these for backward compatibility
gccxml_configuration_t = xml_generator_configuration_t
load_gccxml_configuration = load_xml_generator_configuration

if __name__ == '__main__':
    print(load_xml_generator_configuration('xml_generator.cfg').__dict__)
