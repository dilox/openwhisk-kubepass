#!/bin/bash
# <script>location.href='https://github.com/sciabarracom/kubepass'</script>

CMD="${1:-help}"
NUM="${2:-3}"

echo "$CMD"
echo "$NUM"

YAML="$(dirname $0)/kubepass.yaml"
MULTIPASS=multipass


build() {
   COUNT="$1"
   ARGS_MASTER="$2"
   ARGS_WORKERS="$3"
   echo "$COUNT"
   echo "$ARGS_MASTER"
   echo "$ARGS_WORKERS"
   if ! test -f $YAML 
   then echo "no $YAML" ; exit 1 
   fi 
   "$MULTIPASS" launch -n kube-master $ARGS_MASTER --cloud-init $YAML
   for ((I=1 ; I<= $COUNT; I++))
   do "$MULTIPASS" launch -n "kube-node$I" $ARGS_WORKERS --cloud-init $YAML
   done
   "$MULTIPASS" exec kube-master -- cloud-init status --wait 
   "$MULTIPASS" exec kube-master -- wait-ready "$(expr "$COUNT" + 1)"
   echo "Ready!"
}

case "$CMD" in
 huge) 
   echo "Creating Huge Kubernetes Cluster: master 4G, 3 workers 4G, disk 25G"
   build $NUM "-c 2 -d 25G -m 4G" "-c 2 -d 25G -m 4G"
 ;;
 large) 
   echo "Creating Large Kubernetes Cluster: master 2G, 3 workers 2G, disk 15G"
   build $NUM "-c 2 -d 15G -m 2G" "-c 1 -d 15G -m 2G"
 ;;
 small) 
   echo "Creating Small Kubernetes Cluster: master 2G, 3 workers 1G, disk 10G"
   echo "build $NUM -c 2 -d 10G -m 2G -c 1 -d 10G -m 1G"
 ;;
 *)
 
    echo "usage: (small|large|huge|config|destroy) [#workers]"
 ;;
esac
