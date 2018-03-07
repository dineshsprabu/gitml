#!/bin/bash

python setup.py develop --uninstall
rm -rf *.egg*
rm ./versionml/*.pyc