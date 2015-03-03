#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Wednesday, 03 December 2014 05:53:04 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import re

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Config(object):
    """ Helper class to access the git config file """

    def __init__(self):
        self.branches = {}
        self.remotes = {}
        self.core = {}

    def __close_section(self, section):        
        """ close current section """
        if section:
            section_type = section['section_type']                    
            if section_type == 'core':
                self.core = section
            elif section_type == 'remote':
                self.remotes[section['section_name']] = section
            elif section_type == 'branch':
                self.branches[section['section_name']] = section


    def load_from_string(self, in_str):
        section_re = re.compile(r'\[(?P<section>\w+)( \"(?P<name>.+)\")?]')
        setting_re = re.compile(r'\s*(?P<key>.+) = (?P<value>.+)')

        lines = in_str.split('\n')
        cur_section = None
        for line in lines:
            match = section_re.match(line)
            if not match:
                # not a section so must be a setting
                match = setting_re.match(line)
                if match:
                    cur_section[match.group('key').strip()] = match.group('value').strip()
            else:
                self.__close_section(cur_section)
                cur_section = {}
                stype = match.group('section')
                sname = match.group('name')
                if sname:
                    cur_section['section_name'] = sname
                cur_section['section_type'] = stype

        self.__close_section(cur_section)

    def load_from_file(self, path):
        config_file = open(path, 'r')
        self.load_from_string(config_file.read())
        config_file.close()

    def get_core_setting(self, key):
        return self.get_setting('core', '', key)

    def get_branch_setting(self, name, key):
        return self.get_setting('branch', name, key)

    def get_remote_setting(self, name, key):
        return self.get_setting('remote', name, key)

    def get_setting(self, type, name, key):
        src_dict = None
        if type == 'core':
            src_dict = self.core
        elif type == 'branch':
            if name in self.branches:
                src_dict = self.branches[name]
        elif type == 'remote':
            if name in self.remotes:
                src_dict = self.remotes[name]

        if src_dict and key in src_dict:
            return src_dict[key]

        return None
            

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------
if __name__ == "__main__":
    pass

