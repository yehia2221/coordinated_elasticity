#from __future__ import print_function
import sys
import libvirt
import threading    
#from multiprocessing import Process
#import os
import psutil
#import commands
import multiprocessing
import time
#import json
#import logging
import subprocess as sub

#from pyVim import connect
#from pyVim.connect import SmartConnect, Disconnect
#import ssl
#from pyVmomi import vim
#from pyVmomi import vmodl
#from pyVim.task import WaitForTask
#import atexit
#import sys

class ElasticVM:

	def __init__(self, vcores_number=None, mem_total=None):
		self.vcores_number = vcores_number
		self.mem_total = mem_total
		self.initiane_values()
		self.loglock=threading.Lock() 

        def initiane_values(self):
		self.vcores_number = multiprocessing.cpu_count()
		ram_t = "free -m |awk  \'/^Mem:/{print $2}\'"
		mem_total1 = float(sub.check_output(ram_t, shell=True))
		if mem_total1 < 512:
			self.mem_total = 512
		elif mem_total1 < 1024:
			self.mem_total = 1024
		elif mem_total1 < 1536:
			self.mem_total = 1536
		elif mem_total1 < 2048:
			self.mem_total = 2048
		elif mem_total1 < 2560:
			self.mem_total = 2560
		elif mem_total1 < 3072:
			self.mem_total = 3072
		elif mem_total1 < 3584:
			self.mem_total = 3584
		elif mem_total1 < 4096:
			self.mem_total = 4096
		


        def cpu_usage(self):
                cpu_percent = psutil.cpu_percent(interval=1)
                return cpu_percent
        def mem_usage(self):
                #mem_percent = psutil.virtual_memory().used/1048576
                mem_percent = psutil.virtual_memory().percent
                return mem_percent

        def _readline(self, filename) :
                fh = open(filename, 'r')
                result = fh.readline()
                fh.close()
                return result

        def _write(self, filename, content):
                fh = open(filename, 'w')
                fh.write(content) 
                fh.close()
                pass
	def _inial_avaialbleCPUs(self) :
                cpuinfo = sub.check_output('cat /proc/cpuinfo | grep -i processor |  awk \'{ print $3}\'' , shell=True).strip()
                #print cpuinfo
                cpu_list =  cpuinfo.split('\n')
                cpu_list = [ int(x) for x in cpu_list ]
		return cpu_list

        def cpusetToList(self,str):
                _cpu_list = []
                for cpu  in str.split(","):
                        if '-' in cpu :
                                left_num,right_num = cpu.split('-')
                                _cpu_list.extend(range(int(left_num),int(right_num)+1))
                        else :
                                _cpu_list.append(int(cpu))
                return _cpu_list

	def add_cpu(self, dom, vcpu_nu):
		#print(vcpu_nu)
		print "Number of Vcores  will be increassed"
		cpu_list = self._inial_avaialbleCPUs() # get the availble list of vcpus on that vm 
		time.sleep(10)	
		self.loglock.acquire() 
		dom.setVcpus(vcpu_nu)  # increase Vcpus
		self.loglock.release() 
		print('Now, no. of vcpus become', + vcpu_nu)
		time.sleep(10)
		cpu_list2 = self._inial_avaialbleCPUs() #get the lsit of vcpus after increase
		added_cpu = [a for a in cpu_list+cpu_list2 if (a not in cpu_list) or (a not in cpu_list2)] # find the id of the added vcpu (difference between the two lists)
		path1 = "/sys/fs/cgroup/cpuset/docker/cpuset.cpus"
		c1 = self._readline(path1) # get cpus in docker daemon
		_cores_docker_daemon = self.cpusetToList(c1)
		_cores_docker_daemon.extend(added_cpu)
		self.loglock.acquire() 
		self._write(path1, ",".join(str(x) for x in _cores_docker_daemon)) # update vcpus in docker daemon
		self.loglock.release
        def remove_cpu(self, dom, vcpu_nu):
		print(vcpu_nu)
		print "Number of Vcores will be decresaezd"
		time.sleep(40)
		dom.setVcpusFlags(vcpu_nu, libvirt.VIR_DOMAIN_VCPU_GUEST)
		print('Now, no. of vcpus become', + vcpu_nu)

        def cpu_resize(self, dom, vcpu_nu):
            while True:
                if float(self.cpu_usage()) > 90:
			vcpu_nu = vcpu_nu + 1 
			self.add_cpu(dom, vcpu_nu)

                if float(self.cpu_usage()) < 70 and vcpu_nu > 1: 
			vcpu_nu = vcpu_nu - 1 
			self.remove_cpu(dom, vcpu_nu)                        
	
	def add_mem(self, dom, mem_size):
		print(mem_size/1024)
 		print "The memory size will be increassed"
		time.sleep(20)
		self.loglock.acquire()
		dom.setMemory(mem_size) # add memory in kilobytes
		self.loglock.release()
		print('Now, memory size in MB become', + mem_size/1024)

	def remove_mem(self, dom, mem_size):
		print "the memory size will be decresaezd"
		print(mem_size/1024)
		time.sleep(40)
		dom.setMemory(mem_size)
		print('Now, memory size in MB become', + mem_size/1024)
       
	def mem_resize(self, dom, mem_size):
            while True:
                if float(self.mem_usage()) > 90:
			mem_size = mem_size + 524288 # + 512M 
			self.add_mem(dom, mem_size)
                if float(self.mem_usage()) < 70 and mem_size > 1048576: #  524288:
			mem_size = mem_size -  262144 #524288 
			self.remove_mem(dom, mem_size)

	def connect(self, id=instance_id):
		try:
			conn=libvirt.open("qemu+ssh://root@172.16.225.148/system")
			dom = conn.lookupByID(id)
			if dom == None:
				exit(1)
			vcpu_nu = self.vcores_number 
			mem_size = self.mem_total * 1024
                	#self.cpu_resize(dom, vcpu_nu)
                	#self.add_cpu(dom,vcpu_nu)
                	conn.close()
		except Exception as e:
                	raise e
		return dom, vcpu_nu, mem_size

if __name__ == '__main__':
	inst11 = ElasticVM()
#print ('number of current vcores:', + inst11.vcores_number)
#print ('memory size in MB:',  inst11.mem_total)
#print(inst11.cpu_usage())
#print(inst11.mem_usage())

#try:
#	conn=libvirt.open("qemu+ssh://root@172.16.225.148/system")
#	print("connection succeeded:connection to qemu:///system")
#except:
#        print("connection failed")
#id = 18
#dom = conn.lookupByID(id)
#if dom == None:
#    print('Failed to find the domain '+domName)
#    #print('Failed to find the domain '+domName, file=sys.stderr)
#    exit(1)
#print(dom)
#vcpu_nu = inst11.vcores_number 
#mem_size = inst11.mem_total * 1024 
#inst11.cpu_resize(dom, vcpu_nu)
##inst11.mem_resize(dom, mem_size)
#conn.close()
#exit(0)
