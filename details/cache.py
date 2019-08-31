#-----------------------------------------------------------------------------
# Darkstorm Library
# Copyright (C) 2018 Martin Slater
# Created : Tuesday, 06 February 2018 05:38:38 PM
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
import json
import time
import os.path as path
import random
from os import makedirs
from details.utils.misc import ensure_valid_pathname
from details.utils.file import get_directory_tree

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------

class Cache(object):
    """ Cache """

    def __init__(self, context):
        """ Constructor """
        self.__context = context
        self.__cache_dir = path.join(context.temp_dir, 'cache')

        if not path.exists(self.__cache_dir):
            makedirs(self.__cache_dir)

    def __make_cache_path(self, name):
        return path.join(self.__cache_dir, ensure_valid_pathname(name) + '.json')

    def clear(self):
        """ Delete everything from the cache directory """
        tree = get_directory_tree(self.__cache_dir)
        tree.delete()

    def load_from_cache(self, name):
        cache_path = self.__make_cache_path(name)
        if not path.exists(cache_path):
            return None

        with open(cache_path, 'rt') as json_file:
            json_str = json_file.read()
            obj = json.loads(json_str)
            cur_time = int(time.time())
            if cur_time > obj['cache_expiry']:
                # cache has expired
                return None
            return obj['object']

        return None

    def save_to_cache(self, obj, name, expiry_seconds, random_jitter=None):
        """ Save an object to the cache.

        Args:
            obj(object)          : Object to save, must be serializable to json
            name(string)         : Name of the object on disk
            expiry_seconds(int)  : Number of seconds before the cache expires
            random_jitter(float) : Percentage of expiry seconds +/- to randomly jitter the expiry time.
                                   This can be used to avoid many cache items expiring simulataneously.
        """
        if random_jitter:
            jitter_range = int(expiry_seconds * random_jitter)
            jitter_seconds = random.randrange(jitter_range * 2) - jitter_range
            expiry_seconds += jitter_seconds

        cache_path = self.__make_cache_path(name)
        cache_obj = {
            "cache_expiry": int(time.time()) + expiry_seconds,
            "object": obj
        }
        json_str = json.dumps(cache_obj, indent=4, separators=(',', ': '))
        with open(cache_path, 'w+t') as json_file:
            json_file.write(json_str)





#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

def main():
    """ Main script entry point """
    pass

if __name__ == "__main__":
    main()
