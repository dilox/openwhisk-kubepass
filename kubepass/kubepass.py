#!/usr/bin/env python

import argparse
import os

parser = argparse.ArgumentParser(description='Create you kube cluster')
parser.add_argument("size",
    help="<size of the cluster>",
    choices=['small','large','huge'])
parser.add_argument("count",
    nargs="?",
    type=int,
    help="<worker-count>",
    default="3")

args = parser.parse_args()

print(args.size)
print(args.count)


if os.name == 'nt':
    WINMULTIPASS="c:\\Program Files\\Multipass"
    MULTIPASS="multipass.exe"
    if os.path.isdir(WINMULTIPASS):
        os.environ["PATH"] += os.pathsep + WINMULTIPASS + "\\bin"

    if not os.path.isfile(WINMULTIPASS+"\\bin\\"+MULTIPASS):
        print("Install multipass 0.7.0, please.")
        print("https://github.com/CanonicalLtd/multipass/releases/tag/v0.7.0")








 