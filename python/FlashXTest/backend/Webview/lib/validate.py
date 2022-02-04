#!/usr/bin/env python
import littleParser


def validatePath(target):
	PATH_TO_CONFIG= '../config'
	if target.find('..') != -1:
		raise Exception('Access Denied to %s' % (target,))
	configDict = littleParser.parseFile(PATH_TO_CONFIG)
	pathToOutdirs = configDict.get("pathToOutdir",[])

	if isinstance(pathToOutdirs, (list,tuple)):
		for p in pathToOutdirs:
			p = p.strip()
			if p == target[:len(p)] :
				break
		else:
			raise Exception('Access Denied to %s' %(target,)) 

	else:
		if not pathToOutdirs == target[:len(pathToOutdirs)] :
			raise Exception('Access Denied to %s' %(target,)) 



	return 
