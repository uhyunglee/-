from flask import Flask, jsonify, request
import threading
import json
import cv2
import node2
import requests
import urllib.parse
import os
import time
import subprocess
from FrameDrop import framedrop

app = Flask(__name__)
nodeList = []
droplist = []
total_frames = 0
dropframe=0
fps = 0
start = 0
mergeTime = 0
numcount=0
class VideoInformation:
    def __init__(self, frameWidth, frameHeight, frameCount, fps, videoLength, nodeCount):
        self.frameWidth = frameWidth
        self.frameHeight = frameHeight
        self.frameCount = frameCount
        self.fps = fps
        self.videoLength = videoLength
        self.videoPath = ""
        self.nodeCount = nodeCount

class DownloadInformation:
    def __init__(self, downloadPath, waitTime,dropCount):
        self.downloadPath = downloadPath;
        self.waitTime = waitTime;
        self.dropCount=dropCount


def do_something(AvailNode_List, videoPath,threshold):
    print("do something")
    # resultPath = videoPath.split("'\'")[:-1]
    resultPath = os.path.dirname(videoPath)
    resultPath = os.path.join(resultPath, "result")
    resultPath = os.path.join(resultPath, "result_" + os.path.basename(videoPath))
    print(resultPath)
    global start
    start = time.time()
    FrameDrop = framedrop(videoPath, resultPath, 'CORREL', threshold,
                          AvailNode_List)
    global dropframe
    dropframe = FrameDrop.drop()

    directory_path = '/home/share/nfs/result'  # 체크하려는 디렉토리 경로로 변경해야 합니다
    while True:
        print(str(dropframe)+"        "+str(total_frames),flush=True)
        file_count = count_files(directory_path)
        result=total_frames-dropframe
        print("result : "+str(result)+"  file_count : "+str(file_count),flush=True)
        if  result== file_count or result == file_count+1 or result==file_count-1 :
            break
        time.sleep(1)
    merge()
    response = requests.get('http://192.168.0.11:30600/distribution/download')
    delete(nodeList)


def count_files(directory):
    count = 0
    for _, _, files in os.walk(directory):
        count += len(files)
    print(count,flush=True)
    return count

@app.route("/")
def hello():
    return "Hello main_falsk"


@app.route("/videoinformation")
def home():
    print(":hi")
    try:

        uri = request.url
    except Exception:
        print(1)
    try:
        # URI 디코딩
        decoded_uri = urllib.parse.unquote(uri)
    except Exception:
        print(2)
    # 쿼리스트링 파라미터 가져오기
    try:

        parsed_uri = urllib.parse.urlparse(decoded_uri)
    except Exception:
        print(3)
    try:
        query_params = urllib.parse.parse_qs(parsed_uri.query)
    except:
        print(4)
    print()

    # 필요한 파라미터 값 가져오기
    mode = query_params.get('mode')[0]
    videoPath = query_params.get('filepath')[0]
    threshold = float(query_params.get('threshold')[0])

    print("mode : " + mode)
    print()

    if videoPath == "":
        print("get fileName is fail")
        return jsonify({'error': 'get fileName is fail'})

    print("videoPath " + videoPath)
    print()

    cap = cv2.VideoCapture(videoPath, apiPreference=None)
    if not cap.isOpened():  # check File exists
        print("Video is not opened!")
        return jsonify({'error': 'Video is not opened!'})
    global fps, total_frames

    fps = cap.get(cv2.CAP_PROP_FPS)  # FPS (초당 프레임 수)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)  # 영상 가로 크기
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # 영상 세로 크기
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)  # 총 프레임 수

    model_flops = 1
    try:
        with open("/home/share/nfs/flops/model_flops.txt", "r") as file:
            model_flops = file.read()
            file.close()
            print("model flops is " + str(model_flops))
    except FileNotFoundError:
        print("model_flops file does not exist.")

    model_flops = (float)(model_flops) * (round(width)/512) * (round(height)/512)

    print('http://192.168.0.11:5002/start/' + mode)
    response = requests.get('http://192.168.0.11:5002/start/' + mode)
    str_data = response.content.decode('utf-8')
    # JSON 문자열을 파싱하여 딕셔너리로 변환/
    json_data = json.loads(str_data)
    json_data2 = json.loads(json_data)
    AvailNode_List = [
        node2.Node(ob['name'], ob['cpu_usage'], ob['total_cpu'], ob['memory_usage'], ob['total_memory'], ob['isgpu'],
                   ob['FLOPS'], ob['ip']) for ob in json_data2]
    print(AvailNode_List)

    # for i in range(len(AvailNode_List)):
    #    nodeList.append(False)

    for n in AvailNode_List:
        n.print_node()
        deleteAndMakeFile(n.name)
        #nodeList.append(False)
        n.FLOPS = float(n.FLOPS)
        if model_flops != 0:
            n.PT = model_flops / n.FLOPS
        else:
            n.PT = 9999999/ n.FLOPS
    deleteAndMakeFile("result")

    threading.Thread(target=do_something, args=[AvailNode_List, videoPath,threshold]).start()
    video_information = VideoInformation(width, height, total_frames, fps, total_frames / fps, len(AvailNode_List))
    return jsonify(vars(video_information))

def deleteAndMakeFile(nodeName):
    basePath = "/home/share/nfs"
    filePath = os.path.join(basePath, nodeName)
    for file in os.scandir(filePath):
        os.remove(file.path)



@app.route("/yolo/end/<int:nodeNum>")
def check_end(nodeNum):
    print(nodeNum, flush=True)
    nodeList[nodeNum - 1] = True
    if all(nodeList):
        merge()
        response = requests.get('http://192.168.0.11:30600/distribution/download')
        # requests.get('http://192.168.0.3:8080/distribution/download')
        delete(nodeList)
    return 'OK'
def delete(node):
    response = requests.get('http://192.168.0.11:5002/end/'+str(len(node)))


def merge():
    num = 0
    image_dir = "/home/share/nfs/result/"
    images_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.png')])
    first_png_path = os.path.join(image_dir, images_files[0])
    first_image = cv2.imread(first_png_path)
    height, width, _ = first_image.shape

    # VideoWriter 객체 생성
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    print(total_frames, fps, width, height, flush=True)
    video_writer = cv2.VideoWriter("/home/share/nfs/result/result.mp4", fourcc, fps, (width, height))
    print("im herer1111", flush=True)
    for i in range(1, int(total_frames)):
        file_name = str(i) + ".png"
        image_path = os.path.join(image_dir, file_name)
        print(image_path, flush=True)
        if os.path.exists(image_path):
            print(str(i) + 'is true', flush=True)
            frame = cv2.imread(image_path)
        # 영상에 프레임 추가
        video_writer.write(frame)

    # 사용한 리소스 해제
    video_writer.release()
    global mergeTime
    global start
    end = time.time()
    mergeTime = end - start;

@app.route("/yolo/progress/<int:nodeNum>", methods=['POST'])
def send_Progress2Spring(nodeNum):
    temp = request.get_data().decode( 'utf-8' )
    temp = temp.split("=")[1]
    persent = int(float(temp) *100)
    print(persent, flush=True)
    url = 'http://192.168.0.11:30600/progress/' +str(nodeNum) +"/" +str(persent)
    resource = requests.post(url)
    return 'OK'

@app.route("/download")
def returnDownloadInformation():
    global mergeTime
    filePath = "/home/share/nfs/result/result.mp4"
    downloadInformation = DownloadInformation(filePath, mergeTime,dropframe)
    print(jsonify(vars(downloadInformation)), flush=True)
    return jsonify(vars(downloadInformation))

@app.route("/<nodeNum>/ready")
def ready(nodeNum):
    global numcount
    numcount+=1
    return "OK"
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
