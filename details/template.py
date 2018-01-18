#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Friday, 14 November 2014 10:07:21 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import json
import os
import six
from details.utils.misc import vlog, log

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Template(object):
    """ Template definition for use with the TemplateEngine """

    def __init__(self):
        """ Constructor """
        self.name = ''
        self.description = ''
        self.options = {}
        self.source = ''
        self.excluded_files = []
        self.target_dir = None        
        
    def add_command_line_options(self, parser):
        """ Add a command line option for this template """
        first = True
        for key, val in six.iteritems(self.options):
            # first option is positional the rest are flags
            vlog("Option : %s : %s" % (key, val))
            option_name = key           
            if not first:
                option_name = '--' + key
            parser.add_argument(option_name, action='store', help=val['description'])
            first = False
                            
    @staticmethod
    def load_from_file(context, path):
        """ Load a template from a file """
        try:
            template_def_file = open(path, 'r')
            template_params = json.load(template_def_file)
            template_def_file.close()
            new_template = Template()
            new_template.name = template_params['name']
            new_template.description = template_params['description']
            new_template.options = template_params['options']
            new_template.source = os.path.dirname(path)

            if 'target_dir' in template_params:
                new_template.target_dir = template_params['target_dir']

            new_template.excluded_files.append(context.template_info)
            return new_template
        except:
            return None

    @staticmethod           
    def get_available_templates(context, src_dir):
        """ Returns :
                list(Template) : List of all templates found in the passed directory.
        """
        templates = []
        names = os.listdir(src_dir)
        for name in names:
            path = os.path.abspath(os.path.join(src_dir, name))
            if os.path.isdir(path):
                if os.path.normcase(path) != os.path.normcase(context.common_template_path):
                    info_path = os.path.join(path, context.template_info)
                    info = Template.load_from_file(context, info_path)
                    if info == None:
                        log("Failed to load template " + info_path)
                    else:                       
                        templates.append(info)
        
        return templates            

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
