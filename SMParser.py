#-*- encoding:utf-8 -*-

import re
import os

def parseDuration(source):
    content = re.findall("\d+", source)
    if len(content):
        return int(content[0])
    else:
        return ""

def readFile(fileName):
	try:
	    f = open(fileName, 'r')
	    return f.read()

	finally:
	    if f:
	        f.close()

def saveInfo(path, infos):
	with open(path, 'wb+') as f:
	    f.write(infos)

def getKeyofList(source):
    splitOfAtList = source.split("at ")
    key = ""
    for index in range(1,len(splitOfAtList)):
        key = key + splitOfAtList[index]
    return key.replace(' ','').replace('\n','')

def mergeAndSort(sourceDict, repeatDict):
    result = dict()
    for key in sourceDict.keys():
        result[sourceDict.get(key)] = repeatDict.get(key)
        if key not in repeatDict:
            print "key: " + key + "\n" + "repeat: " + repeatDict.get(key) + "\n" + "source； " + sourceDict.get(key)
    return sorted(result.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

def saveOfFormat(sourceDict, pathDir):
    result = ""
    count = 1
    for key, value in sourceDict:
        result = result + "NO" + str(count) + ":" + str(value) + "\n" + str(key) + "\n"
        count = count + 1
    saveInfo(pathDir, result)


sourcePath = "log.txt" 
policyViolationDict = dict()
resourceLeaksDict = dict()

policyViolationRepeatDict = dict()
resourceLeaksRepeatDict = dict()

resourceLeaksSplit = "A resource was acquired at attached stack trace but never released"
policyViolationSplit = "StrictMode policy violation"

fileContent = readFile(sourcePath)

# 去掉不相关的信息，并按指定信息拆分
listInfo = re.compile('.+ StrictMode:').sub('', fileContent).split(policyViolationSplit)

for info in listInfo:
    splitInfoList = info.split(resourceLeaksSplit)
    for splitInfo in splitInfoList:
        key = getKeyofList(splitInfo)
        if "android.os.StrictMode$StrictModeDiskReadViolation" in splitInfo:

            # 统计日志重复的次数
            if key in policyViolationRepeatDict.keys():
                policyViolationRepeatDict[key] = int(policyViolationRepeatDict.get(key)) + 1
            else:
                policyViolationRepeatDict[key] = 1

            # 在日志相同的前提下过滤耗时最长的日志
            if key in policyViolationDict.keys():
                if parseDuration(splitInfo) > parseDuration(policyViolationDict.get(key)):
                    policyViolationDict[key] = policyViolationSplit + splitInfo
            else:
                policyViolationDict[key] = policyViolationSplit + splitInfo
        elif "See java.io.Closeable for information on avoiding resource leaks" in splitInfo:

            # 统计日志重复的次数
            if key in resourceLeaksRepeatDict.keys():
                resourceLeaksRepeatDict[key] = int(resourceLeaksRepeatDict.get(key)) + 1
            else:
                resourceLeaksRepeatDict[key] = 1
            resourceLeaksDict[key] = resourceLeaksSplit + splitInfo

saveOfFormat(mergeAndSort(resourceLeaksDict, resourceLeaksRepeatDict), "SM_resource_leaks.txt")
saveOfFormat(mergeAndSort(policyViolationDict, policyViolationRepeatDict), "SM_policy_violation.txt")
