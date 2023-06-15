import cv2
import numpy as np
import time
import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import threading

import copy

Num=0

class framedrop():
    def __init__(self, filePath, savePath, flag, threshold, NodeList):
        self.filePath = filePath
        self.threshold = threshold
        self.cap = cv2.VideoCapture(filePath, apiPreference=None)
        self.w = round(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = round(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.videoWriter = cv2.VideoWriter(savePath, self.fourcc, self.fps, (self.w, self.h))
        # Method
        self.method = {'CORREL': cv2.HISTCMP_CORREL,  # cv2.HISTCMP_CORREL: 상관관계 (1: 완전 일치, -1: 완전 불일치, 0: 무관계)
                       'CHISQR': cv2.HISTCMP_CHISQR,  # cv2.HISTCMP_CHISQR: 카이제곱 (0: 완전 일치, 무한대: 완전 불일치)
                       'INTERSECT': cv2.HISTCMP_INTERSECT,
                       # cv2.HISTCMP_INTERSECT: 교차 (1: 완전 일치, 0: 완전 불일치 - 1로 정규화한 경우)
                       'BHATTACHARYYA': cv2.HISTCMP_BHATTACHARYYA,  # cv2.HISTCMP_BHATTACHARYYA 값이 작을수록 유사한 것으로 판단
                       'HELLINGER': cv2.HISTCMP_HELLINGER,
                       'CHISQR_ALT': cv2.HISTCMP_CHISQR_ALT,
                       'KL_DIV': cv2.HISTCMP_KL_DIV}
        self.flag = flag
        self.NodeList = NodeList
        self.start_time = 0
        self.current_time = 0
        self.droplist = []
        self.startList=[True for _ in range(len(NodeList))]


    def drop(self):
        self.ready()
        self.startList = [True for _ in range(len(self.NodeList))]
        FirstList=[False for _ in range(len(self.NodeList))]
        if not self.cap.isOpened():  # check File exists
            print("Video is not opened!")
            return
        drop_frame = 0
        beforeRet, beforeFrame = self.cap.read()
        count = 1
        select_node = self.NodeSelector()
        self.send_to_node(beforeFrame, select_node, count)

        self.start_time = time.time()
        beforeFrameHist = self.preprocess(beforeFrame)

        before_num = count
        print('Frame Count : ' + str(self.frame))
        while (True):
            print("totla_frame="+str(self.frame)+" now_frame="+str(count),flush=True)
            nowRet, nowFrame = self.cap.read()
            if not nowRet: break
            nowFrameHist = self.preprocess(nowFrame)

            result = self.calculateSimilarity(beforeFrameHist, nowFrameHist, self.flag)
            print("result value : "+str(result)+" threshold : "+str(self.threshold),flush=True)
            select_node = self.NodeSelector()
            if result >= self.threshold:
                drop_frame += 1
                self.droplist.append(before_num)
            else:
                # nowFrame을 전송
                temp_name=copy.deepcopy(select_node.name)
                temp_name=temp_name.replace("node","")
                selectedNodeNum = int(temp_name)
                print(self.startList,flush=True)
                print("selectedNodeNum : "+ str(selectedNodeNum),flush=True)
                global Num
                if FirstList[selectedNodeNum-1] == False:
                    port_num=30100+selectedNodeNum
                    threading.Thread(target=self.send_start_message, args=[port_num,select_node.ip]).start()
                    FirstList[selectedNodeNum-1] = True
                    self.startList[selectedNodeNum-1] = False
                    Num+=1
                self.send_to_node(nowFrame, select_node, count)
                before_num = count
                beforeFrameHist = nowFrameHist
                beforeFrame = nowFrame
            count += 1


            # similarity = "#"+str(count) + " -> " + str(round(result,6)) + "\n"
        self.cap.release()
        # self.merge_im(drop_frame)
        print("send_end_message",flush=True)
        self.send_end_message()

        return self.startList
    def ready(self):
        for n in self.NodeList:
            temp_name=copy.deepcopy(n.name)
            temp_name=temp_name.replace("node","")
            selectedNodeNum = int(temp_name)
            print(self.startList,flush=True)
            print("selectedNodeNum : "+ str(selectedNodeNum),flush=True)
            port_num=30100+selectedNodeNum
            retries = Retry(total=10000, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
            retries.initial = 1
            adapter = HTTPAdapter(max_retries=retries)

            # Session 생성 및 Retry 설정 적용
            session = requests.Session()
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            url ='http://'+n.ip + ':' + str(port_num) + '/ready'
            print(url,flush=True)
            response = session.get(url)
            e=time.time()
            print(response,flush=True)
        return

    def send_start_message(self,port_num,ip):
        # Retry 설정
        s=time.time()
        print("port num : "+str(port_num)+"ip is : "+str(ip),flush=True)
        retries = Retry(total=10000, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        retries.initial = 1
        adapter = HTTPAdapter(max_retries=retries)

        # Session 생성 및 Retry 설정 적용
        session = requests.Session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        url ='http://'+ip + ':' + str(port_num) + '/start'
        print(url,flush=True)
        response = session.get(url)
        e=time.time()
        print(response,flush=True)
        print(url+"time : "+str(e-s),flush=True)
        global Num
        Num-=1
        return


    def send_end_message(self):
        retries = Retry(total=10000, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)

        # Session 생성 및 Retry 설정 적용
        session = requests.Session()
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        while(True):
            if Num==0:
                time.sleep(3)
                break
        for now in self.NodeList:
            port_num = 30100+int(now.name.replace("node",""))
            url = 'http://' + now.ip + ':' + str(port_num) + '/end'
            print(url,flush=True)
            response = session.get(url)
            print(response,flush=True)
        return response

    def merge_im(self, drop_frame):
        while True:
            if len(os.listdir("/home/share/nfs/result/")) >= self.frame - drop_frame:  # 디렉터리 내 파일 갯수가 num_files 이상이                                                                                                           면
                break  # 반복문 종료
            else:
                time.sleep(1)  # 1초 대기 후 다시 실행
        for dirpath, dirnames, filenames in os.walk("/home/share/nfs/result/"):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                while os.path.getsize(fp) == 0:  ## 크기가 0인 파일이 있다면 대기
                    time.sleep(1)

    def NodeSelector(self):
        self.current_time = time.time()
        elapsed_time = self.current_time - self.start_time
        self.start_time=time.time()
        min_endtime = 100000000
        for node in self.NodeList:
            print(node.name+"PCT : "+ str(node.PCT)+ "  PT : "+str(node.PT),flush=True)
            node.PCT = node.PCT - elapsed_time if node.PCT - elapsed_time > 0 else 0
            if min_endtime > abs(node.PCT - node.TT) + node.PT:
                min_endtime = abs(node.PCT - node.TT) + node.PT
                select_node = node
        return select_node

    def send_to_node(self, Frame, node, count):
        node.PCT += node.PT
        print(count)
        directory_path = "/home/share/nfs/" + node.name
        if not os.path.isdir(directory_path):
            try:
                os.mkdir(directory_path)
            except OSError as error:
                print(error)

        file_path = directory_path + "/" + str(count) + ".png"
        cv2.imwrite(file_path, Frame)
        print(node.name + "선택")
        print()



    def preprocess(self, frame):
        # ---① 각 이미지를 HSV로 변환
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # ---② H,S 채널에 대한 히스토그램 계산
        hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
        # ---③ 0~1로 정규화
        result = cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
        return result

    def calculateSimilarity(self, beforeFrameHist, nowFrameHist, flag):

        ret = cv2.compareHist(beforeFrameHist, nowFrameHist, self.method[flag])

        if flag == cv2.HISTCMP_INTERSECT:
            ret = ret / np.sum(beforeFrameHist)

        return ret

