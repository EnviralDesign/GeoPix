import string
import uuid
import os.path
import time
import re

geoHolder 	= op.sceneOutliner.op("geoHolder")
# treeInfo 	= op.sceneOutliner.op("null_treeInfo_V2")
treeInfo 	= op.sceneOutliner.op("null_treeInfo_V3")

### given a string, look through geoHolder and
### come up with a name that is not already used.
### this references the Name custom param, not the
### nodes actual name which is a unique UUID
def makeNameUnique(myOp):
	newName = ""
	# if we're working with an OP, we're going to just rename it.
	if(op(myOp)): 
		myOp = op(myOp)
		if(myOp.par.Name):
			oldName = myOp.par.Name.val
			myNames  = []
			found = geoHolder.findChildren(tags=["ObjectType"])
			myNames = [ str(x.par.Name) for x in found ]
				# myNames += [ op(x.val).par.Name.val ]
			newName = mod.globalFuncs.uniquifyString(oldName, myNames)
			# print(myOp.par.Name, newName)
			myOp.par.Name = newName
			
			return None
	
	# if we were given a string, we're going to return a new one.
	elif( "str" in str(type(myOp))):
		oldName = myOp
		myNames  = []
		# for x in treeInfo.col("opPath")[1::]:
		for x in treeInfo.col("path")[1::]:
			myNames += [ op(x.val).par.Name.val ]
		newName = mod.globalFuncs.uniquifyString(oldName, myNames)
		return newName
	
	# if it's anything else, complain about it to user.
	else:
		debug("script requires argument to be OP with cust par Name, or str")

		
		
		
		
### Helper function that returns true if string contains
### digits, false if contains no digits.
def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)

### generate a unique UUID that will never exist again 
### This is to make user created things unique where names can be the same.
# def getUUID():
	# result = str(uuid.uuid4().int)
	# return result

def getEPOCH():
	return int(round(time.time() * 1000))
	
def getNextFreeID():
	found = geoHolder.findChildren(tags=["ObjectType"])
	currentIds = [x.par.Id.val for x in found]
	smallestUnused = next(i for i, e in enumerate(sorted(currentIds) + [ None ], 1) if i != e)
	
	print("ahh")
	return smallestUnused

### sorts hierarchy path text via os.path python utilities.
def sortHierarchyPathText(pathTextLump):
	files = pathTextLump.split("\n")
	std = sorted(files, key=lambda file: (os.path.dirname(file), os.path.basename(file)))
	sortedPaths = ""
	
	for i in range(1,len(std)):
		if os.path.dirname(std[i]) != os.path.dirname(std[i-1]):
			print("")
		print(std[i])
		sortedPaths += std[i] + "\n"
	
	return sortedPaths
	
	
def natural_sort(l): 
	convert = lambda text: int(text) if text.isdigit() else text.lower() 
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
	return sorted(l, key = alphanum_key)
	
	
def patternExpand(pattern):
	
	try:
		pattern = pattern.replace(' ', '')
		if pattern != '*':
		
			patSplit = pattern.split(',')
			patExpanded = []
			for x in patSplit:
				if ':' not in x:
					patExpanded += [int(x)]
				else:
					pair = list(map(int,x.split(':')))
					if pair[0] > pair[1]:
						pairRange = list(range(pair[1],pair[0]+1))[::-1]
					else:
						pairRange = list(range(pair[0],pair[1]+1))
					patExpanded += pairRange
			
					pattern = ','.join(list(map(str,patExpanded)))
	except:
		debug('Error in pattern expansion.')
	
	return pattern