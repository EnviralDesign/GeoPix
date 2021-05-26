"""
SAVE LOAD is an extension for making a component or it's sub components saveable.
"""

import SaveLoadGlobal

class SaveLoad:
	"""
	SaveLoad description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp


	def SaveLoad_GET( self , 
			root_op , 
			include_self , 
			find_children_expression , 
			sub_operators , 
			extra_page_names , 
			extra_parameter_attributes , 
			ignore_defaults , 
			find_children_expression_secondary ,
			panel_values ):
		'''
		returns a dictionary of save data from the saveable items/parameters.
		effectively this is the SAVE function.
		root_op = is the root operator this function and all sub functions uses as an origin for this iteration of saving.
		include_self = if True, will save parameters and attributes etc of the root, and not just the children.
		find_children_expression = this should be a findChildren() funcion, that evaluates properly relative to the root_op. the returned children, are saved. ie children of geoHOLDER.
		sub_operators = this should be a comma separated list of sub components to manually save data about, as well. ie. pix, hull, etc.
		extra_page_names = specify the other page names of params you wish to save, other than the default uppercase ones.
		find_children_expression_secondary = this is the search expression that searches relative to the children found from find_children_expression, ie. for Macro's
		'''

		root_op = op( root_op )
		include_self = eval( include_self )
		ignore_defaults = eval( ignore_defaults )

		try:
			root_objects = eval( find_children_expression ) if find_children_expression != '' else []
		except:
			root_objects = []
			debug('could not eval the expression:', find_children_expression)
		sub_operators = sub_operators.split(',')
		extra_page_names = [ each for each in extra_page_names.split(',') if each != '' ]
		extra_parameter_attributes = [ each for each in extra_parameter_attributes.split(',') if each != '' ]

		panel_value_names = panel_values.split(',')	


		save_data = {}

		# if we have include_self flag True, we want to include the top level operator.
		if include_self == True:
			root_objects.append( root_op )

		
		for obj in root_objects:
			obj_data = {}

			#### save operator level attributes.
			obj_data = SaveLoadGlobal.SaveLoad_get_clone_op_attribute( obj_data, obj )
			obj_data = SaveLoadGlobal.SaveLoad_get_general_op_data( obj_data, obj )
			obj_data = SaveLoadGlobal.SaveLoad_get_panel_data( obj_data, panel_value_names, obj )

			#### save operator and sub operator level node storage.
			obj_data = SaveLoadGlobal.SaveLoad_get_op_node_storage( obj_data, obj, sub_operators )

			#### save operator hierarchy parent.
			obj_data = SaveLoadGlobal.SaveLoad_get_comp_hierearchy_inputs( obj_data, obj )
			obj_data = SaveLoadGlobal.SaveLoad_get_comp_node_inputs( obj_data, obj )

			#### save custom parameters 
			pageNames = SaveLoadGlobal.SaveLoad_get_uppercase_custom_parameter_pages( obj )
			pageNames += extra_page_names # add some others we have in scene objects.
			pageNames = list(set(pageNames))

			parAttrs = SaveLoadGlobal.SaveLoad_get_typical_parameter_attributes_to_save()
			parAttrs += extra_parameter_attributes
			parAttrs = list(set(parAttrs))

			# ignoreDefault = False # setting to true, will not save params already set to default value.
			obj_data = SaveLoadGlobal.SaveLoad_get_parameter_data( 	obj_data, obj, pageNames, parAttrs, ignore_defaults )

			# store the primary save data.
			save_data[obj.path] = obj_data

			
		# return
		for root_object in root_objects:
			try:
				secondaryEvalExpr = "op('%s')%s"%( root_object.path,find_children_expression_secondary)

				secondaryResults = eval(secondaryEvalExpr) if find_children_expression_secondary != '' else []
			except:
				debug('could not eval the expression:', find_children_expression_secondary)
				secondaryResults = []

			all_secondary_obj_data = {}

			for each in secondaryResults:
				secondary_obj_data = {}

				# print(each)

				#### save operator level attributes.
				secondary_obj_data = SaveLoadGlobal.SaveLoad_get_clone_op_attribute( secondary_obj_data, each )
				secondary_obj_data = SaveLoadGlobal.SaveLoad_get_general_op_data( secondary_obj_data, each )
				secondary_obj_data = SaveLoadGlobal.SaveLoad_get_panel_data( secondary_obj_data, panel_value_names, each )

				#### save operator and sub operator level node storage.
				secondary_obj_data = SaveLoadGlobal.SaveLoad_get_op_node_storage( secondary_obj_data, each, sub_operators )

				#### save operator hierarchy parent.
				secondary_obj_data = SaveLoadGlobal.SaveLoad_get_comp_hierearchy_inputs( secondary_obj_data, each )
				secondary_obj_data = SaveLoadGlobal.SaveLoad_get_comp_node_inputs( secondary_obj_data, each )

				#### save custom parameters 
				pageNames = SaveLoadGlobal.SaveLoad_get_uppercase_custom_parameter_pages( each )
				pageNames += extra_page_names # add some others we have in scene objects.

				parAttrs = SaveLoadGlobal.SaveLoad_get_typical_parameter_attributes_to_save()
				ignoreDefault = False
				secondary_obj_data = SaveLoadGlobal.SaveLoad_get_parameter_data( secondary_obj_data, each, pageNames, parAttrs, ignoreDefault )

				all_secondary_obj_data[each.path] = secondary_obj_data

			# print('---',root_object)
			save_data[root_object]['__secondarylayer__'] = all_secondary_obj_data




		return save_data



	def SaveLoad_SET(self, loadDict, exact_match, isImport, foundChildren ):
		'''
		attempts to recreate or set the operators up.. 
		effectively this is the LOAD function.
		'''

		# print( list(loadDict.keys()) )
		
		# get the root path. we'll use this to filter out save data from other parts of the network.
		rootPath = self.ownerComp.path
		
		if exact_match == False:
			# filter out save data from other parts of the network.
			loadDict = { k:v for k,v in loadDict.items() if k.startswith(rootPath) }

		elif exact_match == True:
			# filter out save data from other parts of the network, stricter
			loadDict = { k:v for k,v in loadDict.items() if k == rootPath }

		elif exact_match == 'expr':
			# this filter option is kind of an edge case. in the instance where find_children_expression is set to return operators
			# that are not in the same path structure as 'rootPath' the above two if and elif's fail because of that.
			# we instead use this third case "expr" to say that we know those operators exist, and just check the paths against
			# the paths that the expression returns, which of course should match the same.
			foundChildrenPaths = [ x.path for x in foundChildren ]
			loadDict = { k:v for k,v in loadDict.items() if k in foundChildrenPaths }

		# print( list(loadDict.keys()) )

		# create or set the initial operaetors up, returning a translation dict for any name conflicts.
		translationDict = SaveLoadGlobal.SaveLoad_create_or_set_operators( rootPath , loadDict , isImport=isImport )

		# if isImport == True:
		# 	SaveLoadGlobal.SaveLoad_uniquify_names_on_operators( translationDict )

		# parent objects to their intended parents.
		SaveLoadGlobal.SaveLoad_set_parent_operators( rootPath , loadDict , translationDict )

		# wire operators to their inputs.
		SaveLoadGlobal.SaveLoad_set_input_operators( rootPath , loadDict , translationDict )

		return