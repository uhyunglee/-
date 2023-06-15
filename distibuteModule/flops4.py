import time
from ast import parse
#python3 flops.py --weights yolov5s.pt --device 0 --path /home/share/nfs/flops --nodeNum 2
#python3 flops.py --weights yolov5s.pt --path /home/share/nfs/flops --nodeNum 2 --width 512  --height 512

#python3 flops.py --weights yolov5s.pt --path /home/share/nfs/flops --nodeNum 2 --width 1024 --height 1024

import torch
import argparse
import os
import sys


from utils.general import check_requirements
from pathlib import Path
from ptflops import get_model_complexity_info
from models.common import DetectMultiBackend
from utils.torch_utils import select_device

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default='yolov5s.pt', help='model path(s)')
    parser.add_argument('--width', nargs='+', type=int, default=512, help='video width')
    parser.add_argument('--height', nargs='+', type=int, default=512, help='video height')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--path', default="/home/share/nfs/flops/", type=str)
    parser.add_argument('--nodeNum', default=1 ,type=int)
    opt = parser.parse_args()
    return opt

def main(opt):
    check_requirements(exclude=('tensorboard', 'thop'))
    opt_save = opt
    run(**vars(opt_save))

def saveNodeFlops(path, nodeNum, board_flops):
    change = False
    if os.path.exists(path):
        newLines = []
        with open(path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                nowNum = int(line.split()[0].replace("node" ,""))
                if(nowNum == nodeNum):
                    continue
                newLines.append([nowNum, line+"\n"])
        file.close()
        newLines.append([nodeNum,"node"+str(nodeNum)+" "+str(round(board_flops,4))+"\n" ])
        newLines.sort(key=lambda x:x[0])
        with open(path, 'w') as file:
            for line in newLines:
                file.write(line[1])
        file.close()

    else: # 파일이 존재하지 않을 때

        with open(path, 'w+') as file:
            file.write("node"+str(nodeNum)+" "+str(round(board_flops,4))+"\n")
        file.close()

def saveModelFlops(path, model_flops):
    if not os.path.exists(path):
        print("there is no file!")
        return

    path = os.path.join( path, "model_flops.txt")
    if os.path.exists(path):
        return
    else:
        with open(path, 'w+') as file:
            file.write(str(model_flops))
            file.close



def run(

        weights,
        width,
        height,
        device,
        path ,
        nodeNum

):
    dnn = False
    data = None
    half = False
    width = width[0]
    height = height[0]


    device = select_device(device)
    print(f"Using device: {device}")

    input_data = torch.randn(1, 3, width, height)
    print(input_data.shape)


    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
    if torch.cuda.is_available():
    # 모델과 입력 데이터를 GPU(CUDA) 메모리로 이동
        model.cuda()
        input_data = input_data.cuda()

    model_flops, params = get_model_complexity_info(model, (3,width,height), as_strings=False, print_per_layer_stat=False)

    print(f"Model FLOPs: {model_flops/ 10e9}G")

    # save model Flops
    saveModelFlops(path, model_flops / 10e9)


    _ = model.forward(input_data)
    # Measure inference time
    start_time = time.time()
    #print(start_time)
    for i in range(3):
        _ = model.forward(input_data)
    end_time = time.time()
    #print(end_time)
    inference_time = (end_time - start_time) /3
    #print(inference_time)

    # Compute FLOPs of board_flops
    board_flops = model_flops / inference_time / 10e9

    print(f"Inference time per frame: {inference_time:.4f} seconds")
    print(f"boardFlops: {board_flops:.4f}G")

    flopsFileName = "node_flops.txt"
    path = os.path.join(path, flopsFileName)
    saveNodeFlops(path,nodeNum,board_flops)




if __name__ == "__main__":
    opt = parse_opt()
    main(opt)