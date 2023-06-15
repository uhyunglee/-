import subprocess
import requests
import time
import node
import yaml
import os

class kubemanager():
    def __init__(self) -> None:
        self.spring_web_server_yaml='./spring_web_server.yaml'
        self.distributed_server_yaml='./distributed_server.yaml'
        self.Upload_File_Check='http://192.168.0.5:30620/FileIsUpload'
        self.NodeList=[]
        self.Available_Node=[]
        self.threshold=0

    # spring 웹 서버 POD 쿠버네티스에 뛰움
    def spring_web_server(self):
        output = subprocess.check_output('kubectl apply -f '+self.spring_web_server_yaml, shell=True).decode()
        print(output)


    # 분배모듈 서버 POD 쿠버네티스에 뛰움
    def distributed_server(self):
        output = subprocess.check_output('kubectl apply -f '+self.distributed_server_yaml, shell=True).decode()
        print(output)


    # Yaml 파일이 존재하는지 검사
    def Yaml_File_Check(output):
        return "does not exist" not in output

    # spring 웹 서버에서 File Upload될 때 까지 기다림
    def response(self):
        response=""
        while(response!=True):
            response = requests.get(self.Upload_File_Check)
            time.sleep(1)
        return

    # 현재 쿠버네티스에 접속 중인 노드 확인 후 노드 정보를 가진 객체 생성
    def Node_Information(self, mode):
        self.NodeList = []
        self.Available_Node = []
        output = subprocess.check_output('kubectl top nodes', shell=True).decode()
        result = output.split()
        if len(result) <= 5:
            print("There are no nodes in Kubernetes")
        else:
            self.getNodeInfo(result, mode)

        return self.Available_Node_Check()

    def getNodeInfo(self, result, mode):
        for i in range(5, len(result), 5):
            if '<unknown>' in result[i:i + 5]: continue
            if result[i] == 'master': continue
            nodeName = result[i]
            nodeIp = self.getInternalIp(nodeName)
            print(str(nodeName)+" ip is "+str(nodeIp))
            if nodeIp != "":
                nodeInfo = result[i:i + 5]
                nodeInfo.append(nodeIp)
                new_node = node.Node(nodeInfo)
                self.NodeList.append(new_node)
                if mode == "single" and len(self.NodeList) == 1:
                    break
            else:
                continue



    def getInternalIp(self, nodeName):

        output = subprocess.check_output('kubectl get no -o wide | grep '+nodeName, shell=True).decode()
        result = output.split()
        nodeIp = ""
        if len(result) <= 10:
            print('cant get result of "kubectl get no -o wide" ')
        else:
            if result[0] == nodeName:
                    nodeIp = result[5]
        if nodeIp is None:
            print('error get nodeIp ' + str(nodeName))
        else:
            return nodeIp



    # 노드 중 Yolo실행 가능한 노드 검색
    def Available_Node_Check(self):
        flops={}
        file_path="/home/share/nfs/flops/node_flops.txt"
        if os.path.exists(file_path):
            file = open(file_path, 'r')
        else:
            print("파일이 존재하지 않습니다.")


        while True:
            line = file.readline()
            if not line: break
            node_name,flops_info=line.split(" ")
            flops[node_name]=flops_info
        print("nodeList "+str(len(self.NodeList)))
        for n in self.NodeList:
            if n.total_memory-n.memory_usage > self.threshold and n.name in flops:
                n.set_flops(flops[n.name])
                self.Available_Node.append(n)
        return self.Yolo_Pod_exec()


    # 사용가능 한 노드에는 Yolo Pod 생성
    def Yolo_Pod_exec(self):
        for n in self.Available_Node:
            if n.isgpu:
                with open("gpuyolo.yaml", "r") as f:
                    data = yaml.safe_load_all(f)
                    for item in data:
                        print(item)
                        if item.get("kind") == "Deployment":
                            yaml_data = item
                            break

                    # Service 파트 찾기
                    for item in data:
                        if item.get("kind") == "Service":
                            service_data = item
                            break
            else:
                with open("cpu.yaml", "r") as f:
                    data = yaml.safe_load_all(f)
                    for item in data:
                        print(item)
                        if item.get("kind") == "Deployment":
                            yaml_data = item
                            break

                    # Service 파트 찾기
                    for item in data:
                        if item.get("kind") == "Service":
                            service_data = item
                            break
            POD_Name=n.name+"yolo"
            print("!2312312")


            print(yaml_data["metadata"]["name"])
            yaml_data["metadata"]["name"]=POD_Name
            yaml_data["spec"]["selector"]["matchLabels"]["app"], \
            yaml_data["spec"]["template"]["metadata"]["labels"]["app"] = ["updated-label"] * 2
            yaml_data['spec']['template']['spec']['containers'][0]['name'] = POD_Name
            if n.isgpu:
                yaml_data['spec']['template']['spec']['containers'][0]['command']=\
                    ["python3", "./yolo/yoloFlask.py", "--filePath", "/home/share/nfs/"+n.name, "--save_dir", "/home/share/nfs/result", "--address", "192.168.0.11:30500"]
            else:
                yaml_data['spec']['template']['spec']['containers'][0]['command']=\
                    ["python3", "./yoloFlask.py", "--filePath", "/home/share/nfs/"+n.name, "--save_dir", "/home/share/nfs/result", "--address", "192.168.0.11:30500"]
            yaml_data['spec']['template']['spec']['nodeSelector']['key'] = n.name

            with open(POD_Name+'.yaml', "w") as f:
                yaml.dump(yaml_data, f)
                f.write("---\n")
            print(service_data["metadata"]["name"])
            service_data["metadata"]["name"]=POD_Name
            service_data["spec"]["selector"]["app"]="updated-label"
            service_data["spec"]["ports"][0]["nodePort"]=30100+int(n.name[4:])
            with open(POD_Name+'.yaml', "a") as f:
                yaml.dump(service_data, f)

            output = subprocess.check_output('kubectl apply -f '+POD_Name+'.yaml', shell=True).decode()
            print(output)
            #output = subprocess.check_output('kubectl apply -f '+'yolo_service_plz.yaml', shell=True).decode()
            #print(output)
            #time.sleep(5)
            #self.Yolo_Ready_Check()
        return self.Available_Node

    def node_flops_check(self):
        directory_path = "/home/share/nfs/flops"

        # 디렉토리가 존재하지 않는 경우에만 생성
        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
            print("디렉토리가 생성되었습니다.")
        nodeName=[]
        output = subprocess.check_output('kubectl top nodes', shell=True).decode()
        result = output.split()
        if len(result) <= 5:
            print("There are no nodes in Kubernetes")
        else:
            for i in range(5, len(result), 5):
                if '<unknown>' in result[i:i + 5]: continue
                if result[i] == 'master': continue
                nodeName.append(result[i])
        flops=[]
        file_path="/home/share/nfs/flops/node_flops.txt"
        if os.path.exists(file_path):
            file = open(file_path, 'r')
            while True:
                line = file.readline()
                if not line: break
                node_name,_=line.split(" ")
                flops.append(node_name)
            no_flops_node = []
            for name in nodeName:
                if name not in flops:
                    no_flops_node.append(name)
            print("All" +str(len(nodeName))+"nodes, only" +str(len(flops))+ " nodes have flops information")
            check_list=self.flops_measurement(no_flops_node)
        else:
            file = open(file_path, 'w')
            file.close()
            print("There are no nodes available. Run after a while.")
            check_list=self.flops_measurement(nodeName)
        self.check_end(check_list)
        return

    def flops_measurement(self,node):
        for n in node:
            gpu=False
            output = subprocess.check_output("kubectl get nodes -l 'nvidia.com/gpu'", shell=True).decode()
            info=output.split()
            for i in range(5,len(info)):
                if info[i]==n:
                    gpu=True
            if gpu:
                with open("flops_gpu.yaml", "r") as f:
                    data = yaml.safe_load(f)
            else:
                with open("flops.yaml", "r") as f:
                    data = yaml.safe_load(f)
            POD_Name=n
            nodenum=n[-1]
            print(nodenum)
            if gpu:
                data['spec']['template']['spec']['containers'][0]['command'] = ["python3", "./yolo/flops.py", "--weights","./yolo/yolov5s.pt", "--path","/home/share/nfs/flops", "--nodeNum",nodenum, "--width", "512", "--height","512"]
            else:
                data['spec']['template']['spec']['containers'][0]['command'] = ["python3", "./flops.py", "--weights", "yolov5s.pt", "--path", "/home/share/nfs/flops", "--nodeNum", nodenum, "--width", "512", "--height", "512"]
            data["metadata"]["name"]=POD_Name
            data["spec"]["selector"]["matchLabels"]["app"], \
            data["spec"]["template"]["metadata"]["labels"]["app"] = ["updated-label"] * 2
            data['spec']['template']['spec']['containers'][0]['name'] = POD_Name
            data['spec']['template']['spec']['nodeSelector']['key'] = n
            with open(POD_Name+'flops.yaml', "w") as f:
                yaml.dump(data, f)
            output = subprocess.check_output('kubectl apply -f '+POD_Name+'flops.yaml', shell=True).decode()
            print(output)
        return node

    def check_end(self,check_list):
        file_path="/home/share/nfs/flops/node_flops.txt"

        while True:
            skip=True
            node=[]
            if os.path.exists(file_path):
                file = open(file_path, 'r')
                while True:
                    line = file.readline()
                    if not line: break
                    node_name,_=line.split(" ")
                    node.append(node_name)
                for n in check_list:
                    if n not in node :
                        print(n+" is not exsist wait plz!")
                        time.sleep(3)
                        skip=False
                if skip:
                    break
        for n in check_list:
            output = subprocess.check_output('kubectl delete -f '+n+'flops.yaml', shell=True).decode()
            print(output)

    # 만든 POD이 Running 상태인지 점검
    """sumary_line
        def Yolo_Ready_Check(self):
        output = subprocess.check_output('kubectl get pods', shell=True).decode()
        POD_List=output.split()
        # 5개 단위로 자름
        POD_List = [POD_List[i:i+5] for i in range(0, len(POD_List), 5)]
        POD_Situation={}
        for POD in POD_List:
            name=POD[0].split("-")
            POD_Situation[name[0]]=POD[2]
        print(POD_Situation)
        for n in self.Available_Node:
            if n.name+"yolo" not in POD_Situation:
                print("POD is not establish")
            elif POD_Situation[n.name+"yolo"]!="Running":
                print(n.name+" Yolo POD have problem")
        return self.Available_Node
    """
