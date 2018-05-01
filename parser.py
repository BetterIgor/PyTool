# -*- coding: utf-8 -*-
import xlrd
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import re

# 实体类
class Entity:
    def __init__(self, name = "", desc = "", childs = {}, necessary = "false"):
        self.name = name
        self.desc = desc
        self.necessary = necessary
        self.childs = childs

# 构建根结点
def buildRootNode():
	rootDict = {}
	return Entity("rootName","rootDesc",rootDict)

# 读取xlsx
def readXlWithColumns(filePath, sheet):
	data = xlrd.open_workbook(filePath)
	return data.sheet_by_name(sheet)

# 构建实体链表
def buildNode(columns, root):
	rootDict = root.childs
	for i in range(1, columns.nrows):

		secondNodeDict = {}
		lastNodeDict = {}

		# 初始化根节点
		c01 = columns.cell_value(i,1)
		entityLevelOne = Entity(getDesc(c01), "", secondNodeDict)

		# 初始化次节点
		c03 = columns.cell_value(i,3) 
		c02 = columns.cell_value(i,2)
		c08 = columns.cell_value(i,8)
		entityLevelTwo = Entity(c03, getDesc(c02), lastNodeDict, getNecessary(c08))
		
		# 初始化叶节点
		c05 = columns.cell_value(i,5) 
		c04 = columns.cell_value(i,4) 
		c09 = columns.cell_value(i,9)
		entityLevelThree = Entity(c05, getDesc(c04), "", getNecessary(c09))

		if c01 in rootDict.keys(): # 根节点是否命中
			for module in rootDict.get(c01):
				if c03 in module.childs.keys(): # 次节点是否命中
					fillLastNode(rootDict.get(c01), entityLevelThree, c03, c05)
				else:
					fillSecondNode(rootDict.get(c01), entityLevelTwo, c03)
					fillLastNode(rootDict.get(c01), entityLevelThree, c03, c05)
		else:
			fillRootNode(rootDict, entityLevelOne, c01)
			fillSecondNode(rootDict.get(c01), entityLevelTwo, c03)
			fillLastNode(rootDict.get(c01), entityLevelThree, c03, c05)
	return root

def getDesc(desc):
	descSplit = desc.split("_")
	if len(descSplit) > 2:
		desc = ""
		for index in range(1, len(descSplit)):
			desc = desc + descSplit[index]
			if index != len(descSplit) - 1:
				desc = desc + '_'
		return desc
	return descSplit[len(descSplit) - 1]

def getNecessary(necessary):
	return "true" if necessary=="是" else "false"

# 打印所有节点
def display(root):
	for key in root.childs.keys():
		for p in root.childs.get(key):
			print("feature name:" + p.name)
			for pk in p.childs.keys():
				for m in p.childs.get(pk):
					print("	module id:" + m.name + ", desc:" + m.desc + ", necessary:" + m.necessary)
					for mk in m.childs.keys():
						for i in m.childs.get(mk):
							print("		info id:" + i.name + ", desc:" + i.desc + ", necessary:" + i.necessary)

# 填充根节点
def fillRootNode(rootDict, entityLevelOne, c01):
	productsList = []
	productsList.append(entityLevelOne)
	rootDict[c01] = productsList

# 填充次结点
def fillSecondNode(productList, entityLevelTwo, c03):
	for module in productList:
		moduleList = []
		moduleList.append(entityLevelTwo)
		module.childs[c03] = moduleList

# 填充叶结点
def fillLastNode(productsValue, entityLevelThree, c03, c05):
	for module in productsValue:
		for info in module.childs.get(c03):
			infoList = []
			infoList.append(entityLevelThree)
			info.childs[c05] = infoList

def read_xml(in_path):
    return ET.parse(in_path)

# 将xml转换dict
def creat_dict(root):
    dict_new = {}
    for key, valu in enumerate(root):
        dict_init = {}
        list_init = []
        for item in valu:
            list_init.append([item.tag, item.text])
            for lists in list_init:
                dict_init[lists[0]] = lists[1]
        dict_new[key] = dict_init
    return dict_new

# 将字典解析成节点
def toXml(rootNode, nodeNameList):

	# 根节点
    rootXml = ET.Element(nodeNameList[0])
    rootXml.attrib['id'] = "gdpr"
    rootXml.attrib['version'] = "1.0"
    rootChilds = rootNode.childs

    # 开始遍历，填充节点树
    for rootKey in rootChilds.keys():
    	rootList = rootChilds.get(rootKey)
    	for rootNode in rootList:

    		# 填充子节点
		    nodeLevelOne = ET.SubElement(rootXml, nodeNameList[1])
		    nodeLevelOne.attrib['name'] = rootNode.name

		    nodelevelTwo = ET.SubElement(nodeLevelOne, "param")
		    nodelevelTwo.attrib['name'] = "title"
		    nodelevelTwo.attrib['value'] = rootNode.name

		    fillXml(nodeLevelOne, nodeNameList, 2, rootNode)

    return rootXml

# 递归填充结构相同的节点
def fillXml(nodeLevelOne, nodeNameList, index, node):
	if index >= len(nodeNameList):
		return ""
	for childKey in node.childs.keys():
		for childNode in node.childs.get(childKey):
			nodeXml = ET.SubElement(nodeLevelOne, nodeNameList[index])
			nodeXml.attrib['id'] = childNode.name
			nodeXml.attrib['desc'] = childNode.desc
			nodeXml.attrib['necessary'] = childNode.necessary
			fillXml(nodeXml, nodeNameList, index + 1, childNode)

# 将内容输出到文件中
def write_xml(filePath, root):
    content = str(ET.tostring(root, 'utf-8').decode('utf-8'))
    content1 = content.replace('<feature', '\n' + '<feature')
    rough_string = content1.encode('utf-8')
    reared_content = minidom.parseString(rough_string)
    with open(filePath, 'w+', encoding='utf8') as fs:
        reared_content.writexml(fs, addindent="    ", newl="\n", encoding="utf-8")
    return True

if __name__ == '__main__':

	inputFilePath = input("input file path (xlsx): ")
	outFilePath = input("input out path (xml): ")

	if inputFilePath == "":
	   inputFilePath = r"input.xlsx"

	if outFilePath == "":
	   outFilePath = r"output.xml"

	nodeNameList = []
	nodeNameList.append("widget")
	nodeNameList.append("feature")
	nodeNameList.append("module")
	nodeNameList.append("info")

	content = readXlWithColumns(inputFilePath, "Data_map")

	rootNode = buildNode(content, buildRootNode())
	# display(rootNode)

	rootXml = toXml(rootNode, nodeNameList)
	write_xml(outFilePath, rootXml)

