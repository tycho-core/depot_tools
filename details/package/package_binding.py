#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Monday, 08 December 2014 01:09:56 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class PackageBinding(object):
    """ Maps the package into the local filesystem """    

    def __init__(self, pkg, root_dir):
        """ Constructor """
        self.package = pkg
        self.root_dir = root_dir
            
    def __repr__(self):
        """ Return string representation of the binding for display """
        return "%s (%s)" % (str(self.package), self.root_dir)

    def display_name(self):
        """ Get pretty name for the package for displaying to user """
        return str(self)
        
    def is_installed(self):
        """ Return true if the package is installed in the local filesystem """
        return self.package.is_installed(self.root_dir)

    def checkout(self):
        """ Checkout the package to the local filesystem """
        return self.package.checkout(self.root_dir)

    def update(self):
        """ Update the package in the local filesystem """
        return self.package.update(self.root_dir)

    def local_filesystem_status(self):
        """ Get the status of the package on disk """
        return self.package.local_filesystem_status(self.root_dir)

    def change_version(self, force):
        """ Change the local version to the package version """
        return self.package.change_version(self.root_dir, force)

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
