from __future__ import annotations
from typing import List
import cv2
from numpy import frombuffer
import json
import base64

class FileUtil:
    def __init__(self):
        pass
    
    @staticmethod
    def convertImageToBytes(img, imgType = '.png') -> str:
        _, encriptedImg = 	cv2.imencode(imgType, img)
        imgAsStr = encriptedImg.tostring()
        imgByteStr = base64.b64encode(imgAsStr).decode("utf-8")
        return imgByteStr
    
    @staticmethod
    def convertBytesToImg(encImg: str):
        readImgBytes = base64.b64decode(encImg)
        npImg = frombuffer(readImgBytes,'u1') 
        decImg = cv2.imdecode(npImg, 1)
        return decImg

if __name__ == "__main__":
    from PIL import ImageGrab
    import numpy as np
    from datetime import datetime
    
    cap = cv2.VideoCapture(0)
    _, img = cap.read()
    screen = np.array(ImageGrab.grab(bbox=(0,0,800,600)))
    with open('file.txt', 'w') as file:
        data = {"client_name": "user1", "type": 2, "img": FileUtil.convertImageToBytes(img), "screen": FileUtil.convertImageToBytes(screen), "datetime": str(datetime.now())}
        file.write(json.dumps(data))
    
    
    