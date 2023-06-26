import os, re
from offlineCacheItem import cacheItem

class GroupedItem(object):
    def __init__(self, group) -> None:
        self.__group = group
        self.__cacheItems : list[cacheItem] = []
        self.__isSingleFile = False
        pass

    def equals(self,dest):
        return self.__group == dest
        
    def add(self, cacheItem):
        if cacheItem and cacheItem not in self.__cacheItems:
                self.__cacheItems.append(cacheItem)
        pass

    def makeDir(self, root):
        destRoot = root
        group = self.__group
        if group and len(self.__cacheItems) > 1:
            if len(group) >= 200:
                group = group[0:200]
            destRoot = os.path.join(root, re.sub(r"[\/\\\:\*\?\"\<\>\|]",'-', group)) # 去掉路径中的非法字符
        else:
            destRoot = os.path.join(root, '零散')
            self.__isSingleFile = True

        if not os.path.exists(destRoot):
            os.makedirs(destRoot)

        return destRoot
    pass

    @property
    def cacheItems(self):
        return self.__cacheItems
    
    @property
    def IsSingleFile(self):
        return self.__isSingleFile

    @property
    def group(self):
        return self.__group
    pass