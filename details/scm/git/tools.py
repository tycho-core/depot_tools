#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Monday, 09 February 2015 12:55:41 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.utils.misc import execute
from details.utils.file import extract_file, get_directory_tree
import tempfile
import uuid
import re
import os

#-----------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------


def is_installed():
    """ Checks to see if git is callable with the current environment """
    exitcode, _, _ = execute('git', os.getcwd(), ['--version'], capture=False)
    return exitcode == 0

def has_credential_helper():
    """ If operating over http or https then user needs to input their username 
    and password for each remote git op, this checks to see if they have installed
    a helper to avoid this """
    config = global_git_config()

    if not config:
        return False

    if 'credential.helper' in config:
        return len(config['credential.helper']) > 0

    return False
    
def global_git_config():
    """ Returns a dictionary representing the global git config """
    exitcode, output, _ = execute('git', os.getcwd(), ['config', '--global', '-l'], capture=True)
    if exitcode != 0:
        return None

    # parse output in form key=value
    regex = r'(?P<key>.+)=(?P<value>.+)'    
    result_dict = {}
    for match in re.finditer(regex, output):
        result_dict[match.group('key')] = match.group('value')

    return result_dict

def get_archive(repo, treeish, path, outfile):
    """ Runs git archive on a repo to get files without requiring cloning """
    remote = '--remote=' + repo
    exitcode, _, _ = execute('git', os.getcwd(), ['archive', remote, treeish, path, '-o', outfile])
    return exitcode == 0

def get_archive_file(repo, treeish, path):
    """ Get a single file contents from a git repo.
    Returns:
        string : Contents if successful of None otherwise.
    """
    tar_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()) + '.tar')
    res = get_archive(repo, treeish, path, tar_path)
    contents = None
    if res:
        tar_dir = tar_path + '.dir'
        os.mkdir(tar_dir)
        import tarfile
        tf = tarfile.TarFile(tar_path)
        tf.extractall(tar_dir)
        tf.close()
        files = os.listdir(tar_dir)
        if len(files) == 1:
            with open(os.path.join(tar_dir, files[0]), 'r') as content_file:
                contents = content_file.read()

        if os.path.exists(tar_path):
            os.remove(tar_path)

        if os.path.exists(tar_dir):
            tree = get_directory_tree(tar_dir)
            tree.delete()

    return contents




#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
