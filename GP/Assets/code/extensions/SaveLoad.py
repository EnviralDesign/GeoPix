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


	def SaveLoad_GET( self , root_op , include_self , find_children_expression , sub_operators , extra_page_names ):
		'''
		returns a dictionary of save data from the saveable items/parameters.
		effectively this is the SAVE function.
		'''

		root_op = op( root_op )
		include_self = eval( include_self )
		try:
			root_objects = eval( find_children_expression )
		except:
			root_objects = []
		sub_operators = sub_operators.split(',')

		save_data = {}

		# if we have include_self flag True, we want to include the top level operator.
		if include_self == True:
			root_objects.append( root_op )

		# root_objects = self.ownerComp.findChildren( type=geometryCOMP, depth=1 )
		for obj in root_objects:
			obj_data = {}

			#### save operator level attributes.
			obj_data = SaveLoadGlobal.SaveLoad_get_clone_op_attribute( obj_data, obj )
			obj_data = SaveLoadGlobal.SaveLoad_get_general_op_data( obj_data, obj )

			#### save operator and sub operator level node storage.
			obj_data = SaveLoadGlobal.SaveLoad_get_op_node_storage( obj_data, obj, sub_operators )

			#### save operator hierarchy parent.
			obj_data = SaveLoadGlobal.SaveLoad_get_comp_hierearchy_inputs( obj_data, obj )
			obj_data = SaveLoadGlobal.SaveLoad_get_comp_node_inputs( obj_data, obj )

			#### save custom parameters 
			pageNames = SaveLoadGlobal.SaveLoad_get_uppercase_custom_parameter_pages( obj )
			pageNames += ['Custom','Special','hidden'] # add some others we have in scene objects.
			parAttrs = SaveLoadGlobal.SaveLoad_get_typical_parameter_attributes_to_save()
			ignoreDefault = False
			obj_data = SaveLoadGlobal.SaveLoad_get_parameter_data( 	obj_data, obj, pageNames, parAttrs, ignoreDefault )


			save_data[obj.path] = obj_data


		return save_data



	def SaveLoad_SET(self, loadDict):
		'''
		attempts to recreate or set the operators up.. 
		effectively this is the LOAD function.
		'''
		
		# get the root path. we'll use this to filter out save data from other parts of the network.
		rootPath = self.ownerComp.path
		
		# filter out save data from other parts of the network.
		loadDict = { k:v for k,v in loadDict.items() if k.startswith(rootPath) }

		# create or set the initial operaetors up, returning a translation dict for any name conflicts.
		translationDict = SaveLoadGlobal.SaveLoad_create_or_set_operators( rootPath , loadDict )

		# parent objects to their intended parents.
		SaveLoadGlobal.SaveLoad_set_parent_operators( rootPath , loadDict , translationDict )


		return