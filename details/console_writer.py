#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Friday, 06 March 2015 11:34:07 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import sys

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class ConsoleWriter(object):
    """ Interface for  writing to the console """
    
    def __init__(self):
        """ Constructor """
        self.__out = sys.stdout
        self.__cur_task_name = None
        self.__last_line_len = 0

    def start_task(self, name):
        """ Start a task. This will update the line everytime update_task is called """
        self.write(name)
        self.__cur_task_name = name

    def update_task(self, status):
        """ Update the status of the current task """
        line = '%s : %s' % (self.__cur_task_name, status)
        self.overwrite_line(line)

    def end_task(self):
        """ End the current task """
        self.overwrite_line('%s : done' % (self.__cur_task_name))
        self.__out.write('\n')
        self.__cur_task_name = None

    def write(self, line):
        """ Write to the output """
        self.__out.write(line)
        self.__last_line_len += len(line)

    def overwrite_line(self, line):
        """ Overwrite the last line written to the output """
        line_line = self.__last_line_len
        self.__clear_last_line()        
        self.write(' ' * line_line)
        self.__clear_last_line()
        self.write(line)

    def write_line(self, line):
        """ Write a single line to the output """
        self.__out.write(line)
        self.__out.write('\n')
        self.__last_line_len = 0

    def __clear_last_line(self):
        """ Clear the last line written to the output stream """
        self.__out.write(chr(8) * self.__last_line_len)
        self.__last_line_len = 0
            

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
