import cv2
import numpy as np
import time
import os
class framedrop():
    def __init__(self, filePath, savePath, flag, threshold, NodeList):
        self.filePath = filePath
        self.threshold=threshold
        self.cap = cv2.VideoCapture(filePath, apiPreference=None)
        self.w = round(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.h = round(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
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
        self.NodeList = NodeList
        self.start_time = 0
        self.current_time=0
        self.droplist=[]
        self.count =0

    def drop(self):
        if not self.cap.isOpened():  # check File exists
            print("Video is not opened!")
            return
        drop_frame=0
        beforeRet, beforeFrame = self.cap.read()

        selsect_node = self.NodeSelector()


        self.start_time=time.time()
        beforeFrameHist = self.preprocess(beforeFrame)
        count = 1
        before_num = count
        print('Frame Count : ' + str(self.frame))

        while (count != self.frame):
            nowRet, nowFrame = self.cap.read()
            nowFrameHist = self.preprocess(nowFrame)

            result = self.calculateSimilarity(beforeFrameHist, nowFrameHist, self.flag)
            selsect_node = self.NodeSelector()
            if result >= self.threshold:
                drop_frame += 1
                self.droplist.append(before_num)
            else:
                # nowFrame을 전송
                self.send_to_node(nowFrame, selsect_node, count)
                before_num = count
                beforeFrameHist = nowFrameHist
                beforeFrame = nowFrame
                self.droplist.append(count)
            count += 1
            self.start_time = time.time()
            # similarity = "#"+str(count) + " -> " + str(round(result,6)) + "\n"
        self.cap.release()
        # self.merge_im(drop_frame)
        return drop_frame

    def merge_im(self, drop_frame):
        while True:
            if len(os.listdir("/home/share/nfs/result/")) >= self.frame - drop_frame:  # 디렉터리 내 파일 갯수가 num_files 이상이면
                break  # 반복문 종료
            else:
                time.sleep(1)  # 1초 대기 후 다시 실행
        for dirpath, dirnames, filenames in os.walk("/home/share/nfs/result/"):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                while os.path.getsize(fp) == 0:  ## 크기가 0인 파일이 있다면 대기
                    time.sleep(1)


    def NodeSelector(self):
        self.current_time=time.time()
        elapsed_time=self.current_time-self.start_time
        min_endtime=100000000
        for node in self.NodeList:
            node.PCT=node.PCT-elapsed_time if node.PCT-elapsed_time > 0 else 0
            if min_endtime > abs(node.PCT-node.TT)+node.PT :
                min_endtime=abs(node.PCT-node.TT)+node.PT
                select_node=node
        return select_node

    def send_to_node(self,Frame,node,count):
        node.PCT+=node.PT

        directory_path = "./home/share/nfs/"+node.name
        if os.path.isdir(directory_path) is not False:
            try:
                os.mkdir(directory_path)
            except OSError as error:
                print(error)


        file_path = directory_path+"/"+str(count)+".png"
        out = cv2.VideoWriter(file_path, self.fourcc, self.fps, (self.w, self.h))
        out.write(Frame)
        out.release()
        self.count += 1
        if self.count % 10 == 0:
            print(node.name +"선택" )


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

