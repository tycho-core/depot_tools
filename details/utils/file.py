#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Tuesday, 03 February 2015 10:19:10 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import six
import hashlib
import sys
import os
import shutil
import subprocess

#-----------------------------------------------------------------------------
# Utility functions
#-----------------------------------------------------------------------------  
def download_file(url=None, file_name=None, progress_cb=None):
    """
    Download the specified file over a http connection.
    """
    import urllib2

    class ConsoleCallback(object):
        """ Default callback that outputs to stdout """

        def __init__(self):
            """ Constructor """
            self.__file_size = 0

        def started(self, base_name, file_size):
            """ Called when downloading starts """
            self.__file_size = file_size
            print("Downloading: %s Bytes: %s" % (base_name, file_size))
            
        def finished(self):
            """ Called when downloading ends """
            clr_str = "                           "
            sys.stdout.write(clr_str)
            sys.stdout.write(chr(8)* (len(clr_str)+1))            

        def progress(self, file_size_dl):
            """ Called when downloading has progresed """
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / self.__file_size)
            status = status + chr(8)* (len(status)+1)
            sys.stdout.write(status)

    if not progress_cb:
        progress_cb = ConsoleCallback()

    sha = hashlib.sha1()
    connection = urllib2.urlopen(url)
    dest_file = open(file_name, 'wb')
    meta = connection.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    base_name = file_name.split('/')[-1]

    if progress_cb:
        progress_cb.started(base_name, file_size)

    file_size_dl = 0
    block_sz = 1024 * 128
    while True:
        in_buffer = connection.read(block_sz)
        if not in_buffer:
            break

        file_size_dl += len(in_buffer)
        sha.update(in_buffer)
        dest_file.write(in_buffer)
        if progress_cb:
            progress_cb.progress(file_size_dl)

    # clear output 
    if progress_cb:
        progress_cb.finished()

    dest_file.close()
    return sha.hexdigest()

def copy_file(bin_dir, src, dst_dir):
    #print("Copying %s -> %s" % (src, dst_dir))
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    dst_path = os.path.join(dst_dir, os.path.basename(src))
    shutil.copyfile(src, dst_path)

def extract_file(bin_dir, src, dst_dir):
    import zipfile
    #print("Extracting %s -> %s" % (src, dst_dir))
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    with zipfile.ZipFile(src, 'r') as zip_file:
        zip_file.extractall(dst_dir)

def extract_7z_file(exe_path, src, dst_dir):
    #print("Extracting %s -> %s" % (src, dst_dir))
    cmd = [exe_path, 'x', '-so', '-o' + dst_dir, src]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()
    process.wait()
    return process.returncode == 0
    
def execute_process(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.wait()
    if process.returncode == 1:
        return [False, process.stderr.read()]
    return [True, process.stdout.read()]

def compress_directory(in_dir, out_file):
    import zipfile
    zip_file = zipfile.ZipFile(out_file, 'w')
    for root, _, files in os.walk(in_dir):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(full_path, in_dir)
            zip_file.write(full_path, rel_path)
    zip_file.close()

class FilesystemObject(object): 
    """ Single object in the filesystem. """

    def __init__(self, absolute_path, relative_path, is_directory=False):
        self.absolute_path = absolute_path
        self.relative_path = relative_path
        self.base_name = os.path.basename(relative_path)
        self.is_directory = is_directory
        self.children = []        
        
    def flatten(self):
        """ Iterate over directory heirarchy and return single list of all files """
        result = []
        self.__flatten_aux(self, result)
        return result
        
    def __flatten_aux(self, node, result):
        """ Helper function for flatten """
        for child in node.children:
            if child.is_directory:
                self.__flatten_aux(child, result)
            else:
                result.append(child)

    def __delete_aux(self, fso):
        """ Helper function for delete """
        if fso.is_directory:
            for child in fso.children:
                self.__delete_aux(child)
            os.rmdir(fso.absolute_path)
        else:
            # make sure the path is not read only otherwise the remove() call will fail
            import stat
            os.chmod(fso.absolute_path, stat.S_IWRITE)
            os.remove(fso.absolute_path)

    def delete(self):
        """ If this object is a file then delete the file, otherwise delete
        the contents of this directory and all underneath and remove them"""
        if self.is_directory:
            for child in self.children:
                self.__delete_aux(child)
        else:
            self.__delete_aux(self)



def get_directory_tree(src_path):
    """
    Recursively get the contents of a directory.

    Returns:
        Object(FilesystemObject)
    """        
    root = FilesystemObject(src_path, '', is_directory=True)
    __get_directory_tree_aux(src_path, root)
    return root
    
def __get_directory_tree_aux(root_dir, parent):
    """ Helper function for get_directory_tree """
    names = os.listdir(parent.absolute_path)
    for name in names:
        is_directory = False
        absolute_path = os.path.join(parent.absolute_path, name)
        relative_path = os.path.relpath(absolute_path, root_dir) 
        if os.path.isdir(absolute_path):
            is_directory = True
        node = FilesystemObject(absolute_path, relative_path, is_directory)
        if is_directory:
            __get_directory_tree_aux(root_dir, node)

        parent.children.append(node)                                    
        
#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
