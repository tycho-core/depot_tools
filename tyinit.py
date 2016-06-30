# pylint : disable=superfluous-parens
#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Monday, 17 November 2014 02:48:24 PM
#-----------------------------------------------------------------------------
"""
This is used to initialise the environment for use and should be run on a fresh 
checkout of the depot tools. It is responsible for ensuring the necessary tools are
installed for the platform we are running on.
"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import os
import sys
import shutil
import details.utils.misc as tyutils
import details.utils.file as futils
from details.utils.misc import log, add_command_line_action
from details.template import Template
from details.templateengine import TemplateEngine
from details.console_app import ConsoleApp, configure_providers

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class InitTools(object):   
    """
    InitTools
    """
    description = '? for documentation'


    def __init__(self):
        """ Constructor """
        self.context = None
        self.packages = []
        self.depot_dir = None
        self.tools_dir = None

    def print_error_context(self):
        """ Override to print extra error information when an exception is caught """
        pass
        
    def add_command_line_options(self, parser):
        subparsers = parser.add_subparsers()
        add_command_line_action(subparsers, "install-aliases", "Install aliases for hub commands")
        add_command_line_action(subparsers, "install-sublime", "Install plugin for sublime editor")
        add_command_line_action(subparsers, "configure", "Install tools required to use the hub")

    def app_main(self, context, options):    
        self.context = context
        self.depot_dir = os.path.abspath(os.path.join(tyutils.get_script_dir(), ".."))
        self.tools_dir = os.path.join(self.depot_dir, "tools" + os.path.sep + sys.platform)


        if options.action == 'install-aliases':
            self.install_console_aliases()
        elif options.action == 'configure':
            self.install_tools()
        elif options.action == 'install-sublime':
            self.install_sublime_plugin()

    def install_tools(self):        
        from details.workspace import Workspace
        configure_providers(self.context)
        workspace = Workspace(self.context, self.context.current_dir)
        workspace.update()

    @staticmethod
    def __embed_in_file(file_path, lines):
        """
        Embeds the passed text to the end of a file. It will remove any current content
        that lies between tyhubstart and tyhub end comments (Assumes comments use hash)
        """
        # make sure profile file exists
        if not os.path.exists(file_path):
            profile_file = open(file_path, 'w+')
            if profile_file == None:
                print "failed"

                return False
            profile_file.close()

        # load the profile contents
        current_contents = []
        profile_file = open(file_path, 'r')
        current_contents = profile_file.readlines()
        profile_file.close()

        # check to see if we have already configured this file
        new_contents = []
        consume = False
        for line in current_contents:
            if '#tyhubstart' in line:
                consume = True
            elif '#tyhubend' in line:
                consume = False
            else:
                if not consume:
                    new_contents.append(line)

        # include our aliases
        new_contents.append('#tyhubstart')
        new_contents.extend(lines)
        new_contents.append('#tyhubend')
        profile_file = open(file_path, 'w')
        profile_file.write('\n'.join(new_contents))
        profile_file.close()

        return True


    def __install_powershell_aliases(self):
        powershell_profile_path = "Documents\\WindowsPowerShell\\Microsoft.PowerShell_profile.ps1"
        powershell_script_path = "\\scripts\\setupenv_powershell.ps1"

        # get path to powershell profile
        profile_path = os.getenv('USERPROFILE')
        profile_path = os.path.join(profile_path, powershell_profile_path)

        profile_dir = os.path.dirname(profile_path)
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        base_dir = os.path.abspath(os.path.join(tyutils.get_script_dir(), ".."))
        return self.__embed_in_file(profile_path, ['. "' + base_dir + powershell_script_path + '"'])

    def __install_bash_aliases(self):
        # get path to .bashrc 
        from os.path import expanduser
        home = expanduser("~")  
        bashrc_path = os.path.join(home, '.bashrc')

        script_path = os.path.join(tyutils.get_script_dir(), "..", 'scripts', 'setupenv_bash.sh')
        script_path = os.path.abspath(script_path)
        script_path = script_path.replace('\\', '/')

        # under windows we will have a path of the form c:\foo\bar but since this is bash land
        # we need to map this to /c/foo/bar or /cygdrive/c/foo/bar (cygwin)
        if sys.platform == 'win32':
            script_path = '/' + script_path.replace(':', '')

            # check to see if we are running under cygwin
            if 'BASH' in os.environ:
                bash_path = os.environ['BASH']
                if bash_path.find('/cygdrive/') != -1:
                    script_path += '/cygdrive'


        if not InitTools.__embed_in_file(bashrc_path, ['source ' + script_path]):
            print "Failed to install bash aliases"
            return False

        # on osx ensure there is a .bash_profile file to open the bash file
        if sys.platform == "darwin":
            path = os.path.join(home, ".bash_profile")
            if not os.path.exists(path):
                bash_profile_file = open(path, 'w')
                bash_profile_file.write("if [ -f ~/.bashrc ]; then . ~/.bashrc; fi ")
                bash_profile_file.close()

        return True


    def install_console_aliases(self):
        """
        Install command aliases for the console
        """     

        if sys.platform in ['win32']:
            if not self.__install_powershell_aliases():
                print "Failed to install powershell aliases"
            else:
                print "Installed PowerShell aliases"

        if self.__install_bash_aliases():
            print "Installed bash aliases"
        else:
            print "Failed to install bash aliases"

    def install_sublime_plugin(self):
        """
        Install sublime plugin
        """

        # load the sublime package template
        template_path = os.path.abspath(
            os.path.join(tyutils.get_script_dir(), '..', 'scripts', 'tysublime_package', self.context.template_info))

        template = Template.load_from_file(self.context, template_path)
        if template == None:
            log("Unable to load sublime template (%s)" % template_path)
            return False

        # create temporary directory
        temp_dir = os.path.join(self.context.temp_dir, 'tysublime_package')

        # expand plugin template
        params = {
            'ty_depot_path' : os.path.abspath(os.path.join(tyutils.get_script_dir(), '..'))
        }
        engine = TemplateEngine(self.context)

        if engine.expand_template(template, params, temp_dir):
            # compress the folder
            out_file = os.path.join(self.context.temp_dir, 'ty.sublime-package')
            futils.compress_directory(temp_dir, out_file)

            if os.path.exists(out_file):
                # install into sublime packages
                from os.path import expanduser
                home = expanduser("~")  
                base_dir = None
                if sys.platform == 'win32':
                    # check a coupe of locations to account for OS version changes
                    app_data_dirs = ['AppData\\Roaming','Application Data']
                    for ad_dir in app_data_dirs:
                        abs_ad_dir = os.path.join(home, ad_dir)
                        if os.path.exists(abs_ad_dir):
                            base_dir = abs_ad_dir
                elif sys.platform == 'darwin':
                    base_dir = os.path.join(home, 'Library', 'Application Support')

                if base_dir:
                    versions = ['Sublime Text 2', 'Sublime Text 3']
                    for version in versions:
                        sublime_pkg_dir = os.path.join(base_dir, version, 'Installed Packages')
                        if not os.path.exists(sublime_pkg_dir):
                            log("Cannot find sublime package directory (%s), is it installed?" % 
                                sublime_pkg_dir)
                            continue
                        sublime_pkg_path = os.path.join(sublime_pkg_dir, 'ty.sublime-package')
                        shutil.copyfile(out_file, sublime_pkg_path)     
                        log('Installed plugin for ' + version)
                else:
                    log("Don't know how to install sublime package on %s" % out_file)
                    log("Copy package manually from %s" % sys.platform)
                    return False

        return True




def script_main():
    """ Mains script entry point """
    app = ConsoleApp(InitTools(), os.path.basename(__file__))
    app.app_main()

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    script_main()
