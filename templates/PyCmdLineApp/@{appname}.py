@require(appname_camel)
@include("py_copyright_comment")
"""
@{appname_camel} command line tool.
"""

@include("py_imports_comment")
import argparse

@include("py_class_comment")

class @{appname_camel}(object):
    """ @{appname_camel} """

    def __init__(self, args):
        """ Constructor """
        pass

    def run(self):
        pass

@include("py_comment_line")
# Main
@include("py_comment_line")

def main():
    """ Main script entry point """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-a', '--arg',
                        help='A boolean arg',
                        dest='barg', action='store_true')
    args = parser.parse_args()
    @{appname_camel}(args).run()

if __name__ == "__main__":
    main()
