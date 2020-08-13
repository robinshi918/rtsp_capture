from datetime import datetime
import time
import subprocess
import os
import shutil
from PIL import Image


INTERVAL = 1 * 30 # every 0.5 minute take a capture
RTSP_URL = 'rtsp://admin:VGEQBR@192.168.1.5:554/h264/ch1/main/av_stream'

def getdatatime(humanFriendly = False):
    now = datetime.now()
    if humanFriendly:
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
    else:
        date_time = now.strftime("%Y%m%d_%H%M%S")
    return date_time

def getFreeDiskSpaceInMB():
    total, used, free = shutil.disk_usage("/")
    result = free/1024/1024
    return result

def isNight():
    hour = datetime.now().hour
    return hour >= 18 or hour <= 6

def getJpegSize(filename):
    """"This function prints the resolution of the jpeg image file passed into it"""
    im = Image.open(filename)
    w, h = im.size
    #print("The resolution of the image is",w,"x",h)
    return w, h

def isFrameValid(filename):
    w, h = getJpegSize(filename)
    return w == 1920 and h == 1080

def main_job():
    while True:
        if isNight():
            print("[Warning] Do not capture as it is dark night!! [%s]" % getdatatime(True))
            time.sleep(INTERVAL)
            continue
        try:
            frame_file = "frame_" + getdatatime() + ".jpg"
            cmd_output = subprocess.run(["ffmpeg", "-y", "-i", RTSP_URL, '-vframes', '1', frame_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        #    cmd_output = subprocess.run(["ffmpeg", "-y", "-i", RTSP_URL, '-vframes', '1', frame_file])
            if cmd_output.returncode != 0:
                print("[Error] capture failed, removing" + frame_file)
                os.remove(frame_file)
                continue
            else:
                
                if not isFrameValid(frame_file):
                    print("[Error] Frame size is not 1920x1080, remove %s and re-capture!" % frame_file)
                    os.remove(frame_file)
                    continue
                print("[ OK ] =================> %s" % frame_file)

            if getFreeDiskSpaceInMB() < 500:
                print("[Error] disk space is too small(%dMB). STOP!" % getFreeDiskSpaceInMB())
                break
        except:
            print("exception occurred!!!")
        time.sleep(INTERVAL)

main_job()
