#!/bin/bash

# Installs caroline in develop mode

set -e

su - caroline -c "(cd /home/caroline/src/caroline; python setup.py develop --user)"

# Eof


