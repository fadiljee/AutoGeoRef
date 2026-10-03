from paddleocr import PaddleOCR
import cv2
import pprint

def run():
    ocr = PaddleOCR(lang='en')
    img = cv2.imread('data/1_input_raw/1903051009001100_WSS.jpg')
    res = ocr.ocr(img)
    with open('debug_ocr.txt', 'w') as f:
        pprint.pprint(res, stream=f)

if __name__ == "__main__":
    run()
