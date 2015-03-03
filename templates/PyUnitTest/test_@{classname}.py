@require(classname_camel)
@include("py_copyright_comment")
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

""" Unit Tests for @{classname_camel} """

@include("py_imports_comment")
import unittest
from details.test_case import TestCase

@include("py_comment_line")
# Unit tests
@include("py_comment_line")

class Test@{classname_camel}(TestCase):
    """ @{classname_camel} test cases """
    
    def test_construct(self):
        @{classname_camel}()        

@include("py_comment_line")
# Main
@include("py_comment_line")
if __name__ == "__main__":
    unittest.main()
