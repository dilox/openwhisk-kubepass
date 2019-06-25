import argparse
parser = argparse.ArgumentParser(description='Create you kube cluster')
parser.add_argument("size", help="<size of the cluster>", choices=['small','large','huge'])
parser.add_argument("count", nargs="?", type=int, help="<master-count> <worker-count>...", default="3")

args = parser.parse_args()

print(args.size)
print(args.count)
 