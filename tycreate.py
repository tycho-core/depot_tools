#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Thursday, 29 January 2015 11:09:07 AM
#-----------------------------------------------------------------------------

"""
Command line tool to help create hub components (libraries, plugins, etc.)
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function
import os
import six
from details.utils.misc import vlog, add_command_line_action
from details.context import Context
from details.template import Template
from details.templateengine import TemplateEngine
from details.console_app import ConsoleApp

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

class CreateApp(object):
    """ tyCreate application """
    description = 'See ? for documentation'

    def __init__(self):
        # initialize available templates
        context = Context()
        self.templates = Template.get_available_templates(context, context.template_path)

    def get_error_context(self):
        """ Override to print extra error information when an exception is caught """
        return ""

    def add_command_line_options(self, parser):
        """ Add command line options for this tool """
        parser.add_argument('--output', '-o', action='store', help='Output directory')
        parser.set_defaults(mode='create')
        subparsers = parser.add_subparsers()

        list_parser = add_command_line_action(subparsers,
                                              'list',
                                              'List all available templates')
        list_parser.add_argument('--json', action='store_true', help='Output as json')

        # add options for each available template
        for template in self.templates:
            template_parser = add_command_line_action(subparsers,
                                                      template.name,
                                                      template.description)
            template_parser.set_defaults(submode=template.name)
            template.add_command_line_options(template_parser)

    def app_main(self, context, options):
        """ Application entry point """
        if options.verbose:
            for template in self.templates:
                vlog(template.name)
                vlog(template.description)
                vlog(template.options)

        if options.action == 'list':
            if options.json:
                dicts = [template.to_simple_dict() for template in self.templates]
                context.console.write_line(ConsoleApp.to_json_string(dicts))
            else:
                for template in self.templates:
                    print(template.name)
            return 0

        # find the template user wants to expand and expand it
        opt_dict = vars(options)
        for template in self.templates:
            params = {}
            if options.action == template.name:
                for key, _ in six.iteritems(template.options):
                    params[key] = opt_dict[key]
                engine = TemplateEngine(context)

                output_dir = options.output
                if output_dir is None:
                    if template.target_dir is not None:
                        tengine = TemplateEngine(context)
                        options.output = tengine.expand_template_string(
                            params,
                            template.target_dir)
                        options.output = os.path.abspath(options.output)

                        # fail if directory already exists
                        if os.path.exists(options.output):
                            err_msg = 'Output directory (' + options.output +') already exists'
                            if options.machine:
                                json_obj = {
                                    'created_files': [],
                                    'error' : err_msg
                                }
                                context.console.write_line(ConsoleApp.to_json_string(json_obj))
                            else:
                                context.console.write_line(err_msg)
                            return 1


                    else:
                        options.output = os.getcwd()

                vlog("Output directory : " + options.output)

                created_files = []
                try:
                    created_files = engine.expand_template(template, params, options.output)
                except KeyError as ex:
                    msg = "Parameter not found {0}".format(str(ex))
                    if options.machine:
                        context.console.write_line(ConsoleApp.to_json_string({
                            "error": msg
                        }))
                    else:
                        context.console.write_line(msg)
                    return 1

                if options.machine:
                    # output json summary for consumption by external caller programs.
                    json_obj = {
                        'created_files': created_files,
                        'error' : ''
                    }
                    context.console.write_line(ConsoleApp.to_json_string(json_obj))
                return 0

def main():
    """ Main script entry point """
    app = ConsoleApp(CreateApp(), os.path.basename(__file__))
    app.app_main()

if __name__ == "__main__":
    main()
