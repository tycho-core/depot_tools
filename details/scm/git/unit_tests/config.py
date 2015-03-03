#-----------------------------------------------------------------------------
# Tycho Library
# Copyright (C) 2014 Martin Slater
# Created : Friday, 05 December 2014 03:09:25 PM
#-----------------------------------------------------------------------------
#pylint: disable=C0111
#pylint: disable=R0201
#pylint: disable=R0903

#-----------------------------------------------------------------------------
# Class
#-----------------------------------------------------------------------------
from details.utils.url import Url

class Config(object):
    """ Various constants for git module testing """
    test_repos = ['hubTestProj1']
    github_auth_token = "c42149b432652d992a122ee09f720f1e344e9b98"   
    github_organization = "AcmeHub"
    username = 'test-hub'
    password = 'l1cens3'
    test_repo_name = 'hubTestProj1'
    test_branch_name = 'branch1'
    test_host = 'https://github.com/AcmeHub'
    test_repo_url = '%s/%s.git' % (test_host, test_repo_name)
    test_repo_invalid_url = '%s/Idontexist.git' % (test_host)
