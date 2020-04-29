imageCount = 0
file = None
videoFile = None
videoCount = 0
site_dir = ""
imgSrcs = {}
videoSrcs = {}
videoLinks = {}
imgVals = []
videoVals = []
updated = False
pageName = ""
import os
from staticgennan.utils.videoUpload import uploadVideo

class List:
    def __init__(self, typ = 0):
        self.type = typ
        self.list = []

    def add(self, obj):
        pass

    def add_obj(self, obj):
        self.list.append(obj)

    def get_url(self):
        a = ""
        a1 = ""
        b = "<li>"
        b1 = "</li>"
        if self.type == 0:
            a = ""
            b = ""
            a1 = ""
            b1 = ""
        elif self.type == 1:
            a = "<ul>"
            a1 = "</ul>"
        elif self.type == 2:
            a = "<ol>"
            a1 = "</ol>"
        url = ""
        for i in self.list:
            temp = i.get_url()
            if temp.strip() != '':
                url += b + temp.strip() + b1
            if url.strip() == '':
                return ''
        return a + url.strip() + a1

class Normal:
    def __init__(self):
        self.message = ''

    def add(self, s):
        self.message = s.strip()

    def get_url(self):
        if self.message.strip() == '':
            return ''
        return "<p>" + self.message.strip() + "</p>"


class Heading:
    def __init__(self, size = 2):
        self.size = size

    def add(self, s):
        self.message = s.strip()

    def get_url(self):
        if(self.message.strip == ''):
            return ''
        return "<h{}>{}</h{}>".format(self.size, self.message.strip(), self.size)

class Img:
    def __init__(self):
        self.src = ""

    def add(self, s):
        s = s.strip()
        if(self._link_validate(s)):
            if s in imgSrcs.keys() and imgSrcs[s]:
                self.src = s
                self.dest_src = imgSrcs[s]
            else:
                self.src = s
                temp = self._get_destination(s).strip()
                while temp in imgVals:
                    temp = self._get_destination(s).strip()
                self.dest_src = temp
                imgVals.append(self.dest_src)
                imgSrcs[s] = self.dest_src
                file.write(self.src+" "+site_dir+"/"+self.dest_src+"\n")

    def _link_validate(self,s):
        return True

    def _get_destination(self, s):
        global imageCount
        imageCount += 1
        return "img/image"+str(imageCount)+os.path.splitext(s)[1]

    def get_url(self):
        global pageName
        if pageName!="index":
            return "<img src=\"../{}\" width=150 height=150/>".format(self.dest_src.strip())
        else:
            return "<img src=\"{}\" width=150 height=150/>".format(self.dest_src.strip())

class Video:
    def __init__(self):
        self.link = "#"

    def add(self,s):
        if(self._link_validate(s)):
            self.src = s
            self._transfer_file()



    def _link_validate(self,s):
        return True

    def _transfer_file(self):
        global videoCount, videoSrcs, videoFile
        if self.src in videoSrcs.keys() and self.src in videoLinks.keys():
            self.imgSrc = videoSrcs[self.src]
            self.link = videoLinks[self.src]
        else:
            self.link = uploadVideo(self.src)
            if self.link == '#':
                print('Video with path ', self.src , ' is not uploaded.')
            else:
                self.link = "http://localhost:3000/"+self.link
            videoCount += 1
            temp = "videoScreenShot/image"+str(videoCount)+'.jpg'
            while (temp) in videoVals:
                videoCount += 1
                temp = "videoScreenShot/image"+str(videoCount)+'.jpg'
            self.imgSrc = temp
            videoVals.append(self.imgSrc)
            videoSrcs[self.src] = self.imgSrc.strip()
            videoFile.write(self.src+" "+site_dir+"/"+self.imgSrc.strip()+" " +self.link  +"\n")

    def get_url(self):
        return "<a href=\"{}\"><img src=\"{}\" width=100 height=100/></a>".format(self.link.strip(), self.imgSrc.strip())

class Link:
    def __init__(self):
        self.link = ""
        self.list = []

    def add(self, s):
        if s:
            self.link = s.strip()

    def add_obj(self, obj):
        self.list.append(obj)

    def get_url(self):
        url = ""
        for i in self.list:
            url += i.get_url().strip()
        if url.strip() == '':
            return ''
        return "<a href=\"{}\">{}</a>".format(self.link.strip(), url.strip())

class Raw:
    def __init__(self):
        self.message = ""
    def add(self, s):
        if self._validate(s):
            self.message = s

    def _validate(self, s):
        return True

    def get_url(self):
        return self.message.strip()

ALL_TAGS = ["LARGE", "MEDI", "LINK", "IMG", "VIDEO", "OLIST","ULIST", "LINK", "RAW", "NORM"]
APPEND_FUNC = {
        "LARGE": [Heading, 2],
        "MEDI" : [Heading, 5],
        "LINK" : [Link],
        "IMG" : [Img],
        "VIDEO": [Video],
        "OLIST" : [List, 2],
        "ULIST": [List, 1],
        "RAW": [Raw],
        "NORM": [Normal]
        }

def appendFunc(param):
    params = APPEND_FUNC[param]
    if len(params) == 1:
        return params[0]()
    elif len(params) == 2:
        return params[0](params[1])

def find_label(string):
    for i in ALL_TAGS:
        if i == string[0:len(i)] and string[len(i)] == '(':
            return i
    return ''

class Stack:
    def __init__(self):
        self._list = []
    def push(self, s):
        self._list.append(s)
    def pop(self):
        return self._list.pop()
    def top(self):
        return self._list[self.size() - 1]
    def size(self):
        return len(self._list)

def func(string, i, stack, active = False):#strings,
    s = ''
    while i < len(string):
        s += string[i]
        if string[i] == ' ' or string[i] == '\n' or string[i] == '\t':
            i+=1
            continue
        elif string[i] == "#":

            if s!='':
                stack.top().add(s)
            x = find_label(string[i+1:i+7])
            if len(x) > 0:
                i += len(x) + 2
                if x not in ALL_TAGS:
                    i += 1
                    continue
                if x in ['OLIST', 'ULIST', 'LINK']:
                    active = True
                    stack.push(appendFunc(x))
                    #strings.push('')
                    i = func(string, i, stack)#, strings)
                else:
                    s = ''
                    while i < len(string) and string[i] != ')':
                        s += string[i]
                        i += 1
                    obj = appendFunc(x)
                    obj.add(s)
                    stack.top().add_obj(obj)

        elif string[i] == ')':# and active == True:
            #active = False
            x = stack.pop()
            x.add(s)
            stack.top().add_obj(x)

        i+=1
    return i

def initializeSrcs(imgFileSrc, videoFileSrc):
    global imgSrcs, videoSrcs, imgVals, videoVals, updated, site_dir
    if not updated:
        updated = True
        if os.path.exists(imgFileSrc):
            with open(imgFileSrc, 'r') as imgFile:
                lines = imgFile.readlines()
                for i in lines:
                    val = i.strip().split(' ')
                    if len(val) == 2:
                        value = val[1].strip().replace(site_dir.strip(), "").strip()
                        imgSrcs[val[0].strip()] = value
                        imgVals.append(value)
        if os.path.exists(videoFileSrc):
            with open(videoFileSrc, 'r') as videoFile:
                lines = videoFile.readlines()
                for i in lines:
                    val = i.strip().split(' ')
                    if len(val) == 3:
                        value = val[1].strip().replace(site_dir.strip(), "").strip()
                        videoSrcs[val[0].strip()] = value
                        videoLinks[val[0].strip()] = val[2].strip()
                        videoVals.append(value)

def parseString(string, config, fileName):
    global site_dir, file, videoFile, pageName
    pageName = fileName
    site_dir = config['site_dir']
    initializeSrcs(os.path.dirname(site_dir)+'/images.txt', os.path.dirname(site_dir)+'/videos.txt')
    file = open(os.path.dirname(site_dir)+'/images.txt', "a+")
    videoFile = open(os.path.dirname(site_dir)+'/videos.txt', "a+")
    stack = Stack()
    #strings = Stack()
    stack.push(List())
    #strings.push('')
    func(string, 0, stack)#, strings)
    if (stack.size() == 1):
        obj = stack.pop()
        ret = obj.get_url()
    else:
        print("Parser implementation error")
        print(stack.size())
        ret = ""

    file.close()
    videoFile.close()
    file = None
    videoFile = None
    return ret
