import subprocess


cal_total = lambda a,b: a//b*100
mb_to_gb = lambda mb: mb / 1024

class Node:
    def __init__(self,name,cpu_usage,total_cpu,memory_usage,total_memory,isgpu,FLOPS):
        self.name=name
        self.cpu_usage=cpu_usage
        self.total_cpu=total_cpu
        self.memory_usage=memory_usage
        self.total_memory=total_memory
        self.isgpu=isgpu
        self.FLOPS=FLOPS
        self.TT=0
        self.PT=0
        self.PCT=0
    
    #For Debug
    def print_node(self):
        print("name : "+str(self.name))
        print("cpu info "+str(self.cpu_usage)+"/"+str(self.total_cpu) + " Core")
        print("memory info "+str(self.memory_usage)+"/"+str(self.total_memory)+" GB")
        print("CPU : "+str(self.isgpu))
        print("FLOPS : "+str(self.FLOPS))
        print("-----------------------")
    
    def set_value(self,PT,TT):
        self.TT=TT
        self.PT=PT