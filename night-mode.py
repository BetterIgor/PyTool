#!/usr/bin/python 
# -*- coding: utf-8 -*-

import re
import os
import math

# 解析字段，返回list
def parseField(readContent):
	if(readContent != ""):
		readContent = re.findall(r"=\"(.+?)\">(.*)<",readContent.decode('UTF-8'))
		return readContent

# 解析文件内容
def parseFile(path):
	fileReader = open(path,'rb')
	try:
		readContent = fileReader.read()
		return readContent
	finally:
		fileReader.close()

def writeFile(filePath, contentDict):
	fileWriter = open(filePath,'wb')
	try:
		fileWriter.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<resources>\n")
		for key, value in contentDict:
			fileWriter.write("    <color name=\"" + key + "\">" + value + "</color>\n")
		fileWriter.write("</resources>")
	finally:
		fileWriter.close()

# 打印解析后的字段列表
def printResult(content):
	for data in content:
		print(data[0] + "=" + data[1])
	print ("个数：" + str(len(content)))

# 将小写字母的颜色值全部转成大些字母，颜色不区分大小写，引用保持不变
def list2Dict(fields):
	resultDict = dict()
	for field in fields:
		if(field[1].startswith("#")):
			resultDict[field[0]] = field[1].upper()
		else:
			resultDict[field[0]] = field[1]
	return resultDict

def printFormater(res):
	print("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<resources>")
	for key, value in res:
		print("    <color name=\"" + key + "\">" + value + "</color>")
	print("</resources>")
	print(len(res))

if __name__=="__main__":

	filePath = "colors.xml"

	if(os.path.exists(filePath)):
		sourceFile = parseFile(filePath)

		dic = list2Dict(parseField(sourceFile))
		resultDict = dict()
		for key in dic:
			resultValues = list(resultDict.values())
			sourceValue = dic[key]
			if(sourceValue in resultValues):
				resultDict[key] = "@color/" + list(resultDict.keys())[resultValues.index(sourceValue)]
			else:
				resultDict[key] = dic[key]

		res = sorted(resultDict.items(), key=lambda item: item[1], reverse=False)

		# 格式化输出即可得到结果，输出到文件顺序会乱掉
		printFormater(res)
		# writeFile("./colors_new.xml", res);

	else:
		print("file not exists")
