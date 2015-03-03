#!/bin/bash
TYCHO_DEPOT_TOOLS_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

alias tyhub="python ${TYCHO_DEPOT_TOOLS_PATH}/../tyhub.py"
alias tyworkspace="python ${TYCHO_DEPOT_TOOLS_PATH}/../tyworkspace.py"
alias tycreate="python ${TYCHO_DEPOT_TOOLS_PATH}/../tycreate.py"
alias tyformat="python ${TYCHO_DEPOT_TOOLS_PATH}/../tyformat.py"
alias tyinit="python ${TYCHO_DEPOT_TOOLS_PATH}/../tyinit.py"
