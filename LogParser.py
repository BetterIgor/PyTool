#!/usr/bin/python 
# -*- coding: utf-8 -*-
import re
import os
import time
import math
import csv

# 格式化单个结果
def formatResult(result,addBracket):
	item = []
	content = []
	temp = str(result).split('\'')
	for index in range(len(temp)):
		if index%2 != 0:
			string = temp[index].strip()
			if index == 5 and addBracket:
				string = temp[index].strip() + ")"
			item.append(string)
	content.append(item)
	return content

# 格式化全部结果
def formatResults(result,addBracket):
	content = []
	for item in result:
		content.append(formatResult(item,addBracket))
	return content

# 序列化结果
def serializeResult(firstResult,secondResult,fileName):
	count = 0
	secondKeys = []
	fileWriter = open(fileName + '.log','wb')
	
	for index in range(len(secondResult)):
		secondKeys.append(secondResult[index][0][2])
	with open( fileName + '.csv', 'wb') as csvfile:
		spamwriter = csv.writer(csvfile,dialect='excel')
	   	spamwriter.writerow(['date', 'userId', 'sessionId', 'cplc', 'riskInfo'])
		for i in range(len(firstResult)):
			j = secondKeys.index(firstResult[i][0][1])
			if  j > -1:
				spamwriter.writerow([str(firstResult[i][0][0]),str(secondResult[j][0][0]),str(secondResult[j][0][2]),str(secondResult[j][0][1]),str(firstResult[i][0][2])])
				result = str(firstResult[i][0][0] + " " + secondResult[j][0][0] + " " + secondResult[j][0][2] + " " + secondResult[j][0][1] + " " + firstResult[i][0][2]) + "\n"
				fileWriter.write(result)
				print result
		fileWriter.close()

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

start = time.clock()
firstRe = "(\d*:\d*:\d*.\d*).*tsmSessionId:(.*?), .*riskInfo:(.*?)\)"
secondRe = "userId:(.*), cplc:(.*), tsmSessionId:(.*?),"

firstResult = []
secondResult = []
for line in open("tsm-middletier.stdout.log.20160906"):  
	if line.find("riskInfo") > -1 :
		first = re.findall(firstRe,line)
		firstResult.append(first)
	elif line.find("userId") > -1 and line.find("cplc") > -1 and line.find("tsmSessionId") > -1 :
		second = re.findall(secondRe,line)
		secondResult.append(second)

serializeResult(formatResults(firstResult,True),formatResults(secondResult,False),"rererereer")
end = time.clock()
print formatSeconds(end - start)
