

################### SAVE FUNCTIONS #######################

def SaveLoad_get_typical_parameter_attributes_to_save( ):
	'''
	available parameter attributes:

	valid val expr enableExpr bindExpr bindRange name label startSection 
	displayOnly readOnly min max clampMin clampMax default defaultExpr 
	normMin normMax normVal enable order page password mode menuNames 
	menuLabels menuIndex menuSource styleCloneImmune 
	'''
	typicalParAttrs = [
		'name',
		'val',
		'enable',
	]
	return typicalParAttrs

def SaveLoad_get_uppercase_custom_parameter_pages( obj ):
	'''
	gets the upper case parameter pages. This is a convenience function
	for use with GeoPix specifically, since we leverage upper case custom pages.
	'''

	typicalPages = [ p.name for p in obj.customPages if p.name.isupper() ]
	return typicalPages


def SaveLoad_get_all_custom_parameter_pages( obj ):
	'''
	for testing, or more thorough saving, get all custom pages.
	'''
	return [ p.name for p in obj.customPages ]


def SaveLoad_Strip_Depend_From_Dict( d ):
	'''
	This function will iterate through a dictionary, stripping td depend dict
	structures away if they exist. We must do this because they do not serialize well.
	'''
	dictSansDepend = {}
	for k,v in d.items():
		isDependDict = "TDStoreTools.DependDict" in str(type(v))
		if isDependDict == True:
			v = v.getRaw()

		dictSansDepend[k] = v

	return dictSansDepend



def SaveLoad_get_clone_op_attribute( obj_data, targetOp ):
	'''
	gets the clone source and returns a dict.
	'''

	if hasattr( targetOp.par , 'clone' ):
		if targetOp.par.clone.eval() != None:
			obj_data['.par.clone'] = targetOp.par.clone.eval().path
		else:
			obj_data['.par.clone'] = None
	else:
		obj_data['.par.clone'] = None

	return obj_data



def SaveLoad_get_op_node_storage( obj_data, targetOp, subOperatorNames=[] ):
	'''
	gets the storage dictionary of the targetOp, and returns the dict.
	
	subOperators is an optional list of sub operators, that might have storage that needs saving.
	this is an edge case that unfortunately is developed into GeoPix quite deeply, so the edge case
	will be handled via the optional argument.
	'''

	# first attempt to retrieve just the top level storage, the case in most scenarios.
	obj_data['.storage'] = SaveLoad_Strip_Depend_From_Dict( targetOp.storage )

	for subOpName in subOperatorNames:
		subOp = targetOp.op(subOpName)
		if subOp != None:
			subOpStorage = SaveLoad_Strip_Depend_From_Dict(subOp.storage)
			obj_data['/%s.storage'%(subOpName)] = subOpStorage
	
	return obj_data



def SaveLoad_get_comp_hierearchy_inputs( obj_data, targetOp ):
	'''
	in the case of panel COMPs and geoCOMPs they can be parented to other comps,
	hierarchically, which is the vertical wires in TouchDesigner.

	since we can't connect two operators together by setting some attribute,
	we need to dive into edge case waters. we denote the special attributes with double
	underscores on both sides.
	'''

	if hasattr( targetOp , 'inputCOMPConnectors' ):

		COMPConnections = {}
		for COMPConnector in targetOp.inputCOMPConnectors:
			index = COMPConnector.index
			isInput = COMPConnector.isInput
			isOutput = COMPConnector.isOutput
			inOP = COMPConnector.inOP 
			outOP = COMPConnector.outOP 
			owner = COMPConnector.owner 
			connections = COMPConnector.connections 
			if len(connections) > 0:
				COMPConnections[index] = {'path':connections[0].owner.path, 'index':connections[0].index}

		obj_data['__hierarchyinputs__'] = COMPConnections
	
	return obj_data



def SaveLoad_get_comp_node_inputs( obj_data, targetOp ):
	'''
	in the case of inputs and outputs

	since we can't connect two operators together by setting some attribute,
	we need to dive into edge case waters. we denote the special attributes with double
	underscores on both sides.
	'''
	Connections = {}
	for Connector in targetOp.inputConnectors:
		index = Connector.index
		isInput = Connector.isInput
		isOutput = Connector.isOutput
		inOP = Connector.inOP 
		outOP = Connector.outOP 
		owner = Connector.owner 
		connections = Connector.connections 
		if len(connections) > 0:
			Connections[index] = {'path':connections[0].owner.path, 'index':connections[0].index}

	obj_data['__operatorinputs__'] = Connections
	
	return obj_data


def SaveLoad_get_general_op_data( obj_data, targetOp ):
	'''
	gets some basic backend td network attributes, and returns a dict.
	'''


	obj_data['.nodeX'] = targetOp.nodeX
	obj_data['.nodeY'] = targetOp.nodeY
	obj_data['.nodeWidth'] = targetOp.nodeWidth
	obj_data['.nodeHeight'] = targetOp.nodeHeight
	obj_data['.viewer'] = targetOp.viewer
	obj_data['.name'] = targetOp.name
	obj_data['.color'] = targetOp.color

	# the following attributes, not all nodes have.
	if hasattr(targetOp,'pickable'):
		obj_data['.pickable'] = targetOp.pickable

	if hasattr(targetOp,'activeViewer'):
		obj_data['.activeViewer'] = targetOp.activeViewer

	if hasattr(targetOp,'display'):
		obj_data['.display'] = targetOp.display

	if hasattr(targetOp,'render'):
		obj_data['.render'] = targetOp.render

	
	
	return obj_data


def SaveLoad_get_panel_data( obj_data, panel_value_names, targetOp ):
	'''
	gets some panel attributes if they exist, from the target OP. put them in the obj_data dict.
	'''

	assert type(panel_value_names) == list,'panel attribute names argument must be a list of strings...'

	# filter out blanks.
	panel_value_names = [ x for x in panel_value_names if x not in [''] ]

	# if there is at least one panel attribute name,
	if len(panel_value_names) > 0:

		# if target OP even has a panel member.
		if hasattr( targetOp , 'panel' ):

			# get a reference to the panel object.
			opPanelObject = getattr( targetOp , 'panel' )
			
			# loop through the panel attribute names provided.
			for panelAttrName in panel_value_names:
				# print("<%s>"%(panelAttrName))
				# if the panel object contains the attribute we're trying to save... proceed.
				if hasattr( opPanelObject , panelAttrName ):
					
					# handle panel state edge cases here IF needed.
					panelAttrVal = float( getattr( opPanelObject , panelAttrName ) )

					obj_data['.panel.%s'%(panelAttrName)] = panelAttrVal
				else:
					print( 'Panel attribute: %s.%s.%s could not be found or is invalid, skipping..'%( targetOp.path , 'panel' , panelAttrName ) )
	
	return obj_data


def SaveLoad_get_parameter_data( obj_data, targetOp, pageNames, parAttrs, ignoreDefault ):
	'''
	gets parameter data of the operator, and returns a dict.
	subAttrs must be a list of parameter attributes. you must have at least 1, ie .val
	name is always included as the dictionary key.
	
	pageNames is a list of parameter page name strings. 

	available parameter attributes:

	valid val expr enableExpr bindExpr bindRange name label startSection 
	displayOnly readOnly min max clampMin clampMax default defaultExpr 
	normMin normMax normVal enable order page password mode menuNames 
	menuLabels menuIndex menuSource styleCloneImmune 

	some read only parameters we might want to save:
	style 
	'''

	readOnlyAttrs = [
					'style',
					'isToggle',
					'isString',
					'isPython',
					'isOP',
					'isInt',
					'isFloat',
					'isNumber',
					'isMenu',
					'isMomentary',
					'isPulse',
					'isCustom',
					'isDefault',
					'owner',
					'sequence',
					'collapsable',
					'collapser',
					'prevMode',
					'tupletName',
					'tuplet',
					'help',
					'subLabel',
					'vecIndex',
					'index',
					'bindRange',
					'bindReferences',
					'bindMaster',
					'exportSource',
					'exportOP',
					'valid',
					]

	# make sure we were provided with lists.
	assert type(parAttrs)==list, 'variable <subattrs> must be of type list.'
	assert type(pageNames)==list, 'variable <pageNames> must be of type list.'

	# filter out name, if the user included it.
	parAttrs = [ parAttr for parAttr in parAttrs if parAttr not in ['name'] ]

	# combine default pages and custom pages into one list.
	allPages = targetOp.pages + targetOp.customPages

	# filter parameter pages down to only the pages contained in the argument pageNames.
	parameterPages = [ page for page in allPages if page.name in pageNames ]
	
	# double list comp to unravel that list of pages, into a list of all the associated parameters of those pages.
	allParameters = [ par for page in parameterPages for par in page.pars ]
	# print([ x.name for x in parameterPages ])

	# optional argument above, filters out params set to their defaults. this helps keep save files smaller.
	if ignoreDefault == True:
		allParameters = [ par for par in allParameters if par.val != par.default ]
	
	# iterate through all the saveable parameters.
	for par in allParameters:
		
		# iterate through our saveable parameter attribute names.
		for parAttribute in parAttrs:
			
			# if the attribute is a read only type, generate the .READONLY suffix, otherwise blank string.
			readOnlySuffix = '.READONLY' if parAttribute in readOnlyAttrs else ''
			
			# lets make sure the parameter actually has the attribute.
			if hasattr( par , parAttribute ):

				# generate the key and value.
				key = '.par.%s.%s%s'%( par.name , parAttribute , readOnlySuffix )
				
				# most parameters aren't using binding, we just fetch the value directly.
				if par.bindMaster == None:
					value = getattr( par , parAttribute )

				# if a parameter is bound, we don't care who the bind master is, 
				# we just want to retrieve that value instead.
				else:
					value = getattr( par.bindMaster , parAttribute )

				# assign to the master dict.
				obj_data[ key ] = value

				# EDGE CASE #1 - python params. they do not contain useful data at .val, but hold their stuff in .expr.
				if getattr( par , 'style' ) == 'Python':
					
					# if user wanted to save vals, lets assume they want the Python param equivalent, .expr.
					# if 'val' in parAttrs and 'expr' not in parAttrs:
					if 'expr' not in parAttrs:
						
						# generate key and value.
						key = '.par.%s.%s'%( par.name , 'expr' )
						# value = getattr( par , parAttribute )
						value = getattr( par , 'expr' )

						# print(key,value,parAttribute)

						# assign to the master dict.
						obj_data[ key ] = value
					
					# if user wanted to save vals, lets assume they want the Python param equivalent, .expr.
					# if 'val' in parAttrs and 'expr' not in parAttrs:
					if 'mode' not in parAttrs:
						
						# generate key and value.
						key = '.par.%s.%s'%( par.name , 'mode' )
						# value = getattr( par , parAttribute )
						value = getattr( par , 'mode' )

						# print(key,value,parAttribute)

						# assign to the master dict.
						obj_data[ key ] = str(value)

				# EDGE CASE #2 - parameter modes are not strings, but objects. we need to stringify them to keep json happy 
				elif parAttribute == 'mode':
					
					value = str(value)

					# assign to the master dict.
					obj_data[ key ] = value
			
			# if the par attr doesn't exist, warn the user. this really shouldn't happen.
			else:
				debug(par, 'does not contain attribute by the name of <%s>'%(parAttribute))
	
	
	return obj_data


################### LOAD FUNCTIONS #######################

def SaveLoad_record_translation_link( translationDict , intendedPath , actualPath ):
	'''
	when importing saves, we might be trying to set an operator to a td name that already exists..
	so to mitigate this, functions down stream of the one that creates the operators need a way
	to lookup the new name, based on the intended old name. the translation table solves this problem for us.
	but we must update it along the way. this is just a wrapper function for a simple operation in case
	it needs to be come more complex later.
	'''
	translationDict[intendedPath] = actualPath
	# print('logged:', intendedPath,'=',actualPath)

	return translationDict

def SaveLoad_lookup_translated_op( translationDict , intendedPath ):
	'''
	the importing function needs to find out the name of the actual created object after td silently renames it to avoid conflicts.
	this is a simple operation of a dictionary lookup and converting to an operator, but we do it in
	this wrapper function anyways incase we need to expand on it later.
	'''

	if intendedPath in translationDict.keys():
		return op(translationDict[intendedPath])
	else:
		# print('Could not find a translation entry for <%s>, using original Op.'%(intendedPath))
		return op(intendedPath)



def SaveLoad_init_operator_from_save_data( targetOp , savedData , translationDict ):
	'''
	wrapper function for initializing operators with the typical workflow. set attributes, then record translation.
	'''
	for k,v in savedData.items():

		full_attribute_path = targetOp.path + k
		
		### CASE #1 - starts with a period, means it's an attribute, or par.attribute of the top level operator.
		if k.startswith('.'):
			
			newlySetOrCreatedOp = SaveLoad_set_typical_operator_attributes( full_attribute_path , v )
			# translationDict = SaveLoad_record_translation_link( translationDict , targetOp.path , newlySetOrCreatedOp.path )

		
		### CASE #2 - starts with a forward slash (/), means it's a sub operator's attributes or par.attributes.
		elif k.startswith('/'):

			newlySetOrCreatedOp = SaveLoad_set_typical_operator_attributes( full_attribute_path , v )
			originPathForTranslation = full_attribute_path.split('.')[0]
			# translationDict = SaveLoad_record_translation_link( translationDict , originPathForTranslation , newlySetOrCreatedOp.path )
			pass

		else:
			pass

	# lastly handle secondary stuff.
	SaveLoad_set_secondary_operators( targetOp , savedData , translationDict )

	return translationDict


def SaveLoad_uniquify_names_on_operators( translationDict ):
	'''
	this function is used when the user performs an import function. most things they save and load are not user created objects,
	thus the name param if it even exists should not change from it's original, however there are 3 main edge cases..
	Editor objects, IO objects, and Perform objects which the user can create any number and any variety.
	'''
	for k,v in translationDict.items():
		possiblyTranslatedObject = op(v)
		if possiblyTranslatedObject != None:
			if 'NameMustBeUnique' in possiblyTranslatedObject.tags:
				print(k,v)



	return




def SaveLoad_set_secondary_operators( rootOp , savedData , translationDict ):
	'''
	loads the secondary data 
	'''

	# nuke everything in the container we are trying to replicate. normally we woulnd't do this
	# and handle naming conflicts on import, but the secondary level we don't have import as a feature.
	translatedRootOp = SaveLoad_lookup_translated_op( translationDict , rootOp.path )
	if '__secondarylayer__' in savedData.keys():
		if len(savedData['__secondarylayer__'].keys()):
			firstOne = list(savedData['__secondarylayer__'].keys())[0]
			# print('-------------', '/'.join( firstOne.split('/')[0:-1] ))
			tmpRoot = op( '/'.join( firstOne.split('/')[0:-1] ) )
			f = tmpRoot.findChildren(type=geometryCOMP, depth=1)
			for each in f:
				each.destroy()
	
	# iterate through the SECONDARY objects we are trying to load.
	# this is built in as if it is a general tool, but who are we lying to..
	# this was built in specifically for loading Macro networks.
	# for k,v in savedData['__secondarylayer__'].items():
	for targetOpPath,targetOpSaveData in savedData['__secondarylayer__'].items():
		

		# do a lookup on the rootOp path, so that it reflects any name conflict changes we might have had.
		targetOpPath = targetOpPath.replace( rootOp.path , translatedRootOp.path )
		
		# generate path to parent of root, in context of IO, this is the GRAPH comp.
		rootOp2Path = '/'.join( targetOpPath.split('/')[0:-1] )
		rootOp2 = op(rootOp2Path)

		# get a reference to the clone template.
		cloneTemplate = op(targetOpSaveData['.par.clone'])

		# check if not none, should be fine.
		if cloneTemplate != None:

			# newly copied template.
			targetOp = rootOp2.copy( cloneTemplate )

			# iterate through all the attributes of the operator.
			for attrPath,attrVal in targetOpSaveData.items():

				### CASE #1 - starts with a period, means it's an attribute, or par.attribute of the top level operator.
				if attrPath.startswith('.'):
					
					# targetOp = k.replace( rootOp.path , translatedRootOp.path )
					full_attribute_path = targetOp.path + attrPath
					value_ = attrVal

					# print( 'full_attribute_path',full_attribute_path )

					# if attrPath == '.name':
					# 	value_ = targetOp.name
					# 	if 'Fixture' in targetOp.name:
					# 		print(targetOp)
					
					newlySetOrCreatedOp = SaveLoad_set_typical_operator_attributes( full_attribute_path , value_ )
					translationDict = SaveLoad_record_translation_link( translationDict , targetOpPath , newlySetOrCreatedOp.path )

				# if starts with a path, means it's a sub comp... but leaving this blank for now since
				# we know there will be nothing in our network qualifying this.
				elif attrPath.startswith( '/' ):
					pass

		else:
			debug('cloneTemplate was None, this should not happen.')

	# iterate through the objects we are trying to load secondarily.
	for k,v in savedData['__secondarylayer__'].items():
		didSucceed = SaveLoad_set_input_operators( k , savedData['__secondarylayer__'] , translationDict )




def SaveLoad_set_typical_operator_attributes( full_attribute_path , value_ ):
	'''
	When we set attributes, we might be doing it on the targetOp, a child of the targetOp, 
	or even parameters or attributes of the target or child OP. So for that, we have this
	function that handles the edge case and typical cases in a neat and consistent way.
	we only need to pass in the 4 arguments.
	'''
	
	assert full_attribute_path.count('.') >= 1,'full_attribute_path must contain at least 1 dot separator...\n%s'%(full_attribute_path)
	
	targetOp = op( full_attribute_path.split('.')[0] )
	assert targetOp!=None,'beginning of full_attribute_path should eval to a valid operator...\n%s'%(full_attribute_path)


	# logical block handles the splitting up of the full_attribute_path into separate strings, to use in hasattr and getattr etc.
	if full_attribute_path.count('.') == 1:
		full_attribute_path_split = full_attribute_path.split('.')
		operator_ = full_attribute_path_split[0]
		object_ = ''
		attr_ = full_attribute_path_split[1]
	else:
		indexOfFirstDot = full_attribute_path.find('.')
		indexOfLastDot = full_attribute_path.rfind('.')
		operator_ = full_attribute_path[0:indexOfFirstDot]
		object_ = '.'+full_attribute_path[indexOfFirstDot+1:indexOfLastDot]
		attr_ = full_attribute_path[indexOfLastDot+1::]

	objectEval_ = "op('%s')%s"%( operator_ , object_ )

	### CASE #1 - colors. we get a list when saving, but need to set as a tuple.
	if attr_ == 'color':
		setattr( eval(objectEval_) , attr_ , tuple(value_) )
	
	### CASE #2 - stoage. we can't edit storage by overwriting it, we have to assign things to it.
	elif attr_ == 'storage':
		storageObject = getattr( eval(objectEval_) , attr_ )
		for k,v in value_.items():
			storageObject[k] = v

		# CASE #1 - this operator might be a hull or pix sub component. if so, proceed. 
		if hasattr( targetOp , 'WriteCoordsToTable' ):
			
			# json always requires keys be strings, so when we save our data out it gets stringified. must convert back.
			for k,v in targetOp.storage.items():
				if k in ['HullStored','PixStored']:
					targetOp.storage[k]['coordList'] = { int(k2):v2 for k2,v2 in targetOp.storage[k]['coordList'].items() }
			
			# call the WriteCoordsToTable function to push the storage data out to TouchDesigner nodes.
			targetOp.WriteCoordsToTable()

		# CASE #2 - this operator might be a pixframe sub component. if so, proceed.
		elif hasattr( targetOp , 'Write' ):
			targetOp.Write()

	### CASE #3 - if we're setting the name param,we want to make sure it's unique.
	elif attr_ == 'name':

		# edge 1 = editor object
		# if targetOp.path.startswith( op.geoHolder.path ):
		if targetOp.parent() == op.geoHolder:
			existingNames = [ x.name for x in op.geoHolder.children if x != targetOp ]
			value_ = mod.globalFuncs.uniquifyString( value_ , existingNames )
			setattr( targetOp , attr_ , value_ )

		# edge 2 = io object (top level only, so macros.)
		if targetOp.parent() == op.IO_scene:
			existingNames = [ x.name for x in op.IO_scene.children if x != targetOp ]
			value_ = mod.globalFuncs.uniquifyString( value_ , existingNames )
			setattr( targetOp , attr_ , value_ )

		# edge 3 = perform objects.
		# elif targetOp.path.startswith( op.PerformV2.path ):
		elif targetOp.parent().name not in tdu.expand('Canvas[0-99]'):
			existingNames = [ x.name for x in targetOp.parent().children if x != targetOp ]
			value_ = mod.globalFuncs.uniquifyString( value_ , existingNames )
			setattr( targetOp , attr_ , value_ )


	### GENERAL attribute case. Most things can be set simply this way.
	else:
		try:
			# CASE #1 - might be setting a parameter's mode...
			if attr_ == 'mode':
				
				# but it might also be a non custom parameter named mode.. so lets check if this is a param attr or not.
				if '.par.' in objectEval_:
					setattr( eval(objectEval_) , attr_ , eval(value_) )
			
			# CASE #2 - might be setting a parameter's expr...
			elif attr_ == 'expr':
				
				# but it might also be a non custom parameter named mode.. so lets check if this is a param attr or not.
				if '.par.' in objectEval_:
					if value_ != None:
						setattr( eval(objectEval_) , attr_ , value_ )
					else:
						setattr( eval(objectEval_) , attr_ , '' )
			
			# CASE #3 - might be setting a parameter's val -this is common...
			elif attr_ == 'val':
				
				# but it might also be a non custom parameter named mode.. so lets check if this is a param attr or not.
				if '.par.' in objectEval_:
					# print('=========',objectEval_)
					if getattr( eval(objectEval_) , 'mode' ) not in [ ParMode.EXPRESSION ]:
						
						# if it's a Name parameter, do some uniquifying first, so we can ensure the name is unique among it's siblings.
						if objectEval_.endswith( '.par.Name' ):
							targetOp = eval(objectEval_.split('.')[0])
							
							# edge 1 = editor object
							if targetOp.parent() == op.geoHolder:
								existingNames = [ x.par.Name.eval() for x in op.geoHolder.children if x != targetOp and x.OPType == 'geometryCOMP' ]
								# print('existing EDITOR names',existingNames)
								value_ = mod.globalFuncs.uniquifyString( value_ , existingNames )

							# edge 2 = io object (top level only, so macros.)
							if targetOp.parent() == op.IO_scene:
								# print(targetOp,'is in IO')
								existingNames = [ x.par.Name.eval() for x in op.IO_scene.children if x != targetOp and x.OPType == 'geometryCOMP' ]
								# print('existing IO names',existingNames)
								value_ = mod.globalFuncs.uniquifyString( value_ , existingNames )

							# edge 3 = perform objects.
							elif targetOp.parent().name in tdu.expand('Canvas[0-99]'):
								# print(targetOp,'is in PERFORM')
								existingNames = [ x.par.Name.eval() for x in targetOp.parent().children if x != targetOp and x.OPType == 'containerCOMP' ]
								# print('existing PERFORM names',existingNames)
								value_ = mod.globalFuncs.uniquifyString( value_ , existingNames )
							# print('---')

						setattr( eval(objectEval_) , attr_ , value_ )

			
			# CASE #4 - might be a panel state - ie a button COMP.
			# elif objectEval_.endswith('.panel'):
				'''
				# if it's a button COMP type situation where we want to set the panel.state attribute.
				if attr_ == 'state':
					# NOTE: thought we needed an edge case handler for this situation but turns out we didn't.
					# leaving this here anyways incase we need it later.
					setattr( eval(objectEval_) , attr_ , value_ )
					# eval(objectEval_.split('.')[0]).click( bool(value_) ) # click it
				'''
				# pass
			
			# GENERAL CASE:
			else:
				# print(objectEval_,attr_,value_)
				setattr( eval(objectEval_) , attr_ , value_ )
		except tdError as E:
			if not str(E).startswith( 'Custom parameter expected. ' ):
				print( 'Could not set attribute <%s.%s> due to unexpected tdError:'%(attr_,value_), E )
		except AttributeError as E:
			if not str(E).startswith( "'td.ParCollection' object has no attribute" ):
				print( 'Could not set attribute <%s.%s> due to unexpected AttributeError:'%(attr_,value_), E )


	return targetOp



def SaveLoad_set_parent( targetOp , parentConnections , translationDict ):
	'''
	Manages connecting target OP to parentOPs. a target can only ever have one parent,
	but since we want consistency between this function and the inputs function we treat it
	as if an object might have more than one parent.
	'''
	targetOp = SaveLoad_lookup_translated_op( translationDict , targetOp )


	for conIndex,conDict in parentConnections.items():
		
		index = conDict['index']
		path = conDict['path']

		parentOP = SaveLoad_lookup_translated_op( translationDict , path )

		if parentOP != None:

			targetOp.inputCOMPConnectors[int(conIndex)].connect( parentOP )


	return


def SaveLoad_set_input( targetOp , inputConnections , translationDict ):
	'''
	Manages connecting target inputs to targetOP.
	'''
	
	targetOp2 = SaveLoad_lookup_translated_op( translationDict , targetOp )
	

	for conIndex,conDict in inputConnections.items():
		
		index = conDict['index']
		path = conDict['path']

		sourceOP = SaveLoad_lookup_translated_op( translationDict , path )

		if sourceOP != None:
			targetOp2.inputConnectors[int(conIndex)].connect( sourceOP.outputConnectors[int(index)] )


	return




def SaveLoad_create_or_set_operators( rootPath , loadDict , isImport=False ):
	'''
	wrapper function that takes care of the branching between setting/creating objects.
	'''

	# init this, we will need to fill it out as we load things.
	translationDict = {}

	# iterate through the PRIMARY objects we are trying to load.
	for savedOp,savedData in loadDict.items():


		# get some operator references.
		rootOp = op(rootPath)
		targetOp = op(savedOp)
		cloneTemplateOp = op(savedData['.par.clone'])
		# if this function is being run as an import action, we can trick the function into creating a new object
		# even if one by it's name already exists, thus never overwriting what's already there.
		if isImport == True:
			targetOp = None

		# print( '+++', rootOp , targetOp , cloneTemplateOp )

		### CASE 1 - assume the operator exists, and we just want to set some things.
		# this will be the case for things like global settings, or tools, etc.
		# will not be the case for objects the user creates or deletes themselves.
		if targetOp != None:

			# do the standard initialization of an operator.
			# translationDict = SaveLoad_init_operator_from_save_data( targetOp , savedData , translationDict )
			SaveLoad_init_operator_from_save_data( targetOp , savedData , translationDict )

			translationDict = SaveLoad_record_translation_link( translationDict , savedOp , targetOp.path )

		### CASE 2 - operator does not exist, next assume a clone template of it exists.
		# this scenario will apply to objects users create/delete.
		elif cloneTemplateOp != None:

			# newly copied template.
			targetOp = rootOp.copy( cloneTemplateOp )

			# do the standard initialization of an operator.
			# translationDict = SaveLoad_init_operator_from_save_data( targetOp , savedData , translationDict )
			SaveLoad_init_operator_from_save_data( targetOp , savedData , translationDict )

			translationDict = SaveLoad_record_translation_link( translationDict , savedOp , targetOp.path )


		if hasattr( targetOp , 'SET_WINDOW' ):
			targetOp.SET_WINDOW()


		# CASE 3 - operator does not exist, nor does a clone template exist.
		# placeholder logic branch, but in GeoPix we should not have anything
		# that fits this criteria.
		else:
			# debug('creating from scratch...')
			debug('No valid Target or Clone, Skipping! (this is probably fine)')


	return translationDict




def SaveLoad_set_parent_operators( rootPath , loadDict , translationDict ):
	'''
	wrapper function that takes care of parenting objects to their parents.
	'''

	# iterate through the objects we are trying to load.
	for targetOp,savedData in loadDict.items():

		# get some operator references.
		rootOp = op(rootPath)
		
		for k,v in savedData.items():

			### CASE #1 - __hierarchyinputs__ means we need to parent the targetOp to a parentOP if one is specified
			if k == '__hierarchyinputs__':

				# dict comp to convert keys to ints.. thanks json.
				parentConnections = { int(k2):v2 for k2,v2 in v.items() }

				didSucceed = SaveLoad_set_parent( targetOp , parentConnections , translationDict )

			else:
				pass


	return




def SaveLoad_set_input_operators( rootPath , loadDict , translationDict ):
	'''
	wrapper function that takes care of connecting inputs and outputs of operators.
	'''
	# iterate through the objects we are trying to load.
	for targetOp,savedData in loadDict.items():

		# print(targetOp, savedData)
		# get some operator references.
		rootOp = op(rootPath)

		for k,v in savedData.items():



			### CASE #1 - __operatorinputs__ means we need to connect the sourceOP to the targetOp OP if one is specified
			if k == '__operatorinputs__':

				# dict comp to convert keys to ints.. thanks json.
				inputConnections = { int(k2):v2 for k2,v2 in v.items() }

				didSucceed = SaveLoad_set_input( targetOp , inputConnections , translationDict )

			else:
				pass


	return