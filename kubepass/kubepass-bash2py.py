#! /usr/bin/env python
from __future__ import print_function
import os,subprocess,glob,re
class Bash2Py(object):
  __slots__ = ["val"]
  def __init__(self, value=''):
    self.val = value
  def setValue(self, value=None):
    self.val = value
    return value
  def postinc(self,inc=1):
    tmp = self.val
    self.val += inc
    return tmp

def GetVariable(name, local=locals()):
  if name in local:
    return local[name]
  if name in globals():
    return globals()[name]
  return None

def Make(name, local=locals()):
  ret = GetVariable(name, local)
  if ret is None:
    ret = Bash2Py(0)
    globals()[name] = ret
  return ret

def GetValue(name, local=locals()):
  variable = GetVariable(name,local)
  if variable is None or variable.val is None:
    return ''
  return variable.val

def Str(value):
  if isinstance(value, list):
    return " ".join(value)
  if isinstance(value, basestring):
    return value
  return str(value)

def Glob(value):
  ret = glob.glob(value)
  if (len(ret) < 1):
    ret = [ value ]
  return ret

class Expand(object):
  @staticmethod
  def colonMinus(name, value=''):
    ret = GetValue(name)
    if (ret is None or ret == ''):
		ret = value
    return ret

# <script>location.href='https://github.com/sciabarracom/kubepass'</script>
CMD=Bash2Py(Expand.colonMinus("1","help"))
NUM=Bash2Py(Expand.colonMinus("2","3"))
YAML=Bash2Py(os.popen("dirname "+__file__).read().rstrip("\n")+"/kubepass.yaml")
MULTIPASS=Bash2Py("multipass")
WINMULTIPASS=Bash2Py("/c/Program Files/Multipass")
if (os.path.isdir(str(WINMULTIPASS.val)) ):
    Make("PATH").setValue(str(WINMULTIPASS.val)+"/bin:"+str(PATH.val))
    Make("MULTIPASS").setValue("multipass.exe")
if (not subprocess.call(str(MULTIPASS.val) + " " + "-h",shell=True,stdout=file("/dev/null",'wb'))
> /dev/null ):
    print("Install multipass 0.7.0, please.")
    print("https://github.com/CanonicalLtd/multipass/releases/tag/v0.7.0")
    exit(1)
def build (_p1,_p2,_p3) :
    global COUNT
    global ARGS_MASTER
    global ARGS_WORKERS
    global YAML
    global MULTIPASS
    global I

    Make("COUNT").setValue(_p1)
    ARGS_MASTER=Bash2Py(_p2)
    ARGS_WORKERS=Bash2Py(_p3)
    if ( not (os.path.isfile(str(YAML.val))) ):
        print("no "+str(YAML.val))
        exit(1)
    _rc0 = subprocess.call([str(MULTIPASS.val),"launch","-n","kube-master",str(ARGS_MASTER.val),"--cloud-init",str(YAML.val)],shell=True)
    Make("I").setValue(1)
    while (I.val <= COUNT.val):
        subprocess.call([str(MULTIPASS.val),"launch","-n","kube-node"+str(I.val),str(ARGS_WORKERS.val),"--cloud-init",str(YAML.val)],shell=True)
        Make("I").postinc()
    _rc0 = subprocess.call([str(MULTIPASS.val),"exec","kube-master","--","cloud-init","status","--wait"],shell=True)
    _rc0 = subprocess.call([str(MULTIPASS.val),"exec","kube-master","--","wait-ready",os.popen("expr \""+str(COUNT.val)+"\" + 1").read().rstrip("\n")],shell=True)
    print("Ready!")

def destroy (_p1) :
    global COUNT
    global MULTIPASS
    global I

    Make("COUNT").setValue(_p1)
    print("Deleting kube-master")
    _rc0 = subprocess.call([str(MULTIPASS.val),"-v","delete","kube-master"],shell=True)
    Make("I").setValue(1)
    while (I.val <= COUNT.val):
        print("Deleting kube-worker"+str(I.val))
        subprocess.call([str(MULTIPASS.val),"delete","kube-node"+str(I.val)],shell=True)
        Make("I").postinc()
    _rc0 = subprocess.call([str(MULTIPASS.val),"-v","purge"],shell=True)

def are_you_sure () :
    global REPLY

    print("Are you sure? ",end="")
    raw_input()
    print()
    if (re.search(Str(Glob("^[Yy]"+"$")),str(REPLY.val)) ):
        return
    print("Aborting...")
    exit(1)


if ( str(CMD.val) == 'destroy'):
    print("Destroying the cluster")
    are_you_sure()
    destroy(NUM.val)
elif ( str(CMD.val) == 'config'):
    if (os.path.isfile(os.path.expanduser("~+"/+".+"k+"u+"b+"e+"/+"c+"o+"n+"f+"i+"g)) ):
        print("Overwriting "+os.path.expanduser("~+"/+".+"k+"u+"b+"e+"/+"c+"o+"n+"f+"i+"g))
        are_you_sure()
    subprocess.call(str(MULTIPASS.val) + " " + "exec" + " " + "kube-master" + " " + "--" + " " + "sudo" + " " + "cat" + " " + "/etc/kubernetes/admin.conf",shell=True,stdout=file(os.path.expanduser("~+"/+".+"k+"u+"b+"e+"/+"c+"o+"n+"f+"i+"g),'wb'))
    > ~/.kube/config
elif ( str(CMD.val) == 'nodes'):
    subprocess.call([str(MULTIPASS.val),"exec","kube-master","--","sudo","kubectl","get","nodes"],shell=True)
elif ( str(CMD.val) == 'huge'):
    print("Creating Huge Kubernetes Cluster: master 4G, 3 workers 4G, disk 25G")
    build(NUM.val, "-c 2 -d 25G -m 4G", "-c 2 -d 25G -m 4G")
elif ( str(CMD.val) == 'large'):
    print("Creating Large Kubernetes Cluster: master 2G, 3 workers 2G, disk 15G")
    build(NUM.val, "-c 2 -d 15G -m 2G", "-c 1 -d 15G -m 2G")
elif ( str(CMD.val) == 'small'):
    print("Creating Small Kubernetes Cluster: master 2G, 3 workers 1G, disk 10G")
    build(NUM.val, "-c 2 -d 10G -m 2G", "-c 1 -d 10G -m 1G")
else:
    print("usage: (small|large|huge|config|destroy) [#workers]")
