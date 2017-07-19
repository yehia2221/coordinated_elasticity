import time
import subprocess as sub
import os
import sys
import multiprocessing
import threading
#from elasticvm import ElasticVM

class Elastic:

        ########## cpu  varaibles ###########
        #global cpu_list
        #cpu_list = ["2", "3"]

        def _inial_avaialbleCPUs(self) :
                cpuinfo = sub.check_output('cat /proc/cpuinfo | grep -i processor |  awk \'{ print $3}\'' , shell=True).strip()
		#print cpuinfo
		cpu_list =  cpuinfo.split('\n')
		cpu_list = [ int(x) for x in cpu_list ]
		li = sub.Popen(('docker', 'ps', '--no-trunc', '-q'), stdout=sub.PIPE, stderr=sub.PIPE)
		for container_id  in li.stdout.read().strip().split(os.linesep):
			cpusetpath = "/sys/fs/cgroup/cpuset/docker/"+container_id
			c1 = self._readline(cpusetpath+'/cpuset.cpus')
                        _cores = self.cpusetToList(c1) # return the cores assinged to docker as a lit of intgers
			for val in _cores:
        			if val in cpu_list:
            				cpu_list.remove(val)
            	return  cpu_list
                

        def containers_id(self):
                 li = sub.Popen(('docker', 'ps', '--no-trunc', '-q'), stdout=sub.PIPE, stderr=sub.PIPE)
                 for container_id  in li.stdout.read().strip().split(os.linesep): #strip to cut the last empty line in stdout, split to output line by line instead of char by char
                        thread=threading.Thread(target=self.cpu_resize, args=(container_id,))
                        thread.start()

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

        def cpusetToList(self,str):
                _cpu_list = []
                for cpu  in str.split(","):
                        if '-' in cpu :
                                left_num,right_num = cpu.split('-')
                                _cpu_list.extend(range(int(left_num),int(right_num)+1))
                        else :
                                _cpu_list.append(int(cpu))
                return _cpu_list

        def _read_docker_usage(self, container_id) :
                cmd = sub.Popen('docker stats --no-stream %s ' %container_id, shell=True, stdout=sub.PIPE, stderr=sub.PIPE)
                cmdout = cmd.communicate()[0]
                if (cmd.returncode != 0) :
                        sys.stderr.write('container is not running')
                        sys.exit(1)
		i = 1
		for i <=4:
                	percentagec += cmdout.split('\n')[1].split()[1][:-1]
			time.sleep(4)
                return percentagec
        pass
        def _add_vCPUs(self, cpu_percentage, no_cores_real, cpusetpath, container_id, log_cpu):
                if cpu_percentage >= 90:
			cpu_list = self._inial_avaialbleCPUs()
                        if(len(cpu_list) >=1):
                                c1 = self._readline(cpusetpath+'/cpuset.cpus')
                                _cores = self.cpusetToList(c1)
                                self.loglock.acquire()
                                _cores.append(cpu_list.pop())
                                self._write(cpusetpath+'/cpuset.cpus', ",".join(str(x) for x in _cores))
                                print("pop from list , %s" % cpu_list)
                                self.loglock.release()

                                log_cpu.write("increase : %s\n" % container_id)  # log info
                                log_cpu.write("Time : %d\n" % time.time())
                                log_cpu.write("number of cores : %d\n" % len(_cores))
                                time.sleep(10)
                        else: 
				print("hi, can not do anything for you, you have attend the VM limist")
				#elasticVM = ElasticVM()
                            	#dom, vcpu_nu, mem_size = elasticVM.connect()
				#x = int(sub.check_output('nproc --all', shell=True).strip())
				#x = x + 1
                            	#elasticVM.add_cpu(dom, x) # vm controller will add a new core to the machine, it alos will upadte docker daemon

				#cpu_list = self._inial_avaialbleCPUs()
				#c1 = self._readline(cpusetpath+'/cpuset.cpus')
                                #_cores = self.cpusetToList(c1)
                                #self.loglock.acquire()
                                #_cores.append(cpu_list.pop())
                                #self._write(cpusetpath+'/cpuset.cpus', ",".join(str(x) for x in _cores))
                                #print("pop from list , %s" % cpu_list)
                                #self.loglock.release()				
                                #log_cpu.write("increase : %s\n" % container_id)  # log info
                                #log_cpu.write("Time : %d\n" % time.time())
                                #log_cpu.write("number of cores : %d\n" % len(_cores))
                                #time.sleep(1)


        def _remove_vCPUs(self, cpu_percentage, no_cores_real, cpusetpath, container_id,log_cpu):
                cpu_list = self._inial_avaialbleCPUs()
		if cpu_percentage <= 70 and no_cores_real > 1 :
                        #c11=open(cpusetpath+'/cpuset.cpus', 'w+')
                        c11 = self._readline(cpusetpath+'/cpuset.cpus')
                        cores = self.cpusetToList(c11)
                        pop_core = cores.pop()
                        self._write(cpusetpath+'/cpuset.cpus', ",".join(str(y) for y in cores))
                        self.loglock.acquire()
                        cpu_list.append(pop_core)
                        print("append to cpu_list idle +1 ",cpu_list)
                        self.loglock.release()
                        time.sleep(1)

                        log_cpu.write("decrease : %s\n" % container_id)  # log info
                        log_cpu.write("Time : %d\n" % time.time())
                        log_cpu.write("number of cores : %d\n" % len(cores))
                        time.sleep(19)

        def cpu_resize(self, container_id):
                #log_cpu = open('%s.txt' % container_id, 'wb')
	       with open('%s.txt' % container_id, 'a') as log_cpu:
		log_cpu.write("our experiment is started : %s\n" % container_id)  # log info
                log_cpu.write("Time : %d\n" % time.time())
                #log_cpu.write("number of cores : %d\n" % len(cores))
                time.sleep(1)
                
		cpusetpath = "/sys/fs/cgroup/cpuset/docker/"+container_id
                cpupath = "/sys/fs/cgroup/cpu/docker/"+container_id
                self.loglock=threading.Lock()
                while True:
                        f = self._readline(cpusetpath+'/cpuset.cpus')
                        no_cores_real =  len(self.cpusetToList(f))
                        print("Core NB : ", no_cores_real)

                        cpu_percentage1 = float(self._read_docker_usage(container_id))
                        time.sleep(4)

                        cpu_percentage11 = float(self._read_docker_usage(container_id))
                        cpu_percentage_average = (cpu_percentage1 + cpu_percentage11)/2
                        print(cpu_percentage_average)
                        cpu_percentage = cpu_percentage_average/no_cores_real

                ##########increase or decrease cpu cores  assigned to docker

                        self._add_vCPUs(cpu_percentage, no_cores_real, cpusetpath, container_id,log_cpu)

                        self._remove_vCPUs(cpu_percentage, no_cores_real, cpusetpath, container_id, log_cpu)
                log_cpu.close()
if __name__ == '__main__':

                exp=Elastic()
		#x = exp._inial_avaialbleCPUs()
                #print(x)
		exp.containers_id()


