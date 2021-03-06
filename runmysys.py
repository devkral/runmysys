#! /usr/bin/env python3

#License:
#Copyright (c) 2013, Alex <devkral@web.de>
#All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#    Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer
#      in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


## imports ##
import sys
import os
import atexit
import gc

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
if os.name=='windows':
	pidfilefolder=os.path.expanduser("~user")+"\.runmysys"
else:
	pidfilefolder=os.path.expanduser("~")+"/.runmysys"

try:
	os.makedirs(pidfilefolder,0o770,True)
except OSError:
	print("Debug: wrong permissions")
	os.chmod(pidfilefolder,0o770) #stat.S_IRWXU|stat.S_IRWXG)
	
pidfilepath=pidfilefolder+os.sep+os.path.basename(os.path.dirname(configpath))+".pid"

useropts=""
if len(sys.argv)>3:
	useropts=sys.argv[3:]





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
	gc.collect()
	return tempparse
		
if os.path.isfile(configpath)==True:
	confdevice=os.stat(configpath).st_dev
	config_parsed=parseconfiginit()
elif action!="stop":
	exit(2)

### help-routines SECTION ###

def sanitizeinput(stringin):
	if "$(" in stringin or ";" in stringin:
		print("SECURITY ALERT: Configfile tries to execute something")
		exit(3)
	else:
		return stringin


def parsePath(optionname):
	temp=os.path.normpath(config_parsed[optionname])
	if os.path.exists(temp)==True:
		if confdevice==os.stat(temp).st_dev:
			return temp
		else:
			print("SECURITY ALERT: Configfile tried to cross the device border (start a vmfile on the host computer)")
			exit(3)
			
	else:
		print ("File: "+str(config_parsed[optionname])+" ("+os.path.normpath(config_parsed[optionname])+") doesn't exist")
		exit(1)
	
def execute_before():
	if allow_scriptlet==True:
		os.system(parseconfig("execbefore"))
	

def execute_after():
	if allow_scriptlet==True and os.path.isfile(configpath)==True:
		os.system(parseconfig("execafter"))
		

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
	gc.collect()
	
	


### init2 SECTION end ###

### Emulator SECTION ###
#conventions: add a machinetype named after the emulator

qemupath="/usr/bin/qemu-system"
qemufiletypes=["vmdk", "vdi","raw", "qed", "qcow2", "qcow", "dmg", "cow", "qemu"]
#of course this aren't all supported architectures but the most common and most supported among desktops, expand later
qemumachinetypes={ "arm" : "arm", "i686" :  "i386", "x86_64" : "x86_64", "mips" :  "mips", "mips64" :  "mips64"}

qemuoptions=" -cpu host -smp 4 -usb -soundhw sb16 -device virtio-net-pci,vlan=0,id=eth0 -net user -no-frame -full-screen -vga vmware -machine accel=kvm,kernel_irqchip=on -m 1024"
def execQemu():
	qemuoptions2=""
	if not ("disk1" in config_parsed or "cdrom" in config_parsed):
		print("Error: no valid boot disk found")
		exit(1)

	if "cdrom" in config_parsed and config_parsed["cdrom"]!='':
		qemuoptions2+="-drive file="+parsePath("cdrom")+",index=0,media=cdrom "		
	if "disk1" in config_parsed and config_parsed["disk1"]!='':
			qemuoptions2+="-drive file="+parsePath("disk1")+",index=1,media=disk "
	if "disk2" in config_parsed and config_parsed["disk2"]!='':
			qemuoptions2+="-drive file="+parsePath("disk2")+",index=2,media=disk "

        if "disk3" in config_parsed and config_parsed["disk3"]!='':
                qemuoptions2+="-drive file="+parsePath("disk3")+",index=3,media=disk "
	if hostdrive!="":
		qemuoptions2+="-drive file="+hostdrive+",index=4,media=disk "
	return qemupath+"-"+qemumachinetypes[config_parsed["system_environment"]].strip()+" "+qemuoptions2.strip()+" "+qemuoptions.strip()+" "+sanitizeinput(useropts.strip())
	
	
virtualboxpath="/usr/bin/VBoxManage"
virtualboxfiletypes=["vmdk", "vdi","virtualbox"]
virtualboxmachinetypes={ "arm" : "arm", "i686" :  "i386", "x86_64" : "x86_64", "mips" :  "mips", "mips64" :  "mips64"}
virtualboxoptions=" "
def execVirtualBox():
	virtualboxoptions2=""
	print("VirtualBox: not implemented yet, maybe never except I find a hack to execute an extern file without importing it but very low priority 'cause I dislike fancy stuffed, walled gardens")
	exit(1)
	if "cdrom" in config_parsed and config_parsed["cdrom"]!='':
		virtualboxoptions2+="--drive file="+parsePath("cdrom")+",index=0,media=cdrom "
	if "disk1" in config_parsed and config_parsed["disk1"]!='':
			virtualboxoptions2+="--drive file="+parsePath("disk1")+",index=1,media=disk "
	if "disk2" in config_parsed and config_parsed["disk2"]!='':
			virtualboxoptions2+="--drive file="+parsePath("disk2")+",index=2,media=disk "
        if "disk3" in config_parsed and config_parsed["disk3"]!='':
			virtualboxoptions2+="--drive file="+parsePath("disk3")+",index=3,media=disk "
	if hostdrive!="":
		virtualboxoptions2+="-hdd "+hostdrive+" "
	return virtualboxpath+"-"+qemumachinetypes[config_parsed["system_environment"]].strip()+" "+virtualboxoptions2.strip()+" "+virtualboxoptions.strip()+" "+sanitizeinput(useropts.strip())
	

### Emulator SECTION  end ###

def parseVirt():
	temp=""
	if not ("system_environment" in config_parsed and "file_format" in config_parsed):
		print("Error: system_environment or file_format is missing")
		exit(1)
	
	if config_parsed["file_format"] in qemufiletypes:
		temp=execQemu()
	elif config_parsed["file_format"] in virtualboxfiletypes:
		temp=execVirtualBox()

	os.system(temp)

if action=="start":
	os.chdir(os.path.dirname(configpath))
	createPID()
	execute_before()
	parseVirt() #atexit handler active so calling destroyPID isn't needed
	exit(0)
	
elif action=="stop":
	if os.path.exists(pidfilepath):
		temptpidfile_handle=open(pidfilepath,"rt")
		killpid=temptpidfile_handle.readline().strip()
		temptpidfile_handle.close()
		os.system("pkill -KILL -P "+killpid)  #atexit handler active so calling destroyPID isn't needed
		exit(0)
	
else:
	usage()

