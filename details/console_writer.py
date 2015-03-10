#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Friday, 06 March 2015 11:34:07 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import sys
import threading
import time

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
        self.__activity_thread = None

    def start_task(self, name):
        """ Start a task. This will update the line everytime update_task is called """
        self.write(name)
        self.__cur_task_name = name
        self.show_activity()

    def update_task(self, status):
        """ Update the status of the current task """
        self.hide_activity()
        line = '%s : %s    ' % (self.__cur_task_name, status)
        self.overwrite_line(line)
        self.show_activity()

    def end_task(self):
        """ End the current task """
        self.hide_activity()
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

    class ActivityThread(threading.Thread):
        """ Thread object to show activity indicator """

        class Spinner(object):
            """ Spinning activity indicator """

            __spinner = ['|', '/', '-', '\\']

            def __init__(self, out_stream):
                """ Constructor """
                self.__cur_char = 0
                self.__first = True
                self.__out = out_stream

            def update(self):
                """ Update the spinner """
                self.cleanup()
                self.__out.write(' %s' % self.__spinner[self.__cur_char])
                self.__cur_char += 1
                if self.__cur_char == len(self.__spinner):
                    self.__cur_char = 0
                self.__first = False

            def cleanup(self):
                """ Cleanup any remaining console output """
                length = 2
                bksp = 8
                if not self.__first:
                    line = '%s%s%s' % (chr(bksp) * length, ' ' * length, chr(bksp) * length)
                    self.__out.write(line)

        class Bouncer(object):
            """ Bouncing ball indicator """

            def __init__(self, out_stream, length):
                assert length > 2

                self.__out = out_stream
                self.__background = '|%s|' % ('-' * (length - 2))
                self.__ball_pos = 1
                self.__length = length
                self.__first = True
                self.__direction = 1

            def update(self):
                """ Update the ball """
                if not self.__first:
                    self.__out.write(chr(8) * self.__length)

                self.__out.write(self.__background[0:self.__ball_pos])
                self.__out.write('#')
                self.__out.write(self.__background[self.__ball_pos+1:])
                self.__first = False
                self.__ball_pos += self.__direction
                if self.__ball_pos == self.__length - 2:
                    self.__direction = -1
                    self.__ball_pos = self.__length - 2
                elif self.__ball_pos == 0:
                    self.__direction = 1
                    self.__ball_pos = 2

            def cleanup(self):
                """ Cleanup any remaining console output """
                if not self.__first:                    
                    line_len = self.__length
                    line = '%s%s%s' % (chr(8) * line_len, ' ' * line_len, chr(8) * line_len)
                    self.__out.write(line)

        def __init__(self, out_stream):
            """ Constructor """
            super(ConsoleWriter.ActivityThread, self).__init__()
            self.__exit_event = threading.Event()
            self.__out = out_stream
            self.__indicator = ConsoleWriter.ActivityThread.Bouncer(out_stream, 12)

        def run(self):
            """ Main thread loop """

            activity_freq = 0.05
            while not self.__exit_event.is_set():
                self.__indicator.update()
                time.sleep(activity_freq)
            self.__indicator.cleanup()


        def cancel(self):
            """ Stop the activity thread """
            self.__exit_event.set()

    def show_activity(self):
        """ Show the activity spinner """
        assert not self.__activity_thread
        self.__activity_thread = ConsoleWriter.ActivityThread(self.__out)
        self.__activity_thread.start()


    def hide_activity(self):
        """" Stop showing the activity spinner """
        if self.__activity_thread:
            self.__activity_thread.cancel()
            self.__activity_thread.join()
            self.__activity_thread = None



#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
