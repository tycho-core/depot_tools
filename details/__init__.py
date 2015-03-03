import sys
import os
HUB_PACKAGE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'hub-site-packages')
HUB_PACKAGE_PATH = os.path.abspath(HUB_PACKAGE_PATH)
sys.path.append(HUB_PACKAGE_PATH)
