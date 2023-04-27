import subprocess


cal_total = lambda a,b: a//b*100
mb_to_gb = lambda mb: mb / 1024

class Node:
    def __init__(self,node_info):
        self.name=node_info[0]
        self.cpu_usage=int(node_info[1][:-1])/1000 # m단위 제거
        self.total_cpu=round(cal_total(self.cpu_usage*1000,int(node_info[2][:-1]))/1000)
        self.memory_usage=int(node_info[3][:-2])/1000 # Mi단위 제거
        self.total_memory=round(mb_to_gb(cal_total(self.memory_usage*1000,int(node_info[4][:-1]))))
        self.isgpu=self.check_gpu()
        self.FLOPS=0

    def check_gpu(self):
        output = subprocess.check_output("kubectl get nodes -l 'nvidia.com/gpu'", shell=True).decode()
        info=output.split()
        for i in range(5,len(info)):
            if info[i]==self.name:
                return True
        return False
    
    #For Debug
    def print_node(self):
        print("name : "+str(self.name))
        print("cpu info "+str(self.cpu_usage)+"/"+str(self.total_cpu) + " Core")
        print("memory info "+str(self.memory_usage)+"/"+str(self.total_memory)+" GB")
        print("CPU : "+str(self.isgpu))
        print("FLOPS : "+str(self.FLOPS))
        print("-----------------------")
    