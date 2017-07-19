import time
import subprocess as sub
import os
import threading
from elasticvm import ElasticVM 
#import globalvar
class Elastic:

        ########## Memey varaibles ###########
        global threshold,l_threshold,mem_path,allocated_mem,mem_total

        #allocated_mem = 268435456

	def _allocated_mem(self) :
		allocated_mem = 0
		li = sub.Popen(('docker', 'ps', '--no-trunc', '-q'), stdout=sub.PIPE, stderr=sub.PIPE)
		for container_id  in li.stdout.read().strip().split(os.linesep):
			mem_path = "/sys/fs/cgroup/memory/docker/"+container_id
			m = float(self._readline(mem_path+'/memory.limit_in_bytes'))
                	allocated_mem = allocated_mem + m
		return allocated_mem

        ram_t = "free  |awk  \'/^Mem:/{print $2}\'"
        mem_total1 = float(sub.check_output(ram_t, shell=True))
	mem_total =  mem_total1 * 1024

        threshold = 0.9
        l_threshold = 0.5

        def containers_id(self):
                 li = sub.Popen(('docker', 'ps', '--no-trunc', '-q'), stdout=sub.PIPE, stderr=sub.PIPE)
                 for container_id  in li.stdout.read().strip().split(os.linesep): #strip to cut the last empty line in stdout, split to output line by line instead of char by char

                        thread=threading.Thread(target=self.memory_resize, args=(container_id,))
                        thread.start()
        #pass

        def _readline(self, filename) :
                fh = open(filename, 'r')
                result = fh.readline()
                fh.close()
                return result
        #pass

        def _write(self, filename, content):
                fh = open(filename, 'w')
                fh.write(content)
                fh.close()
                #pass   
        def _monitor_memory(self, mem_path):
                mem_usage1 = float(self._readline(mem_path+'/memory.usage_in_bytes'))
                time.sleep(4)

                mem_usage2 = float(self._readline(mem_path+'/memory.usage_in_bytes'))
                time.sleep(4)

                #mem_usage3 = float(self._readline(mem_path+'/memory.usage_in_bytes'))
                #time.sleep(1)

                #print("usage4 %f" % mem_usage4)
                #mem_usage4 = float(self._readline(mem_path+'/memory.usage_in_bytes'))
                #time.sleep(1)

                mem_usage = (mem_usage1 + mem_usage2) / 2
                return mem_usage
        #pass

        def memory_resize(self, container_id):
            global allocated_mem,mem_total
	    allocated_mem = self._allocated_mem()
            #log_mem = open('%s.txt' % container_id, 'wb')
            with open('%s.txt' % container_id, 'a') as myfile:
            	myfile.write("our experiment starts %s\n" % container_id)
                myfile.write("Time : %d\n" % time.time())

            mem_path="/sys/fs/cgroup/memory/docker/"+container_id
            print(mem_path)
            self.loglock=threading.Lock()
            while True:
                #print("wait wait")              
                m = float(self._readline(mem_path+'/memory.limit_in_bytes'))

                mem_usage = float(self._monitor_memory(mem_path))
                #print("wait wait")
                #time.sleep(4)  
                mem_threshold = threshold*m
                mem_l_threshold= l_threshold*m
                if mem_usage >= mem_threshold:
                        if allocated_mem <= mem_total:
                                print("visited to increase")
                                print(mem_path)
                                m += 268435456 #536870912
                                str(m)
                                self._write(mem_path+'/memory.limit_in_bytes', "%d" % m)
                                time.sleep(2)

                                self.loglock.acquire()
                                allocated_mem+=268435456 #536870912
                                print(allocated_mem)
				self.loglock.release()
				with open('%s.txt' % container_id, 'a') as myfile:
                                #log_mem = open('%s.txt' % container_id, 'wb')
                                	myfile.write("increase : %s\n" % container_id)
					myfile.write("Time : %d\n" % time.time())
					myfile.write("size : %d\n" % m)
				
                                time.sleep(8)
                        else: 
				print("wait, we will contact VM controller to  add RAM at the VM level, then we will increase your container")
                                elasticVM = ElasticVM()
                                dom, vcpu_nu, mem_size = elasticVM.connect()
				self.loglock.acquire() 
				mem_size = mem_size + 524288 # (512MB), in kilobyes, this memory size comes from the vm controller
                                self.loglock.release()
				elasticVM.add_mem(dom, mem_size) # vm controller will add 512KB  to the machine
				self.loglock.acquire() 
				m += 268435456 #536870912 
				str(m)
				self._write(mem_path+'/memory.limit_in_bytes', "%d" % m) # add 256MB( added in bytes) 
				with open('%s.txt' % container_id, 'a') as myfile:
                                #log_mem = open('%s.txt' % container_id, 'wb')
                                	myfile.write("increase : %s\n" % container_id)
                                	myfile.write("Time : %d\n" % time.time())
                                	myfile.write("size : %d\n" % m)

				time.sleep(2) 
				allocated_mem+=268435456 
				self.loglock.release() 
				time.sleep(8) 

                if mem_usage <= mem_l_threshold and m > 1073741824: #536870912: #268435456:
                        m -= 134217728
                        str(m)
                        print("decrease")
                        print(mem_path)
                        self._write(mem_path+'/memory.limit_in_bytes', "%d" % m)
                        time.sleep(2)
                        self.loglock.acquire()
                        allocated_mem-=134217728
                        print(allocated_mem)
                        self.loglock.release()
                        with open('%s.txt' % container_id, 'a') as myfile:
                                myfile.write("decrease: %s\n" % container_id)
                                myfile.write("Time : %d\n" % time.time())
                                myfile.write("size : %d\n" % m)
                        #log_mem.write("decrease : %s\n" % container_id)
                        time.sleep(18)
            #log_mem.close()  
             #print("wait wait")          
             #time.sleep(3)
if __name__ == '__main__':
                exp=Elastic()
                exp.containers_id()
		#print mem_total
		#x = exp._allocated_mem()
		#print(x)

