import os
import imageCompress
import cv2

def transferImage(config):
    if not os.path.exists(os.path.dirname(config['site_dir'])+'/images.txt'):
        return
    file = open(os.path.dirname(config['site_dir'])+'/images.txt', "r")
    os.mkdir(config['site_dir']+'/img')
    for i in file.readlines():
        src, dst = i.strip().split(' ')[:2]
        dst = dst.replace('\\', '/')
        print(dst)
        src = src.replace('\\', '/')
        print(src)
        imageCompress.compress(src.strip(), 2, dst.strip())
        print(i)
    file.close()
    os.remove(os.path.dirname(config['site_dir'])+'/images.txt')
    print("Image uploading done")

    if not os.path.exists(os.path.dirname(config['site_dir'])+'/videos.txt'):
        return
    file = open(os.path.dirname(config['site_dir'])+'/videos.txt', "r")
    os.mkdir(config['site_dir']+'/videoScreenShot')
    for i in file.readlines():
        src, dst = i.strip().split(' ')[:2]
        dst = dst.replace('\\', '/')
        print(dst)
        src = src.replace('\\', '/')
        print(src)
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
    cv2.destroyAllWindows()
    file.close()
    os.remove(os.path.dirname(config['site_dir'])+'/videos.txt')
    print("Video uploading done")
