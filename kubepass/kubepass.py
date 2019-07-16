#!/usr/bin/env python

import argparse
import os
import sys
import shutil

# usage: python kubepass.py [-h] {small,large,huge,destroy} [{1,2,3,4,5}]

parser = argparse.ArgumentParser(description='Create you kube cluster')
parser.add_argument("size",
                    help="<size of the cluster>",
                    choices=['small', 'large', 'huge', 'destroy'])
parser.add_argument("count",
                    nargs="?",
                    type=int,
                    help="<worker-count>",
                    default="3",
                    choices=range(1, 6))
parser.add_argument("-d",
                    "--dashboard",
                    help="<deploy Web UI Dashboard>",
                    action="store_true")

parser.add_argument("-r",
                    "--rook",
                    help="<deploy rook>",
                    action="store_true")

args = parser.parse_args()

size = (args.size)
count = (args.count)

# controllo che sia installato multipass e aggiungo multipass.exe al $PATH
WINMULTIPASS = "c:"+os.sep+"Program Files"+os.sep+"Multipass"
MULTIPASS = "multipass.exe"

if os.name == 'nt':
    if os.path.isdir(WINMULTIPASS):
        os.environ["PATH"] += os.pathsep + WINMULTIPASS + os.sep + "bin"

# if not os.path.isfile(WINMULTIPASS+os.sep+"bin"+os.sep+MULTIPASS):
command = 'multipass'
if shutil.which(command) is None:
    print("Install multipass 0.7.0, please.")
    print("https://github.com/CanonicalLtd/multipass/releases/tag/v0.7.0")
    sys.exit(1)


# controlla che esista file kubepass.yaml

YAML = "kubepass.yaml"
if not os.path.isfile(YAML):
    print("no "+YAML)
    sys.exit(1)


def build(COUNT, ARGS_MASTER, ARGS_WORKERS):
    os.system(MULTIPASS+" launch -n kube-master " +
              ARGS_MASTER+" --cloud-init "+YAML)
    for i in range(1, COUNT+1):
        NODE = "kube-node"+str(i)
        os.system(MULTIPASS+" launch -n "+NODE+" " +
                  ARGS_WORKERS+" --cloud-init "+YAML)
    os.system(MULTIPASS+" exec kube-master -- cloud-init status --wait")
    os.system(MULTIPASS+" exec kube-master -- wait-ready "+str(COUNT+1))

    # nel caso venga specificata l'opzione --dashboard, viene deployata anche la web ui
    if args.dashboard == True:
        print("Install Web Ui Dashboard")
        os.system(
            "kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0-beta1/aio/deploy/recommended.yaml")

    # nel caso venga specificata l'opzione --rook viene deployato anche root
    if args.rook == True:
        print("Install rook")
        ROOK = "https://raw.githubusercontent.com/rook/rook/release-0.9/cluster/examples/kubernetes/ceph"
        os.system("kubectl apply - f "+ROOK+"/operator.yaml")
        os.system("kubectl apply - f "+ROOK+"/cluster.yaml")
        os.system("kubectl apply - f "+ROOK+"/cluster.yaml")
        os.system(
            "kubectl patch storageclass rook-ceph-block - p '{\"metadata\": {\"annotations\":{\"storageclass.kubernetes.io/is-default-class\":\"true\"}}}'")
        print("Ready!")


def destroy(COUNT):
    print("Deleting kube-master")
    os.system(MULTIPASS+" -v delete kube-master")
    for i in range(1, COUNT+1):
        NODE = "kube-node"+str(i)
        print("Deleting kube-worker"+str(i))
        os.system(MULTIPASS+" delete "+NODE)
    os.system(MULTIPASS+" -v purge")


def are_you_sure():
    answer = input("are you sure? (y/n) ")
    if answer[0].lower() != 'y':
        exit()


if size == 'small':
    print("Creating Small Kubernetes Cluster: master 2G, %s workers 1G, disk 10G" % count)
    build(count, "-c 2 -d 10G -m 2G", "-c 1 -d 10G -m 1G")

if size == 'large':
    print("Creating Large Kubernetes Cluster: master 2G, %s workers 2G, disk 15G" % count)
    build(count, "-c 2 -d 15G -m 2G", "-c 1 -d 15G -m 2G")

if size == 'huge':
    print("Creating Huge Kubernetes Cluster: master 4G, %s workers 4G, disk 25G" % count)
    build(count, "-c 2 -d 25G -m 4G", "-c 2 -d 25G -m 4G")

if size == 'destroy':
    print("Destroying the cluster")
    are_you_sure()
    destroy(count)
