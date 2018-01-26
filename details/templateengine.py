#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Friday, 14 November 2014 11:05:56 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import json
import datetime
import uuid
import os
import six
from wheezy.template.engine import Engine
from wheezy.template.ext.core import CoreExtension
from wheezy.template.loader import FileLoader, DictLoader
from details.utils.misc import vlog
from details.utils.file import get_directory_tree

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class TemplateEngine(object):
    """ TemplateEngine """

    def __init__(self, context):
        """ Constructor """
        self.context = context

    def __make_header_guard(self, name):
        name = "_%s_%s" % (name.upper(), uuid.uuid4())
        name = name.replace(".", "_")
        name = name.replace("-", "_")
        return name.upper()

    def __make_default_params(self):
        params = {}
        now = datetime.datetime.now()
        params['year'] = datetime.datetime.strftime(now, "%Y")
        params['date'] = datetime.datetime.strftime(now, "%A, %d %B %Y %I:%M:%S %p")
        return params

    def __get_global_params(self):
        if os.path.exists(self.context.global_options_path):
            global_params_file = open(self.context.global_options_path)
            global_params = json.load(global_params_file)
            global_params_file.close()
            return global_params

        return {}

    def is_project_dir(self, dir):
        """
        Check to see if the passed directory is a project directory or a child of it

        Returns:
            bool : True if directory is within a project
        """
        return self.__get_project_params_path(dir) != None

    def __get_project_params_path(self, directory):
        # search up the tree from the passed directory looking for project options file
        while not os.path.exists(os.path.join(directory, self.context.project_options_name)):
            nextdir = os.path.dirname(directory)
            vlog('Search : %s\\%s' % (directory, self.context.project_options_name))
            if directory == nextdir:
                return None
            directory = nextdir

        path = os.path.join(directory, self.context.project_options_name)
        if os.path.exists(path):
            return path

        return None

    def __get_project_template_path(self, directory):
        path = self.__get_project_params_path(directory)
        if path:
            path = os.path.dirname(path)
            path = os.path.join(path, self.context.project_template_dir)
            if os.path.exists(path):
                return path

        return None

    def __get_project_params(self, directory):
        path = self.__get_project_params_path(directory)
        if path:
            params_file = open(path)
            params = json.load(params_file)
            params_file.close()
            return params

        return {}

    def __apply_template_file(self, params, input_path, in_search_paths):
        # add file directory to search paths
        search_paths = []
        search_paths.extend(in_search_paths)
        search_paths.append(os.path.dirname(input_path))

        # apply templates
        vlog('Default search path : ' + str(in_search_paths))
        vlog('Search path : ' + str(search_paths))
        vlog(params)
        engine = Engine(
            loader=FileLoader(search_paths),
            extensions=[CoreExtension()]
        )
        template_name = os.path.basename(input_path)
        vlog('Loading template ' + template_name)
        template = engine.get_template(template_name)

        vlog('Rendering')
        output = template.render(params)
        return output

    def __apply_template_string(self, params, input_string):
        # automatically require all params
        require_string = "@require("
        first = True
        for key in params.keys():
            if not first:
                require_string = require_string + ","
            require_string = require_string + key
            first = False
        require_string = require_string + ")\n"

        input_string = require_string + input_string

        # set template engine
        template_dict = {'input_string' : input_string}
        engine = Engine(
            loader=DictLoader(template_dict),
            extensions=[CoreExtension()]
        )
        template = engine.get_template('input_string')
        output = template.render(params)
        return output

    @staticmethod
    def __make_camel_case(in_str):
        """ Transform an underscore delimted string to camel case
        i.e.  this_string -> ThisString """
        out_str = ''
        camel_me = False
        first = True
        for char in in_str:
            if camel_me:
                out_str += char.upper()
                camel_me = False
            elif char == '_':
                camel_me = True
            elif first:
                out_str += char.upper()
                first = False
            else:
                out_str += char

        return out_str

    def expand_template_string(self, params, input_string):
        return self.__apply_template_string(params, input_string)

    def expand_template(self, template, inparams, output_dir):
        # setup default template parameters
        params = self.__make_default_params()

        # class specific params
        for key, val in six.iteritems(inparams):
            params[key] = val
            params[key + '_upper'] = val.upper()
            params[key + '_camel'] = TemplateEngine.__make_camel_case(val)

        # load global template parameters
        params.update(self.__get_global_params())

        # template search paths. intialised here as we need to add per project directory to the
        # head of the list
        default_search_paths = []

        # check whether we are in a project and configure per project settings
        if self.is_project_dir(output_dir):
            # load project template parameters
            params.update(self.__get_project_params(output_dir))

            # project template search path
            default_search_paths.append(self.__get_project_template_path(output_dir))

        # add default search paths at the end
        default_search_paths.extend(self.context.common_template_paths)

        vlog(params)

        # get list of all files in the library template directory
        template_list = get_directory_tree(template.source).flatten()

        # keep track of all files we have created
        dest_paths = []

        # iterate over all files and expand templates into new location
        for input_file in template_list:
            vlog('Processing ' + input_file.absolute_path)

            # check to see if this file is in the excluded list
            if input_file.base_name in template.excluded_files:
                continue

            # apply templates to filename
            output_name = self.__apply_template_string(params,
                                                       os.path.basename(input_file.relative_path))

            # apply templates to file
            params['header_guard'] = self.__make_header_guard(output_name)
            output = self.__apply_template_file(params, input_file.absolute_path,
                                                default_search_paths)

            # save to new location
            dest_path = os.path.join(output_dir, input_file.relative_path)
            dest_path = os.path.join(os.path.dirname(dest_path), output_name)
            dest_dir = os.path.dirname(dest_path)

            # ensure destination directory exists
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            vlog('Writing output to ' + dest_path)
            out_file = open(dest_path, 'w+')
            out_file.write(output)
            out_file.close()

            dest_paths.append(dest_path)

        return dest_paths

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
