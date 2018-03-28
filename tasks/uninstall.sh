#!/bin/bash

python setup.py develop --uninstall
rm -rf *.egg*
rm ./gitml/*.pyc