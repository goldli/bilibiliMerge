# from typing import ClassVar
from PySide6.QtCore import *
import os, re , time, math
from offlineCacheItem import cacheItem
from groupedItem import GroupedItem

class MergeOption(object):
    def __init__(self, ffmpegFile, cachePath, deleteFilesWhenFinished) -> None:
        self.__ffmpeg = ffmpegFile
        self.__cachePath = cachePath
        self.__deleteFilesWhenFinished = deleteFilesWhenFinished
        pass

    @property
    def ffmpeg(self):
        return self.__ffmpeg

    @property
    def cachePath(self):
        return self.__cachePath
    
    @property
    def deleteFilesWhenFinished(self):
        return self.__deleteFilesWhenFinished 
    pass

class ProgressBarThread(QThread):
    ffmpeg = r'{} -loglevel quiet -i "{}" -i "{}" -c copy "{}"'
    '''
    更新进度条
    '''
    onBeginMergeFile = Signal(str)
    onMergedFile = Signal(str, float)  # 合并了一个文件
    onMergeFileFailed = Signal(str)
    onBeginGroup = Signal(str)
    onMergeCompleted = Signal(str) # 全部完成
    onRewriteFileError = Signal(str)

    def __init__(self):
        super().__init__()  # 初始化父级
        pass

    def __rewriteFile(self, fileName, fileIndex) -> bool:
        '''
            对bilibili 离线文件进行去除文件头部9个0 处理
        '''
        tmpFile = fileName + ('.mp4' if fileIndex == 0 else '.mp3')
        if os.path.exists(tmpFile): 
            return True
        try:
            with open(fileName, 'rb') as file: # https://zhuanlan.zhihu.com/p/631220387
                file.seek(9)
                context = file.read()

                with open(tmpFile, 'wb') as tvideo:
                    tvideo.write(context)
                    tvideo.close()

                file.close()

            return True
        except Exception as e:
            self.onRewriteFileError.emit(str(e))
            return False
        pass

    def __mergeFile(self, cacheItem : cacheItem, targetFolder, isSingleFile) -> bool:
        destFileName = cacheItem.getOutputName(targetFolder, isSingleFile)
        if os.path.exists(destFileName):
            # print('文件已存在：' + destFileName)
            return True

        files = cacheItem.getFiles()
        if len(files) == 0:
            # print('\033[0;37;41m跳过目录： ' + cacheItem.name + '\033[0m')
            return True

        fileIndex = 0
        for file in files:
            if not self.__rewriteFile(file, fileIndex):
                return False
            fileIndex +=1

        cmd = self.ffmpeg.format(self.__opt.ffmpeg, files[0]+'.mp4', files[1]+'.mp3', destFileName)
        # print(cmd)
        try:
            os.system(cmd)
            os.remove(files[0]+'.mp4')
            os.remove(files[1]+'.mp3')
        except Exception as e:
            self.onMergeFileFailed.emit(e)
            return False
            # print(e)
        return True
        pass
    
    def run(self):
        """
            子线程执行时执行此函数
            长时间的操作过程要在这里完成。
            self.{信号变量}.emit 输出结果。
        """
        total = 0
        for groupedItem in self.__groupedItems:
            self.onBeginGroup.emit(groupedItem.group)
            destDir = groupedItem.makeDir(self.__opt.cachePath)
            for cacheItem in groupedItem.cacheItems:
                self.onBeginMergeFile.emit(cacheItem.title)
                if self.__mergeFile(cacheItem, destDir, groupedItem.IsSingleFile):
                    total +=1
                    self.onMergedFile.emit(cacheItem.title, total * 100 / self.__filesCount)
                    if self.__opt.deleteFilesWhenFinished:
                        cacheItem.removeDir()

        self.onMergeCompleted.emit('合并操作完成。成功：{}/{}'.format(total, self.__filesCount))
        pass
    
    def Execute(self, filesCount: int, opt: MergeOption, groupedItems: list[GroupedItem]):
        self.__filesCount = filesCount
        self.__opt = opt
        self.__groupedItems = groupedItems

        self.start()
        pass

    pass

class BilibiliMerge(ProgressBarThread):
    onSuccessGetFiles = Signal(int) # 获取到待合并的文件数量
    onFailedGetFiles = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        pass

    def __getFiles(self, cachePath : str) -> list[cacheItem]:
        '''
            查找目录下的有效文件
        '''
        cacheItems = []
        try:
            for sub in os.listdir(cachePath):
                subdir = cachePath + '\\' + sub
                if os.path.isdir(subdir):
                    if re.search('[^\d]', sub) == None: # 文件夹的名称是数字
                        cacheItems.append(cacheItem(sub, subdir))
            return cacheItems
        except Exception as ex:
            # print(ex)
            self.onFailedGetFiles.emit(str(ex))
            return None
        pass

    def __reorganized(self, cacheItems : list) -> list[GroupedItem]:
        filesCount = len(cacheItems)

        if filesCount == 0:
            return None
        
        groupedItems : list[GroupedItem] = []
        for i in range(filesCount):
            group = cacheItems[i].group # 目标文件夹名称
            
            targetItem = None

            for item in groupedItems:
                if item.equals(group):
                    targetItem = item
                    break
            if targetItem == None:
                targetItem = GroupedItem(group)
                groupedItems.append(targetItem)

            targetItem.add(cacheItems[i])
        return groupedItems

    def Execute(self, opt: MergeOption):
        files = self.__getFiles(opt.cachePath)
        if files == None:
            return
        
        filesCount = len(files)
        self.onSuccessGetFiles.emit(filesCount)

        groupedItems = self.__reorganized(files)
        if groupedItems:
            super().Execute(filesCount, opt, groupedItems)
        pass

    def Cancel(self):
        self.quit()
        pass


    pass