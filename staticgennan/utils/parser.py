imageCount = 0
file = None
videoFile = None
videoCount = 0
site_dir = ""
imgSrcs = {}
videoSrcs = {}
import os

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
            if i.get_url().strip() != '':
                url += b + i.get_url().strip() + b1
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
        if(self._link_validate(s)):
            if s in imgSrcs.keys() and imgSrcs[s]:
                self.src = s
                self.dest_src = imgSrcs[s]
            else:
                self.src = s
                self.dest_src = self._get_destination(s)
                imgSrcs[s] = self.dest_src
                file.write(self.src+" "+site_dir+"/"+self.dest_src+"\n")

    def _link_validate(self,s):
        return True

    def _get_destination(self, s):
        global imageCount
        imageCount += 1
        return "img/image"+str(imageCount)+os.path.splitext(s)[1]

    def _transfer_file(self):
        pass

    def get_url(self):
        self._transfer_file()
        return "<img width=150 height=150 src=\"{}\"/>".format(self.dest_src.strip())

class Video:
    def __init__(self):
        self.link = ""

    def add(self,s):
        if(self._link_validate(s)):
            self.src = s
            self._transfer_file()



    def _link_validate(self,s):
        return True

    def _transfer_file(self):
        self.link = "https://www.google.com"
        global videoCount, videoSrcs, videoFile
        if self.src in videoSrcs.keys() and videoSrcs[self.src]:
            self.imgSrc = videoSrcs[self.src]
        else:
            videoCount += 1
            self.imgSrc = "videoScreenShot/image"+str(videoCount)+'.jpg'
            videoSrcs[self.src] = self.imgSrc
            videoFile.write(self.src+" "+site_dir+"/"+self.imgSrc+"\n")

    def get_url(self):
        return "<a href=\"{}\"><img width=100 height=100 src=\"{}\"/></a>".format(self.link.strip(), self.imgSrc.strip())

class Link:
    def __init__(self):
        self.link = ""
        self.list = []

    def add(self, s):
        if s:
            self.link = s

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
        "LARGE": Heading(2),
        "MEDI" : Heading(4),
        "LINK" : Link(),
        "IMG" : Img(),
        "VIDEO": Video(),
        "OLIST" : List(2),
        "ULIST": List(1),
        "RAW": Raw(),
        "NORM": Normal()
        }

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

def func(string, i, stack, strings, active = False):
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
                    stack.push(APPEND_FUNC[x])
                    strings.push('')
                    i = func(string, i, stack, strings)
                else:
                    s = ''
                    while i < len(string) and string[i] != ')':
                        s += string[i]
                        i += 1
                    obj = APPEND_FUNC[x]
                    obj.add(s)
                    stack.top().add_obj(obj)

        elif string[i] == ')':# and active == True:
            #active = False
            x = stack.pop()
            x.add(s)
            stack.top().add_obj(x)

        i+=1
    return i

def parseString(string, config, fileName):
    global site_dir, file, videoFile
    site_dir = config['site_dir']
    file = open(os.path.dirname(site_dir)+'/images.txt', "+w")
    videoFile = open(os.path.dirname(site_dir)+'/videos.txt', "+w")
    print("Parser entered doing the stuff")
    stack = Stack()
    strings = Stack()
    stack = Stack()
    strings = Stack()
    stack.push(List())
    strings.push('')
    func(string, 0, stack, strings)
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
