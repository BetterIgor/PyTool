#-*- encoding:utf-8 -*-

import re
import os
import json
import sys

# 秒转时间段
def secondToInterval(seconds):
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	return "%02d:%02d:%02d" % (h, m, s)

def readFile(fileName):
	try:
	    f = open(fileName, 'r')
	    return f.read()

	finally:
	    if f:
	        f.close()

def getFileSize(filePath):
	fsize = os.path.getsize(filePath)
	fsize = fsize/float(1024)
	return round(fsize, 2)

def saveData():
	outputPath = resultSummary['包名'] + "/" + resultSummary['版本名']
	isExists = os.path.exists(outputPath)
	if not isExists:
	    os.makedirs(outputPath)
	with open(outputPath + "/" + simpleDataFileName, 'w+') as f:
		f.write(json.dumps(obj=resultSummary))

	with open(outputPath + "/" + dataFileName, 'w+') as f:
		for tag in tagDict:
			f.write("\n\n>>>>>>>>>>>>>>>>>>>>" + str(tag) + "<<<<<<<<<<<<<<<<<<<\n")
			f.write(json.dumps(obj=tagDict[tag]))

		f.write("\n\n>>>>>>>>>>>>>>>>>>>>解析失败的数据<<<<<<<<<<<<<<<<<<<\n")
		for item in exceptionList:
			f.write(item)

def parsePreVersionInfo():
	dirList = []
	for dirName in os.listdir(resultSummary['包名'] + "/"):
		if(dirName.startswith(".")):
			continue
		else:
			dirList.append(dirName)
	dirList.sort(reverse=True)
	return json.loads(readFile(resultSummary['包名'] + "/" + dirList[0] + "/" + simpleDataFileName))

def processData():
	for index in range(0, len(timeList)):
		splits = timeList[index].split(":")
		timeList[index] = float(splits[0]) * 3600 + float(splits[1]) * 60 + float(splits[2])
	timeList.sort()
	resultSummary["测试时长"] = secondToInterval(timeList[len(timeList) - 1] - timeList[0])

	pageLoadInfoList = []
	for tag in tagDict:
		if("BASE_INFO" == tag):
			baseInfo = tagDict[tag][0]
			resultSummary["包名"] = baseInfo['APP_PACKAGE_NAME']
			resultSummary["版本名"] = baseInfo['APP_VERSION_NAME']
			resultSummary["版本号"] = baseInfo['APP_VERSION_CODE']
			resultSummary["最小版本号"] = baseInfo['APP_MIN_SDK_VERSION']
			resultSummary["目标版本号"] = baseInfo['APP_TARGET_SDK_VERSION']
			resultSummary["系统版本"] = baseInfo['SYSTEM_VERSION']
			resultSummary["设备型号"] = baseInfo['SYSTEM_BRAND']

		elif("PAGELOAD" == tag):
			pageHash = dict()
			for page in tagDict[tag]:
				events = page['allEvents']
				pageInfo = events[0]['pageInfo']
				pageHash[pageInfo['pageHashCode']] = pageInfo['pageClassName']
				for event in events:
					pageLoadInfoList.append(event)
			resultSummary["测试页面"] = str(len(pageHash.keys())) + "个"
		elif "STARTUP" == tag:
			tempDict = {}
			for startUp in tagDict[tag]:
				if startUp['startupType'] in tempDict.keys():
					tempDict[startUp['startupType']].append(startUp['startupTime'])
				else:
					tempList = []
					tempList.append(startUp['startupTime'])
					tempDict[startUp['startupType']] = tempList

			startUpResult = ""
			for su in tempDict.keys():
				tempDict[su].sort(reverse=True)
				startUpResult = startUpResult + "类型: " + str(su) + ", 最长耗时: " + str(tempDict[su][0]) + "ms, 平均耗时: " + str(sum(tempDict[su]) / len(tempDict[su])) + "ms "

			resultSummary["启动"] = startUpResult
		elif "LEAK" == tag:
			tagDict[tag].sort(key=lambda x:(x['leakObjectName'],x['leakObjectName']), reverse=True)

			resultSummary["内存泄漏"] = str(len(tagDict[tag])) + "次"
		elif "SM" == tag:
			tagDict[tag].sort(key=lambda x:(x['longBlockInfo']['blockTime'],x['longBlockInfo']['blockTime']), reverse=True)

			sumCost = 0
			for sm in tagDict[tag]:
				sumCost = sumCost + sm['longBlockInfo']['blockTime']
			resultSummary["卡顿"] = str(len(tagDict[tag])) + "次, " + "最长耗时：" + str(tagDict[tag][0]['longBlockInfo']['blockTime']) + "ms, 平均耗时：" +  str(sumCost / len(tagDict[tag])) + "ms"
		elif "BATTERY" == tag:
			resultSummary["耗电量"] = str(tagDict[tag][len(tagDict[tag]) - 1]['level'] - tagDict[tag][0]['level']) + "%"
		elif "CPU" == tag:
			# 待定
			tagDict[tag].sort(key=lambda x:(x['appCpuRatio'],x['appCpuRatio']), reverse=True)

			sumCost = 0
			for sm in tagDict[tag]:
				sumCost = sumCost + sm['appCpuRatio']
			resultSummary["CPU"] = "最大使用率：" + str(round(tagDict[tag][0]['appCpuRatio'] * 100,2)) + "%, 平均使用率：" + str(round((sumCost/len(tagDict[tag])) * 100, 2)) + "%"
		elif "FPS" == tag:
			tagDict[tag].sort(key=lambda x:(x['currentFps'],x['currentFps']), reverse=False)

			sumCost = 0
			for fps in tagDict[tag]:
				sumCost = sumCost + fps['currentFps']
			resultSummary["流畅度"] = "平均值：" + str(round(sumCost/len(tagDict[tag]),2)) + "帧/秒"
		elif "RAM" == tag:
			tagDict[tag].sort(key=lambda x:(x['availMemKb'],x['availMemKb']), reverse=False)
			sumCost = 0
			for ra in tagDict[tag]:
				sumCost = sumCost + ra['totalMemKb'] - ra['availMemKb']
			resultSummary["RAM"] = "最大占用：" + str(tagDict[tag][0]['totalMemKb'] - tagDict[tag][0]['availMemKb']) + "KB, 平均占用：" + str(round(sumCost/len(tagDict[tag]),2)) + "KB"
		elif "HEAP" == tag:
			tagDict[tag].sort(key=lambda x:(x['freeMemKb'],x['freeMemKb']), reverse=False)
			sumCost = 0
			for heap in tagDict[tag]:
				sumCost = sumCost + heap['maxMemKb'] - heap['freeMemKb']
			resultSummary["HEAP"] = "最大占用：" + str(tagDict[tag][0]['maxMemKb'] - tagDict[tag][0]['freeMemKb']) + "KB, 平均占用：" + str(round(sumCost/len(tagDict[tag]),2)) + "KB"
		# else:
		# 	print(tag)
		# 	print(tagDict[tag][0])


	pageLoadInfoList.sort(key=lambda x:(x['endTimeMillis'],x['startTimeMillis']))
	pageLoadMax = pageLoadInfoList[0]
	loadPageSumCost = 0
	for pageInfo in pageLoadInfoList:
		loadPageSumCost = loadPageSumCost + pageInfo['endTimeMillis'] - pageInfo['startTimeMillis']
	resultSummary['生命周期'] = "最长耗时: " + str(pageLoadMax['endTimeMillis'] - pageLoadMax['startTimeMillis']) + "ms, 平均耗时: " + str(round(loadPageSumCost /  len(pageLoadInfoList), 2)) + "ms"


	# 计算View层级
	print(apkPath)
	os.system("java -jar /Users/igor/tools/decompile/apktool_2.4.1.jar d -f " + apkPath + " -o app")
	os.system("python3 /Users/igor/workspace/python/layoutParser/LayoutParser.py /Users/igor/workspace/python/eyeLogParser/app/res/layout > "+resultSummary['包名'] + "/" + resultSummary['版本名']+"/" + layoutLevelFilename)
	layoutLevel = json.loads(readFile(resultSummary['包名'] + "/" + resultSummary['版本名'] + "/" + layoutLevelFilename))
	resultSummary["View层级"] = "最大值：" + str(layoutLevel["LEVEL_MAX"]) + ", 平均值：" + str(layoutLevel["LEVEL_AVG"])

	resultSummary["APK大小"] = str(getFileSize(apkPath)) + "KB"

def parseData():
	for line in open(sourcePath): 
		if line.find("Eye") > -1:
			matachLine = re.findall(flagRe,line)
			try:
				for time, tag, data in matachLine:
					timeList.append(time)
					if(tag in tagDict.keys()):
						tagDict[tag].append(json.loads(data))
					else:
						childList = []
						childList.append(json.loads(data))
						tagDict[tag] = childList
			except BaseException:
			    exceptionList.append("TAG:" + tag + ", DATA:" + data)
		else:
			continue
			
def printOnlyCurrentInfo():
	for title in resultSummary:
		if("===" in title):
			print(str(title))
		else:
			print(str(title) + " : " + str(resultSummary[title]))

def printCompareInfo():
	preVersionInfo = parsePreVersionInfo()
	for title in resultSummary:
		if("===" in title):
			print(str(title))
		else:
			print(str(title) + " : " + str(resultSummary[title]) + " | " + str(preVersionInfo[title]))

if __name__=="__main__":
	tagDict = dict()
	flagRe = "(\d+:\d+:\d+.\d+).*tag:(.*) data:(.*)"
	exceptionList = []
	timeList = []
	sourcePath = "log.txt" 
	simpleDataFileName = "simple_data.txt"
	dataFileName = "data.txt"
	layoutLevelFilename = "layoutLevel.txt"
	apkPath = sys.argv[1]

	resultSummary = {
		'\n===================基本信息===================' : '',
		'包名' : '',
		'版本名' : '',
		'版本号' : '',
		'最小版本号' : '',
		'目标版本号' : '',
		'系统版本' : '',
		'设备型号' : '',
		'测试时长' : '',
		'测试页面' : '',
		'\n===================优化指标===================' : '',
		'启动' : '',
		'流畅度' : '',
		'内存泄漏' : '',
		'耗电量' : '',
		'CPU' : '',
		'HEAP' : '',
		'RAM' : '',
		'生命周期' : '',
		'APK大小':'',
		'View层级':''
	}

	parseData()

	processData()

	printOnlyCurrentInfo()
	# printCompareInfo()

	saveData()


