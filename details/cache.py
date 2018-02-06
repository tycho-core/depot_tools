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
from os import makedirs
from utils.misc import ensure_valid_pathname

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

    def load_from_cache(self, name):
        cache_path = path.join(self.__cache_dir, ensure_valid_pathname(name) + '.json')
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

    def save_to_cache(self, obj, name, expiry_seconds):
        cache_path = path.join(self.__cache_dir, ensure_valid_pathname(name) + '.json')
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
