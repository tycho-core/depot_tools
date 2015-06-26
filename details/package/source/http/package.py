#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2015 Martin Slater
# Created : Tuesday, 03 February 2015 11:44:42 AM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from details.package.package_base import PackageBase
from details.package.package_info import PackageInfo
from details.depends import Dependency
from details.utils.misc import log
import details.utils.file as futils
import os.path

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Package(PackageBase):
    """ Package """
    
    def __init__(self, provider, pkg_name, pkg_version):
        super(Package, self).__init__(provider, pkg_name, pkg_version)   
            
    def get_package_info(self, refresh=True):
        """ Returns the info for this package """
        return self.provider.get_package_info(self, refresh)

    def checkout(self, local_dir):
        provider = self.provider

        # get the file list for this package
        pkg_info = self.get_package_info()
        pkg_type = pkg_info.get_option('type')

        if not pkg_type:
            pkg_type = 'archive'

        assert pkg_type == 'archive'

        if pkg_type == 'archive':
            archive_name = pkg_info.get_option('archive_name')
            assert archive_name != None
            archive_path = provider.cache_package_file(self, archive_name, True)
            _, ext = os.path.splitext(archive_path)

            decompress_handlers = {
                '.7z'  : self.__extract_7zip,
                '.zip' : self.__extract_zip
            }
            if not ext in decompress_handlers:
                print 'noext' 
                return False

            self.provider.context.console.update_sub_task('Extracting')
            decompress_handlers[ext](archive_path, local_dir)

        # append version to packing info file and save
        src_path = provider.cache_package_file(self, provider.context.package_info_filename, True)
        local_pkg_info = PackageInfo.create_from_json_file(src_path)
        local_pkg_info.add_option('remote_version', provider.make_pkg_url(self.name, self.version))
        this_version = Dependency(provider.source_name, self.name, self.version)
        local_pkg_info.add_option('version', str(this_version))
        dst_path = os.path.join(local_dir, provider.context.package_info_filename)
        local_pkg_info.save_to_json_file(dst_path)
        return True



    def __extract_7zip(self, src, dst):
        """ Extract a 7zip file """
        path = self.provider.context.filesystem_mappings.find_file('@{ty_hub_bin_tools}/7zip', 
                                                                   '7za', 
                                                                   ['', '.exe'])
        if not path:
            return False

        futils.extract_7z_file(path, src, dst)

    def __extract_zip(self, src, dst):
        """ Extract a zip file """
        futils.extract_file('', src, dst)    

    def update(self, local_dir):
        """
        Update the package to the latest version
        """
        pass

    def change_version(self, local_dir, force):
        status = self.local_filesystem_status(local_dir)
        update = False
        if not status.is_installed():
            update = True

        if status.get_version() != self.version:
            update = True

        if update:
            # need to delete current version and get new one
            tree = futils.get_directory_tree(local_dir)
            if tree:
                log("Removing %s" % (local_dir))
                tree.delete()
            return self.checkout(local_dir)

        return True

    def local_filesystem_status(self, local_dir):
        """
        Returns:
            PackageBase.Status : Status of package in local filesystem
        """
        installed = False
        valid = False
        modified = False
        version = None
        modifications = None
        raw_modifications = None

        pkg_info_path = os.path.join(local_dir, self.provider.context.package_info_filename)
        if os.path.exists(local_dir) and os.path.exists(pkg_info_path):
            installed = True

            info = PackageInfo.create_from_json_file(pkg_info_path)
            if info and info.has_option('version'):
                version_str = info.get_option('version')
                deps = Dependency.create_from_string(version_str)
                if len(deps.children) == 1:
                    dep = deps.children[0]
                    if dep.name == self.name:
                        version = dep.branch
                        valid = True

        return PackageBase.Status(installed, valid, modified, version, 
                                  modifications, raw_modifications)

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
