#-*- coding: UTF-8 -*- 
import xml.etree.ElementTree as ET
import os
import sys
import json

levelMax = 1
 
#遍历所有的节点
def walkData(rootNode, level, resultList):
    global levelMax
    tempList =[levelMax, level, rootNode.tag]
    resultList.append(tempList)
    
    #遍历每个子节点
    childrenNode = list(rootNode)
    if len(childrenNode) == 0:
        if(levelMax < level):
            levelMax = level
        return
    for child in childrenNode:
        walkData(child, level + 1, resultList)
    return

def findMaxLevel(fileName):
   level = 1
   resultList = []
   root = ET.parse(fileName).getroot()
   walkData(root, level, resultList)
   return resultList
 
if __name__ == '__main__':

   dirPath = sys.argv[1]
   result = dict()
   for parent, dirnames, filenames in os.walk(dirPath,  followlinks=True):
      for fileName in filenames:
         if (fileName.endswith("xml")):
            levelMax = 1
            filePath = os.path.join(parent, fileName)
            findMaxLevel(str(filePath))
            result[filePath] = levelMax

   sortedResult = sorted(result.items(), key=lambda result:result[1], reverse=True)

   resultFormater = {
     "LEVEL_MAX":'',
     "LEVEL_AVG":'',
     "DATA_LIST":[]
   }

   sumLevel = 0
   for levelInfo in sortedResult:
      sumLevel = sumLevel + levelInfo[1]
      resultFormater["DATA_LIST"].append(levelInfo)

   resultFormater["LEVEL_MAX"] = resultFormater["DATA_LIST"][0][1]
   resultFormater["LEVEL_AVG"] = round(sumLevel / len(resultFormater["DATA_LIST"]), 2)
   print(json.dumps(obj=resultFormater))

