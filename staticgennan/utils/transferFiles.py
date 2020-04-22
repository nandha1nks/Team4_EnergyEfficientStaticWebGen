import os
import imageCompress
import cv2

def transferImage(config):
    if not os.path.exists(os.path.dirname(config['site_dir'])+'/images.txt'):
        return
    file = open(os.path.dirname(config['site_dir'])+'/images.txt', "r")
    if not os.path.isdir(config['site_dir']+'/img'):
        os.mkdir(config['site_dir']+'/img')
    for i in file.readlines():
        src, dst = i.strip().split(' ')[:2]
        dst = dst.replace('\\', '/').strip()
        src = src.replace('\\', '/').strip()
        if os.path.exists(src) and not os.path.exists(dst):
            imageCompress.compress(src, 2, dst)
        elif not os.path.exists(src):
            print("Image Error: There is no image in the path you provided ", src)
    file.close()
    #os.remove(os.path.dirname(config['site_dir'])+'/images.txt')
    #print("Image uploading done")

    if not os.path.exists(os.path.dirname(config['site_dir'])+'/videos.txt'):
        return
    file = open(os.path.dirname(config['site_dir'])+'/videos.txt', "r")
    if os.path.isdir(config['site_dir']+'/videoScreenShot'):
        os.mkdir(config['site_dir']+'/videoScreenShot')
    for i in file.readlines():
        src, dst = i.strip().split(' ')[:2]
        dst = dst.replace('\\', '/').strip()
        src = src.replace('\\', '/').strip()
        if os.path.exists(src) and not os.path.exists(dst):
            cam = cv2.VideoCapture(src)
            frames = []
            while True:
                ret, frame = cam.read()
                if ret:
                    frames.append(frame)
                else:
                    break
            if len(frames)>0:
                cv2.imwrite(dst, frames[int(len(frames)/2)])
            else:
                print("No frames")
            cam.release()
        elif not os.path.exists(src):
            print("Video Error: There is no video in the path you provided ", src)
    cv2.destroyAllWindows()
    file.close()
    #os.remove(os.path.dirname(config['site_dir'])+'/videos.txt')
    #print("Video uploading done")
