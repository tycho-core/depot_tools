#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Thursday, 20 November 2014 12:47:23 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import sublime, sublime_plugin
from details.templateengine import TemplateEngine
from details.template import Template
from details.context import Context
from details.utils.misc import enable_verbose_log
from details.format import Formatter
import os
import sys
import six

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------
def get_current_view_file_dir():
    window = sublime.active_window()
    if window != None:
        view = window.active_view()
        if view != None:
            return os.path.dirname(view.file_name())

    return None

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class CreateTemplateCommands:
    """ Hub sublime plugin """

    def __init__(self, in_context):
        """ Constructor """
        self.context = in_context
        self.engine = TemplateEngine(self.context)
        self.templates = Template.get_available_templates(self.context, 
                                                          self.context.template_path)
            
    def register_commands(self):
        """ Register commands """

        # Sublime discovers commands by looking at all the definitions in the module for ones 
        # that derive from its command base classes (WindowCommand et al). So to add our commands
        # we need to dynamically create new types and add them to the module.
        for template in self.templates:
            name = template.name.capitalize()
            type_name = "TyCreate" + name + "Command"

            # need to ensure
            if sys.version_info[0] < 3:
                type_name = type_name.encode('ascii', 'ignore')

            cmd_type = type(
                type_name,
                (sublime_plugin.WindowCommand,), 
                {
                    'template'     : template,
                    'run'          : CreateTemplateCommands.__command_run,
                    '__init__'     : CreateTemplateCommands.__command_init,
                    'input_done'   : CreateTemplateCommands.__command_input_done,
                    'input_change' : CreateTemplateCommands.__command_input_change,
                    'input_cancel' : CreateTemplateCommands.__command_input_cancel,
                    'engine'       : self.engine            
                }
            )
            globals()[cmd_type.__name__] = cmd_type
            print("added : " + type_name)


    @staticmethod
    def __command_init(self, window):
        self.window = window

    @staticmethod
    def __command_input_done(self, text):
        if self.state == 'output_dir':
            self.output_dir = text
            
            self.state = 'options'
            self.cur_option = 0
            self.option_name = None
            self.template_params = {}
        elif self.state == 'options':
            self.template_params[self.option_name] = text
            self.cur_option += 1

        # see if we are out of options
        if self.cur_option == len(self.template.options):
            print(str(self.template_params))
            if not self.engine.expand_template(self.template, 
                                               self.template_params, 
                                               self.output_dir):
                sublime.status_message("Failed to create template " + self.template.name)
        else:
            opt = self.options[self.cur_option]
            self.option_name = opt[0]
            self.window.show_input_panel(
                opt[1]['description'], "",          
                self.input_done, 
                self.input_change, 
                self.input_cancel)

    @staticmethod
    def __command_input_change(self, text):
        pass

    @staticmethod
    def __command_input_cancel(self, text):
        pass

    @staticmethod 
    def __command_run(self, name=None, dst_dir=None):
        # get current files directory 
        default_str = get_current_view_file_dir()

        # initial state
        self.state = 'output_dir'
        self.opt_index = 0
        self.options = {}
        self.output_dir = None
        self.options = []

        for key, val in six.iteritems(self.template.options):
            self.options.append([key, val])

        # get the directory to run in
        self.window.show_input_panel("Enter output directory", 
                                     default_str, 
                                     self.input_done, 
                                     self.input_change, 
                                     self.input_cancel)

#-----------------------------------------------------------------------------
# Commands
#-----------------------------------------------------------------------------
        
class TyFormatFileCommand(sublime_plugin.WindowCommand):    
    def run(self, input_path=None):
        if input_path == None:
            default_str = get_current_view_file_dir()
            self.window.show_input_panel("Enter file to format", 
                                         default_str,
                                         self.input_done,
                                         self.input_change,
                                         self.input_cancel)
        else:           
            pass

    def format_file(self, input_file):
        context = Context()
        print(input_file)
        file_type = Formatter.get_file_type(input_file)
        if file_type == 'c++':
            fmt = Formatter(context)
            return fmt.format_file_inplace(input_file, silent=True)         

        sublime.status_message("Unknowm file type (%s)" % (os.path.splitext(input_file)[1]))
        return False

    def input_done(self, input_file):
        self.format_file(input_file)

    def input_change(self, text):
        pass

    def input_cancel(self):
        pass

class TyFormatViewCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.context = Context()

        # get entire view contents
        view = self.view
        region = sublime.Region(0, view.size())
        content = view.substr(region)

        # save to temporary file preserving file extension
        ext = os.path.splitext(view.file_name())[1]
        temp_name = "tysubtemp" + ext
        temp_name = os.path.join(self.context.temp_dir, temp_name)
        temp_file = open(temp_name, 'w')
        temp_file.write(content)
        temp_file.close()
        file_format_cmd = TyFormatFileCommand(view.window)
        if file_format_cmd.format_file(temp_name):
            temp_file = open(temp_name, 'r')
            content = temp_file.read()
            temp_file.close()
            os.remove(temp_file)
            view.replace(edit, region, content)
            os.remove(temp_name)



def __register():
    context = Context()

    context.Verbose = True
    enable_verbose_log()
    plugin = CreateTemplateCommands(context)
    plugin.register_commands()

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
else:
    __register()

