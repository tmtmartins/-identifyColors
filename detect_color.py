#!/usr/bin/env python
# -*- coding: utf-8 -*-

# USAGE: You need to specify "only one" source
#
# (python) detect_color --image /path/to/image.png
# or
# (python) detect_color --video /path/to/video.png
# or
# (python) detect_color --webcam

from tkinter import image_names
import cv2
import argparse
from operator import xor
import imutils
import numpy as np 
from PIL import Image, ImageEnhance

def get_arguments():
    ap = argparse.ArgumentParser()
    ap.add_argument('-i', '--image', required=False,
                    help='Path to the image')
    ap.add_argument('-w', '--webcam', required=False,
                    help='Use webcam', action='store_true')
    ap.add_argument('-p', '--preview', required=False,
                    help='Show a preview of the image after applying the mask',
                    action='store_true')
    ap.add_argument("-v", "--video", required=False, 
                    help="path to the (optional) video file")
    args = vars(ap.parse_args())

    # if not xor(bool(args['image']), bool(args['webcam']), bool(args['video'])):
    #     ap.error("Please specify only one source")

    return args

def equalize(frame):
    frame_yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    frame_yuv[:,:,0] = cv2.equalizeHist(frame_yuv[:,:,0])
    frame_treated = cv2.cvtColor(frame_yuv, cv2.COLOR_YUV2BGR)
    hsv = cv2.cvtColor(frame_treated, cv2.COLOR_BGR2HSV)

    # We want to increase saturation by 50
    value = 40
    # Grab saturation channel
    saturation = hsv[..., 1]
    # Increase saturation by a given value
    saturation = cv2.add(saturation, value)
    # Clip resulting values to fit within 0 - 255 range
    np.clip(saturation, 0, 255)
    # Put back adjusted channel into the HSV image
    hsv[..., 1] = saturation
    frame_treated = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    if args['preview']:
        res = np.hstack((frame, frame_treated)) #stacking images side-by-side
        cv2.imshow('before and after treatment', res)
        cv2.waitKey()
        cv2.destroyAllWindows()

    return frame_treated

def localize_colors(frame, colorlower, colorUpper, color):

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # Construir uma mascara para a cor
    # Uma serie de dilatacoes e erosoes para remover qualquer ruido
    mask = cv2.inRange(hsv, colorlower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cntColor, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)
    centerColor = None

    # Só seguir se pelo menos um contorno foi encontrado
    if len(cntColor) > 0:
        # Encontrar o maior contorno da mascara, em seguida, usar-lo para calcular o circulo de fecho minima e
        cColor = max(cntColor, key=cv2.contourArea)
        rectColor = cv2.minAreaRect(cColor)
        boxColor = cv2.boxPoints(rectColor)
        boxColor = np.int0(boxColor)
        MColor = cv2.moments(cColor)
        centerColor = (int(MColor["m10"] / MColor["m00"]), int(MColor["m01"] / MColor["m00"]))
        cv2.putText(img=frame, text=color, org=(centerColor), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=(255, 255, 255),thickness=3)
        cv2.putText(img=frame, text=color, org=(centerColor), fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1, color=(0, 0, 0),thickness=2)
        cv2.drawContours(frame, cntColor, contourIdx=-1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)

    return frame


def mount_frame(frame):
    # Redimensionar o quadro, esbater-lo e converte-lo para o HSV
    frame = imutils.resize(frame, width=800)
    frame = equalize(frame)

    frame = localize_colors(frame, greenLower, greenUpper, "VERDE")
    frame = localize_colors(frame, redLower, redUpper, "VERMELHO")
    frame = localize_colors(frame, yellowLower, yellowUpper, "AMARELO")
    frame = localize_colors(frame, blueLower, blueUpper, "AZUL")
    
    return frame

def find_on_image():
    img_before = cv2.imread(args['image'], cv2.IMREAD_COLOR)
    img_before = imutils.resize(img_before, width=800)
    img_after = mount_frame(img_before)
    if args['preview']:
        res = np.hstack((img_before, img_after)) #stacking images side-by-side
        cv2.imshow('Before and After', res)
    else: 
        cv2.imshow('Imagem Final', img_after)
    cv2.waitKey()
    cv2.destroyAllWindows()

    return img_before, img_after

def find_on_video(video):
    # Manter looping
    while True:
        # Agarrar o quadro atual
        (grabbed, frame) = video.read()

        # Se estamos vendo um video e vamos pegar um quadro,
        # Em seguida, chegamos ao final do video
        if args.get("video") and not grabbed:
            break

        frame = mount_frame(frame)

        # Mostrar o quadro na tela
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # Condicao de parada 'q', parar o loop
        if key == ord("q"):
            break

        # Limpeza da camara e feche todas as janelas abertas
    video.release()
    cv2.destroyAllWindows()


args = get_arguments()

#verde
greenLower = (40,59,78)
greenUpper = (93,255,255)

#vermelho
redLower = (0,190,71)
redUpper = (5,255,255)

#azul
blueLower = (95,67,112)
blueUpper = (122,255,255)

#amarelo
yellowLower = (22,105,230)
yellowUpper = (33,255,255)

#roxo
purpleLower = (124,70,127)
purpleUpper = (158,255,255)

#laranja
orangeLower = (11,201,166)
orangeUpper = (22,255,255)

#ciano
cyanLower = (79,100,125)
cyanUpper = (92,255,255)

#rosa
pinkLower = (150,63,184)
pinkUpper = (177,238,255)
def main():
    args = get_arguments()

    if args['image']:
        img, img_equalized = find_on_image()
        print('image')

    elif args["video"]:
        video = cv2.VideoCapture(args["video"])
        print('video')
        find_on_video(video)
    else:
        camera = cv2.VideoCapture(0)
        print('webcam')
        find_on_video(camera)


if __name__ == '__main__':
    main()