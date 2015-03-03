@require(classname_camel)
@include("py_copyright_comment")

@include("py_imports_comment")

@include("py_class_comment")

class @{classname_camel}(object):
    """ @{classname_camel} """
    
    def __init__(self):
        """ Constructor """
        pass
            

@include("py_comment_line")
# Main
@include("py_comment_line")

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
