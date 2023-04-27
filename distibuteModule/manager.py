import subprocess
import requests
import time 
import node
import yaml


class kubemanager:
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
    def Node_Information(self):
        output = subprocess.check_output('kubectl top nodes', shell=True).decode()
        result=output.split()
        if len(result)<=5 :
            print("There are no nodes in Kubernetes")
        else:
            for i in range(5,len(result),5):
                if '<unknown>' in result[i:i+5]: continue
                new_node=node.Node(result[i:i+5])
                self.NodeList.append(new_node)
        return self.Available_Node_Check()

    
    # 노드 중 Yolo실행 가능한 노드 검색 
    def Available_Node_Check(self):
        for n in self.NodeList:
            if n.total_memory-n.memory_usage > self.threshold:
                self.Available_Node.append(n)
        return self.Yolo_Pod_exec()
    

    # 사용가능 한 노드에는 Yolo Pod 생성
    def Yolo_Pod_exec(self):
        for n in self.Available_Node:
            if n.isgpu:
                with open("gpuyolo.yaml", "r") as f:
                    yaml_data = yaml.safe_load(f)
            else:
                with open("cpu.yaml", "r") as f:
                    yaml_data = yaml.safe_load(f)
            POD_Name=n.name+"yolo"

            yaml_data["metadata"]["name"], \
            yaml_data["spec"]["selector"]["matchLabels"]["run"], \
            yaml_data["spec"]["template"]["metadata"]["labels"]["run"], \
            yaml_data['spec']['template']['spec']['containers'][0]['name'] = [POD_Name] * 4
            yaml_data['spec']['template']['spec']['nodeSelector']['key'] = n.name
            
            with open(POD_Name+'.yaml', "w") as f:
                yaml.safe_dump(yaml_data, f)

            output = subprocess.check_output('kubectl apply -f '+POD_Name+'.yaml', shell=True).decode()
            print(output)
            #time.sleep(5)
            #self.Yolo_Ready_Check()
        return self.Available_Node

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


   