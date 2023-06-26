import os, json, shutil

class cacheItem(object):
    def retriveVideoInfo(self):
        jsonFile = os.path.join(self.__path,'.videoInfo')
        if os.path.exists(jsonFile):
            with open(jsonFile, 'r', encoding='UTF-8') as file:
                # jsonContext = file.read()
                jsonContext = json.load(file)
                self.__group = jsonContext['groupTitle'] # 分组
                self.__title = jsonContext['title'] # 标题
                self.__p = jsonContext['p'] # 章节号
                self.__uname = jsonContext['uname'] # 作者
                file.close()

    def __init__(self, name, path) -> None:
        self.__name = name
        self.__path = path
        self.__title = ''
        self.__group = ''
        self.retriveVideoInfo()
        pass

    def getOutputName(self, targetFolder, isSingleFile):
        name = ''
        if self.__p:
            name = 'p{:0=3d} '.format(self.__p)
        if isSingleFile:
            name = ''
        
        name = name + self.__title
        fn = os.path.join(targetFolder, name + '.mp4')
        # print('文件名: ' + fn)
        return fn
    
    def getFiles(self) -> list[str]:
        files = []
        for file in os.listdir(self.__path):
            if file.endswith('.m4s'):
                files.append(os.path.join(self.__path, file) )
        targetFile = []
        result = len(files) == 2

        # bilibili 离线文件，视频 、音频 规则
        if result:
            if '30280' in files[0] > 0:
                targetFile.append(files[1])
                targetFile.append(files[0])
            else:
                targetFile.append(files[0])
                targetFile.append(files[1])

        return targetFile

    @property
    def title(self):
        return self.__title
    
    @property
    def group(self):
        return self.__group

    def removeDir(self):
        # print('删除文件夹: {}'.format(self.__path))
        shutil.rmtree(self.__path)
        pass
    pass