from io import BytesIO
from PIL import Image
import cv2
import numpy as np


def cv2_to_pil(cv2_img):
    if not cv2:
        raise ImportError("OpenCv was never found during boot. Install opencv to use this function")
    return Image.fromarray(cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB))

def pil_to_cv2(pil_img):
    if not cv2:
        raise ImportError("OpenCv was never found during boot. Install opencv to use this function")
    if not Image:
        raise ImportError("PIL was never found during boot. Install Python Image Lib. to use this function")
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def pil_to_memory_file(pil_img):
    if BytesIO == False:
        raise ImportError("BytesIO was never found, please install it to use this feature")
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io