from flask import Flask, jsonify
import threading
import json
import cv2
import node2
import requests
import subprocess
from FrameDrop import framedrop

app = Flask(__name__)

class VideoInformation:
    def __init__(self, frameWidth, frameHeight, frameCount, fps, videoLength):
        self.frameWidth = frameWidth
        self.frameHeight = frameHeight
        self.frameCount = frameCount
        self.fps = fps
        self.videoLength = videoLength

def do_something(AvailNode_List):
    FrameDrop = framedrop("/home/share/nfs/traffic-mini.mp4", "/home/share/nfs/result-mini.mp4", 'CORREL',85,AvailNode_List)
    drop_frame = FrameDrop.drop()
    
@app.route("/")
def hello():
    return "Hello main_falsk"

@app.route("/videoinformation")
def home():
    
    cap = cv2.VideoCapture("/home/share/nfs/traffic-mini.mp4", apiPreference=None)
    if not cap.isOpened():  # check File exists
        print("Video is not opened!")
    fps = cap.get(cv2.CAP_PROP_FPS)      # FPS (초당 프레임 수)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # 영상 가로 크기
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # 영상 세로 크기
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)   # 총 프레임 수

    response = requests.get('http://192.168.0.11:5002/start')
    str_data = response.content.decode('utf-8')
    # JSON 문자열을 파싱하여 딕셔너리로 변환
    json_data = json.loads(str_data)
    json_data2=json.loads(json_data)
    AvailNode_List = [node2.Node(ob['name'], ob['cpu_usage'],ob['total_cpu'],ob['memory_usage'],ob['total_memory'],ob['isgpu'],ob['FLOPS']) for ob in json_data2]
    print(AvailNode_List)
    for n in AvailNode_List:
        n.print_node()
    threading.Thread(target=do_something,args=(AvailNode_List,)).start()
    video_information = VideoInformation(width, height, total_frames, fps, total_frames/fps)
    return jsonify(vars(video_information))


if __name__ == "__main__":
    app.run(host = '0.0.0.0',port = 5001, debug = True)