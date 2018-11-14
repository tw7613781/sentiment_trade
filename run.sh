#!/bin/sh

# define work repository
path=$(dirname "$0")

cd $path

. env/bin/activate

python main.py