import cv2
import numpy as np
import time
import node
import random

class framedrop():
    def __init__(self, filePath, savePath, flag, threshold,NodeList):
        self.filePath = filePath
        self.threshold=threshold
        self.cap = cv2.VideoCapture(filePath, apiPreference=None)
        self.w = round(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = round(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fourcc = cv2.VideoWriter_fourcc('M','P','4','V')
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame = round(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.videoWriter = cv2.VideoWriter(savePath, self.fourcc, self.fps,(self.w,self.h))
        #Method
        self.method = {'CORREL' :cv2.HISTCMP_CORREL,                # cv2.HISTCMP_CORREL: 상관관계 (1: 완전 일치, -1: 완전 불일치, 0: 무관계)
        'CHISQR':cv2.HISTCMP_CHISQR,                 # cv2.HISTCMP_CHISQR: 카이제곱 (0: 완전 일치, 무한대: 완전 불일치)
        'INTERSECT':cv2.HISTCMP_INTERSECT,           # cv2.HISTCMP_INTERSECT: 교차 (1: 완전 일치, 0: 완전 불일치 - 1로 정규화한 경우)
        'BHATTACHARYYA':cv2.HISTCMP_BHATTACHARYYA,   # cv2.HISTCMP_BHATTACHARYYA 값이 작을수록 유사한 것으로 판단
        'HELLINGER':cv2.HISTCMP_HELLINGER,
        'CHISQR_ALT':cv2.HISTCMP_CHISQR_ALT,
        'KL_DIV':cv2.HISTCMP_KL_DIV}
        self.flag = flag
        self.NodeList=NodeList
        self.start_time=0
        self.current_time=0

    def drop(self):
        if not self.cap.isOpened():  # check File exists
            print("Video is not opened!")
            return
        drop_frame=0
        beforeRet, beforeFrame = self.cap.read()
        print('Frame Count : '+str(self.frame))
        print()
        print("Frame 1")
        selsect_node=self.NodeSelector()
        
        self.send_to_node(beforeFrame,selsect_node)

        self.start_time=time.time()
        beforeFrameHist = self.preprocess(beforeFrame)
        count = 1
        

        while(count != self.frame):
            nowRet, nowFrame = self.cap.read()
            nowFrameHist = self.preprocess(nowFrame)

            result = self.calculateSimilarity(beforeFrameHist, nowFrameHist, self.flag)
            print('Frame '+str(count+1))
            selsect_node=self.NodeSelector()
            
            if result >= self.threshold:
                drop_frame+=1
                self.send_to_node()
            else:
                # nowFrame을 전송
                self.send_to_node(nowFrame,selsect_node)
                beforeFrameHist = nowFrameHist
                beforeFrame=nowFrame
            count +=1 
            self.start_time=time.time()
            #similarity = "#"+str(count) + " -> " + str(round(result,6)) + "\n"
        self.cap.release()
        print()
        for node in self.NodeList:
            print(node.name+"의 남은 작업시간 : "+'{:.4f}'.format(node.PCT)+"sec")
        return drop_frame
    
    def NodeSelector(self):
        self.current_time=time.time()
        elapsed_time=self.current_time-self.start_time
        min_endtime=100000000
        for node in self.NodeList:
            
            node.PCT=node.PCT-elapsed_time if node.PCT-elapsed_time > 0 else 0
            #print(node.name+"의 남은 작업시간 : "+'{:.4f}'.format(node.PCT)+"sec"+ ", 예상 작업 완료시간 : "+'{:.4f}'.format(abs(node.PCT-node.TT)+node.PT)+"sec")
            if min_endtime > abs(node.PCT-node.TT)+node.PT :
                min_endtime=abs(node.PCT-node.TT)+node.PT
                select_node=node
        return select_node

    def send_to_node(self,Frame,node):
        node.PCT+=node.PT
        # 파일 저장
        print(node.name +"선택" )
        print()
        




        
    

    def preprocess(self, frame):
        # ---① 각 이미지를 HSV로 변환
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # ---② H,S 채널에 대한 히스토그램 계산
        hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
        # ---③ 0~1로 정규화
        result =cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return result


    def calculateSimilarity(self, beforeFrameHist, nowFrameHist, flag ):

        ret = cv2.compareHist(beforeFrameHist, nowFrameHist, self.method[flag])

        if flag == cv2.HISTCMP_INTERSECT:
            ret = ret/np.sum(beforeFrameHist)

        return ret
    

json_data2=[
    {
        "name": "master",
        "cpu_usage": 0.669,
        "total_cpu": 4,
        "memory_usage": 1.734,
        "total_memory": 8,
        "isgpu": False,
        "FLOPS": 0
    },
    {
        "name": "node1",
        "cpu_usage": 0.185,
        "total_cpu": 5,
        "memory_usage": 0.718,
        "total_memory": 2,
        "isgpu": False,
        "FLOPS": 0
    },
    {
        "name": "node2",
        "cpu_usage": 0.294,
        "total_cpu": 4,
        "memory_usage": 0.879,
        "total_memory": 4,
        "isgpu": True,
        "FLOPS": 0
    },
    {
        "name": "node3",
        "cpu_usage": 0.294,
        "total_cpu": 4,
        "memory_usage": 0.879,
        "total_memory": 4,
        "isgpu": True,
        "FLOPS": 0
    },
    {
        "name": "node4",
        "cpu_usage": 0.294,
        "total_cpu": 4,
        "memory_usage": 0.879,
        "total_memory": 4,
        "isgpu": True,
        "FLOPS": 0
    }
]


AvailNode_List = [node.Node(ob['name'], ob['cpu_usage'],ob['total_cpu'],ob['memory_usage'],ob['total_memory'],ob['isgpu'],ob['FLOPS']) for ob in json_data2]
FrameDrop = framedrop("C:/Users/Public/test1.mp4", "C:/Users/Public/blacaaaaaaak.mp4", 'CORREL',85,AvailNode_List)
print("1 Frame당 처리 시간")
for node in AvailNode_List:
    node.set_value(random.randint(1, 10),0)
    print(node.name+ " "+ str(node.PT))
drop_frame = FrameDrop.drop()