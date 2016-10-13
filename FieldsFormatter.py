#!/usr/bin/python 
# -*- coding: utf-8 -*-

import re
import os
import datetime
import time
import math

# 解析字段，返回list
def parseField(readContent):
	if(readContent != ""):
		readContent = re.findall(r"=(.+?)>(.*)<",readContent)
		return readContent

# 解析文件内容
def parseFile(path):
	fileReader = open(path,'rb')
	try:
		readContent = fileReader.read()
		return readContent
	finally:
		fileReader.close()

# 将补丁写入文件
def patchFile(filePath,patch):
	fileWriter = open(filePath,'a')
	try:
		fileWriter.write("    <!--new patch-->\n")
		for key,value in patch:
			fileWriter.write("    <string name=" + key + ">" + value + "</string>\n")
		fileWriter.write("</resources>")
	finally:
		fileWriter.close()

# 将国际化后字段的值写入文件
def writeFile(newFilePath,fileContent):
	patchName = "_formated"
	fileWriter = open(newFilePath + patchName,'w')
	try:
		fileWriter.write(fileContent)
	finally:
		fileWriter.close()

# 打印解析后的字段列表
def printResult(content):
	for data in content:
		print(data[0] + "=" + data[1])
	print "个数：" + str(len(content))

# 获得补丁
def getPatch(first,second):
	firstKeys = []
	newList = []
	for item in first:
		firstKeys.append(item[0])
	for item in second:
		if(item[0] not in firstKeys):
			newList.append(item)
	return newList

# 获得字段的 name列表
def getKeys(fieldList):
	fieldKeys = []
	for item in fieldList:
		fieldKeys.append(item[0])
	return fieldKeys

# 获得字段对应的值列表
def getValues(fieldList):
	fieldValues = []
	for item in fieldList:
		fieldValues.append(item[1])
	return fieldValues

# 拷贝文件，并去掉文件最后一行
def copyFileWithNoEndLine(sourcePath,targetPath):
	try:
		sourceFile = open (sourcePath)
		targetFiles = open(targetPath, 'wb') 
		lines = sourceFile.readlines()     
		curr = lines[:-1]
		targetFiles.writelines(curr)
	finally:
		targetFiles.close( )
		sourceFile.close()

# 生成新文件，并打入补丁
def patchField(sourcePath,targetPath,patch):
	copyFileWithNoEndLine(sourcePath,targetPath)
	patchFile(targetPath,patch)

# 国际化对应字段的值
def globalizationField(source,target):
	targetfields = parseField(target)
	targetKeys = getKeys(targetfields)
	targetValues = getValues(targetfields)
	sourceKeys = getKeys(parseField(source))
	for item in sourceKeys:
		if(item in targetKeys):
			regex = re.compile(item + '>(.*)<')
			targetValue = targetValues[targetKeys.index(item)]
			source = regex.sub( item + '>' + targetValue + '<',source)
	return source

def moveRootPath():
	rootDir =  "./FieldsFormatter/"
	if(not os.path.exists(rootDir)):
		os.makedirs(rootDir)
	os.chdir(rootDir)

def getCurrentTime():
	return str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 将秒格式化成时间段
def formatSeconds(allTime):
    day = 24*60*60
    hour = 60*60
    min = 60
    if allTime <60:
        return  "%d sec"%math.ceil(allTime)
    elif  allTime > day:
        days = divmod(allTime,day)
        return "%d days, %s"%(int(days[0]),formatSeconds(days[1]))
    elif allTime > hour:
        hours = divmod(allTime,hour)
        return '%d hours, %s'%(int(hours[0]),formatSeconds(hours[1]))
    else:
        mins = divmod(allTime,min)
        return "%d mins, %d sec"%(int(mins[0]),math.ceil(mins[1]))

"""
def listToDict(listContent):
	dict_content = {}
	for i in listContent:
		dict_content[i[0]] = i[1]
	return dict_content
"""
if __name__=="__main__":
	start = time.clock()
	#editPath = raw_input("Enter a file you want to edit : ");		# 要修改的文件
	#referPath = raw_input("Enter a file to be refer to : ");		# 参照的文件

	editPath = "a"
	referPath = "b"
	patchPath = "all.xml"

	if(os.path.exists(editPath) & os.path.exists(referPath)):
		editFile = parseFile("chinese.xml")
		referFile = parseFile("english.xml")
#		moveRootPath()

		# 打入补丁，保证字段的完整性
		patchField(editPath,patchPath,getPatch(parseField(editFile), parseField(referFile)))
		# 将字段国际化并写入新文件
		patchFile = parseFile(patchPath)
		writeFile(editPath, globalizationField(patchFile,editPath))
		writeFile(referPath, globalizationField(patchFile,referFile))
	else:
		print "file not exists"

	#moveFile("chinese.xml","all.xml")
	#patchFile(english);
	#printResult(getPatch(chinese,english))
	#printResult(english)
	#print(len(english))
	end = time.clock()
	print formatSeconds(end - start)
