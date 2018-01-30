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
        self.__task_status = ''
        self.__cur_line = ''
        self.__sub_task_status = ''
        self.__animate = True
        self.__show_task_info = True

    def enable_animations(self):
        """ Enable console animations """
        self.__animate = True

    def disable_animations(self):
        """ Disable console animations """
        self.__animate = False

    def disable_task_info(self):
        """ Disable outputing task progress informatin """
        self.__show_task_info = False

    def enable_task_info(self):
        """ Enable outputing task progress informatin """
        self.__show_task_info = True

    def shutdown(self):
        """ Ensure all threads are stopped and output cleared """
        self.hide_activity()
        self.__clear_last_line()

    def start_task(self, name):
        """ Start a task. This will update the line everytime update_task is called """
        if self.__show_task_info:
            self.write(name)
            self.__cur_task_name = name
            self.show_activity()

    def update_task(self, status):
        """ Update the status of the current task """
        if self.__show_task_info:
            self.hide_activity()
            line = '%s : %s    ' % (self.__cur_task_name, status)
            self.__task_status = status
            self.overwrite_line(line)
            self.show_activity()

    def update_sub_task(self, status):
        """ Update the sub task of the main task """
        if self.__show_task_info:
            self.pause_activity()
            line = '%s : %s : %s    ' % (self.__cur_task_name, self.__task_status, status)
            self.__sub_task_status = status
            self.overwrite_line(line)
            self.resume_activity()

    def end_task(self):
        """ End the current task """
        if self.__show_task_info:
            self.hide_activity()
            self.overwrite_line('%s : done' % (self.__cur_task_name))
            self.__out.write('\n')
            self.__cur_task_name = None
            self.__cur_line = ''
            self.__last_line_len = 0

    def write(self, line):
        """ Write to the output """
        if len(line) > 0:
            self.__out.write(line)
            self.__out.flush()
            self.__cur_line = line
            self.__last_line_len += len(line)

    def overwrite_line(self, line):
        """ Overwrite the last line written to the output """

        if not self.__animate:
            self.write('\n' + line);
            return

        # find longest matching substring between current and new line so
        # we can minimise redraw
        # find the matching part if it exists
        match_len = 0
        for old_char, new_char in zip(self.__cur_line, line):
            if old_char == new_char:
                match_len += 1
            else:
                break

        if match_len == 0:
            self.__clear_last_line()
            self.write(line)
        else:
            # find the remainder we need to clear if new line is shorter than
            # the current line
            padding_len = 0
            if len(line) < len(self.__cur_line):
                padding_len = len(self.__cur_line) - len(line)

            # clear from the end of the match to the end of the line
            self.__out.write(chr(8) * (len(self.__cur_line) - match_len))
            new_line = line[match_len:] + (' ' * padding_len) + (chr(8) * padding_len)
            self.__out.write(new_line)

        self.__cur_line = line
        self.__last_line_len = len(line)

    def write_line(self, line):
        """ Write a single line to the output """
        self.pause_activity()
        self.__clear_last_line()
        self.__out.write(line)
        self.__out.write('\n')
        self.write(self.__cur_line)
        self.resume_activity()

    def __clear_last_line(self):
        """ Clear the last line written to the output stream """

        if not self.__animate:
            self.write('\n')
        else:
            line_line = self.__last_line_len
            self.__out.write(chr(8) * self.__last_line_len)
            self.write(' ' * line_line)
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
                    self.__first = True

        def __init__(self, out_stream):
            """ Constructor """
            super(ConsoleWriter.ActivityThread, self).__init__()
            self.__exit_event = threading.Event()
            self.__out = out_stream
            self.__indicator = ConsoleWriter.ActivityThread.Bouncer(out_stream, 12)
            self.__pause_event = threading.Event()
            self.__paused_event = threading.Event()
            self.__resume_event = threading.Event()
            self.__paused = False

        def run(self):
            """ Main thread loop """

            activity_freq = 0.05
            while True:
                if self.__exit_event.is_set():
                    # thread quitting
                    break

                if self.__pause_event.is_set():
                    # reset the event
                    self.__pause_event.clear()

                    # clean up any display
                    self.__indicator.cleanup()

                    # signal the main thread that is safe to proceed
                    self.__paused_event.set()

                    # wait for the resume event to be fired
                    self.__resume_event.wait()

                    # and reset it
                    self.__resume_event.clear()

                self.__indicator.update()
                time.sleep(activity_freq)

            self.__indicator.cleanup()


        def pause(self):
            """ Pause the thread """

            # set the pause event to halt the update loop
            self.__pause_event.set()

            # wait for the thread to signal it has entered a paused state before
            # returning
            self.__paused_event.wait()
            self.__paused_event.clear()
            self.__paused = True

        def resume(self):
            """ Resume the thread """
            self.__paused = False
            self.__resume_event.set()

        def cancel(self):
            """ Stop the activity thread """

            # if paused then resume the main loop before trying to exit
            if self.__paused:
                self.resume()

            self.__exit_event.set()

    def show_activity(self):
        """ Show the activity spinner """
        if self.__animate:
            assert not self.__activity_thread
            self.__activity_thread = ConsoleWriter.ActivityThread(self.__out)
            self.__activity_thread.start()


    def hide_activity(self):
        """" Stop showing the activity spinner """
        if self.__activity_thread:
            self.__activity_thread.cancel()
            self.__activity_thread.join()
            self.__activity_thread = None

    def pause_activity(self):
        """ Pause the current activity indicator, preserves its state. """
        if self.__activity_thread:
            self.__activity_thread.pause()

    def resume_activity(self):
        """ Resume the activity indicator """
        if self.__activity_thread:
            self.__activity_thread.resume()


#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
