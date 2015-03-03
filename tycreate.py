    #-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Wargaming.net
# Created : Thursday, 29 January 2015 11:09:07 AM
#-----------------------------------------------------------------------------

"""
Command line tool to help create hub components (libraries, plugins, etc.)
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import argparse
import os
from details.utils.misc import vlog, enable_verbose_log, add_command_line_action
from details.context import Context
from details.template import Template
from details.templateengine import TemplateEngine
from details.console_app import ConsoleApp

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

class CreateApp(object):
    description = 'See ? for documentation'

    def __init__(self):
        # initialize available templates
        context = Context()
        self.templates = Template.get_available_templates(context, context.template_path)

    def add_command_line_options(self, parser):
        parser.add_argument('--output', '-o', action='store', help='Output directory')
        
        parser.set_defaults(mode='create')
        subparsers = parser.add_subparsers()
            
        # add options for each available template
        for template in self.templates:
            template_parser = add_command_line_action(subparsers, 
                                                      template.name, 
                                                      template.description)
            template_parser.set_defaults(submode=template.name)
            template.add_command_line_options(template_parser)      


    def app_main(self, context, options):   
        """ Application entry point """
        if options.output == None:
            options.output = os.getcwd()

        vlog("Output directory : " + options.output)

        if options.verbose:
            for template in self.templates:
                vlog(template.name)
                vlog(template.description)
                vlog(template.options)
                    
        # find the template user wants to expand and expand it
        opt_dict = vars(options)
        for template in self.templates:
            params = {}
            if options.action == template.name:
                for key, _ in template.options.iteritems():
                    params[key] = opt_dict[key]
                engine = TemplateEngine(context)
                engine.expand_template(template, params, options.output)

def main():
    """ Main script entry point """
    app = ConsoleApp(CreateApp())
    app.app_main()
            
if __name__ == "__main__":
    main()
