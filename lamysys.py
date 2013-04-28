#! /usr/bin/env python3

#author: Alex <devkral@web.de>
#License: public domain

## imports ##
import sys
import os
import atexit

## imports-end ##
### options ###
allow_scriptlet=False # security issue
hostdrive="" #hostdefined drive

### options-end ###

### help ##
def usage():
	print (sys.argv[0]+" <action> <path to config file> [<args>]")
	print ("actions:")
	print ("start: starts a new instance")
	print ("stop: kills a running instance (if there is one)")
	sys.exit(1)


### help-end ###

### Config parser ###
# depends on help
# make sure it is the first item except help and options

if len(sys.argv)<3:
	usage()

action=sys.argv[1]
configpath=os.path.abspath(sys.argv[2])
pidfilepath=os.path.dirname(configpath)+os.sep+"lamysys.pid"

useropts=""
if len(sys.argv)>3:
	useropts=sys.argv[3:]


if os.path.exists(configpath)==False:
	exit(2)

def parseconfiginit():
	tempparse={}
	config_filehandle=open(configpath,"rt")
	tempchunk=config_filehandle.readline()
	while tempchunk!='':
		tempchunk=tempchunk.partition("#")[0]
		if '=' in tempchunk:
			tempchunk2=tempchunk.partition("=")
			tempparse[tempchunk2[0].strip()]=tempchunk2[2].strip().strip('"')
		tempchunk=config_filehandle.readline()
	config_filehandle.close()
	return tempparse
		
config_parsed=parseconfiginit()


### help-routines SECTION ###

def sanitizeinput(stringin):
	if "$(" in stringin or ";" in stringin:
		print("SECURITY ALERT: Configfile tries to execute something")
		exit(3)
	else:
		return stringin


def parsePath(optionname):
	temp=os.path.abspath(config_parsed[optionname])
	if os.path.exists(temp)==True:
		return temp
	else:
		raise ("File: "+str(config_parsed[optionname])+" doesn't exist")
	
def execute_before():
	if allow_scriptlet==True:
		os.system(os.path.abspath(parseconfig("execbefore")))
	

def execute_after():	
	if allow_scriptlet==True:
		os.system(os.path.abspath(parseconfig("execafter")))
		

### help-routines SECTION end ###

### init2 SECTION ###

def destroyPID():
	execute_after()
	if os.path.isfile(pidfilepath)==True:
		os.remove(pidfilepath)
	else:
		print("Debug: missing PIDfile")
	
	
def createPID():
	if os.path.isfile(pidfilepath)==False:
		temppid_handle=open(pidfilepath,"wt")
		temppid_handle.write(str(os.getpid()))
		temppid_handle.close()
	else:
		temppid_handle=open(pidfilepath,"rt")
		temppid2=temppid_handle.readline().strip("\n").strip()
		temppid_handle.close()
		if temppid2!="":
			if os.name=="posix":
				if os.path.exists("/proc/"+str(temppid2))==True:
					print("Error: another instance is running")
					exit(2)
		temppid_handle=open(pidfilepath,"wt")
		temppid_handle.write(str(os.getpid()))
		temppid_handle.close()
	atexit.register(destroyPID)
	
	


### init2 SECTION end ###

### Emulator SECTION ###
#conventions: add a machinetype named after the emulator

qemupath="/usr/bin/qemu-system"
qemufiletypes=["raw","qcow","qcow2" "qemu"]
qemumachinetypes={ "arm" : "arm", "x86_64" : "x86_64"}
qemuoptions=" -cpu host -smp 4 -device virtio-net-pci,vlan=0,id=eth0 -net user -vga std -machine accel=kvm,kernel_irqchip=on -m 1024"
def execQemu():
	qemuoptions2=""
	if not ("hdapath" in config_parsed or "cdrom" in config_parsed):
		print("Error: no valid boot disk found")
		exit(1)
		
	if "disk1" in config_parsed and config_parsed["disk1"]!='':
			qemuoptions2+="-hda "+parsePath("disk1")+" "
	if "disk2" in config_parsed and config_parsed["disk2"]!='':
			qemuoptions2+="-hdb "+parsePath("disk2")+" "
	if "cdrom" in config_parsed and config_parsed["cdrom"]!='':
		qemuoptions2+="-cdrom "+parsePath("cdrom")+" "
	else:
		if "disk3" in config_parsed and config_parsed["disk3"]!='':
			qemuoptions2+="-hdc "+parsePath("disk3")+" "
	if hostdrive!="":
		qemuoptions2+="-hdd "+hostdrive+" "
	return qemupath+"-"+qemumachinetypes[config_parsed["system_environment"]].strip()+" "+qemuoptions2.strip()+" "+qemuoptions.strip()+" "+sanitizeinput(useropts.strip())
	

vmwarepath="/usr/bin/qemu-system"
vmwarefiletypes=["raw","qcow","qcow2" "vmware"]
vmwaremachinetypes={ "arm" : "arm", "x86_64" : "x86_64"}
vmwareoptions=" -cpu host -smp 4 -device virtio-net-pci,vlan=0,id=eth0 -net user -vga std -machine accel=kvm,kernel_irqchip=on -m 1024"
def execVMware():
	vmwareoptions2=""
	if not ("hdapath" in config_parsed or "cdrom" in config_parsed):
		print("Error: no valid boot disk found")
		exit(1)
	
	print("VMware Not implemented yet")
	exit(1)
	if "disk1" in config_parsed and config_parsed["disk1"]!='':
			qemuoptions2+="-hda "+parsePath("disk1")+" "
	if "disk2" in config_parsed and config_parsed["disk2"]!='':
			qemuoptions2+="-hdb "+parsePath("disk2")+" "
	if "cdrom" in config_parsed and config_parsed["cdrom"]!='':
		qemuoptions2+="-cdrom "+parsePath("cdrom")+" "
	else:
		if "disk3" in config_parsed and config_parsed["disk3"]!='':
			qemuoptions2+="-hdc "+parsePath("disk3")+" "
	if hostdrive!="":
		qemuoptions2+="-hdd "+hostdrive+" "
	return vmwarepath+"-"+qemumachinetypes[config_parsed["system_environment"]].strip()+" "+vmwareoptions2.strip()+" "+vmwareoptions.strip()+" "+sanitizeinput(useropts.strip())
	
virtualboxpath="/usr/bin/qemu-system"
virtualboxfiletypes=["raw","qcow","qcow2" "virtualbox"]
virtualboxmachinetypes={ "arm" : "arm", "x86_64" : "x86_64"}
virtualboxoptions=" -cpu host -smp 4 -device virtio-net-pci,vlan=0,id=eth0 -net user -vga std -machine accel=kvm,kernel_irqchip=on -m 1024"
def execVirtualBox():
	vmwareoptions2=""
	if not ("hdapath" in config_parsed or "cdrom" in config_parsed):
		print("Error: no valid boot disk found")
		exit(1)
	
	print("VirtualBox Not implemented yet")
	exit(1)
	if "disk1" in config_parsed and config_parsed["disk1"]!='':
			qemuoptions2+="-hda "+parsePath("disk1")+" "
	if "disk2" in config_parsed and config_parsed["disk2"]!='':
			qemuoptions2+="-hdb "+parsePath("disk2")+" "
	if "cdrom" in config_parsed and config_parsed["cdrom"]!='':
		qemuoptions2+="-cdrom "+parsePath("cdrom")+" "
	else:
		if "disk3" in config_parsed and config_parsed["disk3"]!='':
			qemuoptions2+="-hdc "+parsePath("disk3")+" "
	if hostdrive!="":
		qemuoptions2+="-hdd "+hostdrive+" "
	return vmwarepath+"-"+qemumachinetypes[config_parsed["system_environment"]].strip()+" "+vmwareoptions2.strip()+" "+vmwareoptions.strip()+" "+sanitizeinput(useropts.strip())
	

### Emulator SECTION  end ###

def parseVirt():
	temp=""
	if not ("system_environment" in config_parsed and "file_format" in config_parsed):
		print("Error: system_environment or file_format is missing")
		exit(1)
	
	if config_parsed["file_format"] in qemufiletypes:
		temp=execQemu()
	elif config_parsed["file_format"] in vmwarefiletypes:
		temp=execVMware()

	os.system(temp)

if action=="start":
	createPID()
	execute_before()
	parseVirt()
	
elif action=="stop":
	if os.path.exists(pidfilepath):
		temptpidfile_handle=open(pidfilepath,"rt")
		killpid=temptpidfile_handle.readline().strip()
		temptpidfile_handle.close()
		os.system("pkill -TERM -P "+killpid)
	
else:
	usage()

