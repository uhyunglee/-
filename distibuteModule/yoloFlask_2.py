from flask import Flask, jsonify
import json
import requests

import argparse
import os
import sys
from pathlib import Path
import time
import torch
import threading

from models.common import DetectMultiBackend # ▒~U~D▒~Z~T
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages #▒~U~D▒~Z~T
from utils.general import (LOGGER, Profile, check_file, check_img_size, check_requirements, cv2, non_max_suppression, print_args, scale_coords,increment_path)
from utils.plots import Annotator, colors
from utils.torch_utils import select_device, smart_inference_mode

"""

Python .\detect_cpu_preLoad.py --filePath D:\Capstone\yolo5_distribute\node1 --save_dir D:\Capstone\yolo5_distribute\result
python3 ./yolo_flask.py --filePath /home/share/nfs/node1 --save_dir /home/share/nfs/result

"""

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative
app = Flask(__name__)
global OPT
OPT=""
global IsLast
IsLast = False

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=ROOT / 'yolov5s.pt', help='model path(s)')
    parser.add_argument('--filePath', type=str, default=ROOT / 'node1/input', help='file/dir/URL/glob')
    parser.add_argument('--data', type=str, default=ROOT / 'data/coco128.yaml', help='(optional) dataset.yaml path')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--save_dir', type=str, default=ROOT / 'node1/result', help='file/dir/URL/glob, 0 for webcam')
    parser.add_argument('--conf-thres', type=float, default=0.25, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='show results')
    parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    parser.add_argument('--address', default="", help='response address')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    print_args(vars(opt))
    return opt

def main(opt):
    print("start main", flush=True);
    check_requirements(exclude=('tensorboard', 'thop'))
    print("pass requierements", flush=True);
    opt_save = opt
    run(**vars(opt_save))

@smart_inference_mode()
def run(
        weights=ROOT / 'yolov5s.pt',  # model.pt path(s)
        filePath=ROOT  / 'node1/',  # file/dir/URL/glob, 0 for webcam
        data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
        imgsz=(640, 640),  # inference size (height, width)
        save_dir = "./node1/result",
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=False,  # show resultss
        save_crop=False,  # save cropped prediction boxes
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        address = ""
):
    # Load model
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size
    save_img = True
    model.warmup(imgsz=(1, 3, *imgsz))  # warmup
    mode = 'image'
    nodepath = os.path.normpath(filePath) # ▒~G▒~H째 ▒~E▒▒~S~\ ▒~]▒▒~@
    nodeNumStr=nodepath[-1]

    check_dir(save_dir)

    frameCount = 0;
    leftFrame = 0;

    print("detection start " ,flush=True)

    while(1):
        for (root, dirs, files) in os.walk(filePath):
            leftFrame = len(files)
            for file in files:
                source = os.path.join(filePath, file) #/home/share/nfs/node1/1.png
                print(source,flush=True)
                save_path = os.path.join(save_dir, file) #/home/share/nfs/result\1.png
                # Dataloader

                dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
                bs = 1  # batch_size
                vid_path, vid_writer = [None] * bs, [None] * bs

                # Run inference
                seen, windows, dt = 0, [], (Profile(), Profile(), Profile())
                for path, im, im0s, vid_cap, s in dataset:
                    with dt[0]:
                        im = torch.from_numpy(im).to(device)
                        im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
                        im /= 255  # 0 - 255 to 0.0 - 1.0
                        if len(im.shape) == 3:
                            im = im[None]  # expand for batch dim

                    # Inference
                    with dt[1]:
                        visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
                        pred = model(im, augment=augment, visualize=visualize)

                    # NMS
                    with dt[2]:
                        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

                    # Process predictions
                    for i, det in enumerate(pred):  # per image
                        seen += 1
                        p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)
                        p = Path(p)  # to Path
                        # save_path = "/home/share/nfs/node1/cpuResult.mp4"  # im.jpg
                        s += '%gx%g ' % im.shape[2:]  # print string
                        gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
                        imc = im0.copy() if save_crop else im0  # for save_crop
                        annotator = Annotator(im0, line_width=line_thickness, example=str(names))
                        if len(det):
                            # Rescale boxes from img_size to im0 size
                            det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                            # Print results
                            for c in det[:, -1].unique():
                                n = (det[:, -1] == c).sum()  # detections per class
                                s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                            # Write results
                            for *xyxy, conf, cls in reversed(det):
                                if save_img or save_crop or view_img:  # Add bbox to image
                                    c = int(cls)  # integer class
                                    label = None if hide_labels else (
                                        names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                                    annotator.box_label(xyxy, label, color=colors(c, True))

                        # Save results (image with detections)
                        if save_img:
                            if dataset.mode == 'image':
                                print(save_path,flush=True)
                                cv2.imwrite(save_path, im0)
                            else:  # 'video' or 'stream'
                                if vid_path[i] != save_path:  # new video
                                    vid_path[i] = save_path
                                    if isinstance(vid_writer[i], cv2.VideoWriter):
                                        vid_writer[i].release()  # release previous video writer
                                    if vid_cap:  # video
                                        fps = vid_cap.get(cv2.CAP_PROP_FPS)
                                        w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                        h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                    else:  # stream
                                        fps, w, h = 30, im0.shape[1], im0.shape[0]
                                    save_path = str(
                                        Path(save_path).with_suffix('.mp4'))  # force *.mp4 suffix on results videos
                                    vid_writer[i] = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps,
                                                                    (w, h))
                                vid_writer[i].write(im0)

                    # Print time (inference-only)
                    LOGGER.info(f"{s}{'' if len(det) else '(no detections), '}{dt[1].dt * 1E3:.1f}ms")

                # Print results
                t = tuple(x.t / seen * 1E3 for x in dt)  # speeds per image
                LOGGER.info(
                    f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS per image at shape {(1, 3, *imgsz)}' % t)
                #resultTime = time.time() - start
                removeFile(source)
                frameCount = frameCount + 1

                if frameCount % 10 == 0:
                    thread = threading.Thread(target=send_Progress, args=(str(nodeNumStr), frameCount, leftFrame))
                    thread.start()


                if IsLast and not newFileCheck(filePath): # end all
                    thread = threading.Thread(target=send_Progress, args=(str(nodeNumStr), frameCount, 0))
                    thread.start()
                    url = 'http://192.168.0.11:30500/yolo/end/' + str(nodeNumStr)
                    response = requests.get(url, timeout=10)
                    print("finish 2",flush=True)
                    print(response,flush=True)
                    exit()
                else:
                    waitNewFile(filePath)




@app.route("/end")
def last():
    global IsLast
    IsLast = True
    data = {'message': 'yolo going end'}
    print(IsLast,flush=True)
    return jsonify(data)

@app.route("/start")
def start():
    global OPT
    data = {'message': 'yolo Start'}
    thread = threading.Thread(target=main, args=(OPT,))
    thread.start()
    return jsonify(data)

def removeFile(file):
    if os.path.isfile(file):
        os.remove(file)

def newFileCheck(filePath):
    temp = os.listdir(filePath)
    count = len(temp)
    if count == 0:
        return False
    else:
        return True

def waitNewFile(filePath):
    temp = os.listdir(filePath)
    count = len(temp)
    while count == 0:
        time.sleep(4)
        temp = os.listdir(filePath)
        count = len(temp)

def check_dir(save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created 'result' directory at {save_dir}")
    else:
        print(f"'result' directory already exists at {save_dir}")

def send_Progress(nodeNumStr, frameCount, leftFrame):
    persent = frameCount/(frameCount+leftFrame)
    data = {'persent' : persent}
    url = 'http://192.168.0.11:30500/yolo/progress/' + str(nodeNumStr)
    print(url, flush=True)
    response = requests.post(url, data=data)
    print(response, flush=True)
    return response

def getNodeNum(opt):
    filePath = opt.filePath
    nodepath = os.path.normpath(filePath)  # ▒~G▒~H째 ▒~E▒▒~S~\ ▒~]▒▒~@
    nodeNumStr = nodepath[-1]
    return str(nodeNumStr)

@app.route("/read")
def ready():
    data = {'message': 'I am ready'}
    print("I am ready", flush=True)
    return jsonify(data)



if __name__ == "__main__":
    OPT = parse_opt()
    nodeNumStr = getNodeNum(OPT)
    app.run(host = '0.0.0.0',port = 5001, debug = True)
    url = 'http://192.168.0.11:30500/' + str(nodeNumStr) +"/ready"
    response = requests.get(url)
    print(response, flush=True)
