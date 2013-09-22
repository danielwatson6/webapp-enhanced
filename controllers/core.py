from lib import server

class ParentController(server.BaseController):
	
	#
	# This is the parent controller.
	#
	# To keep code DRY, everything common
	# to the rest of the controllers
	# should be defined in this class.
	#
	
	pass


class Controller(server.Controller, ParentController):
	
	# This is the base controller for simple controllers.
	pass

class ModelController(server.ModelController, ParentController):
	
	# This is the base controller for model-supporting controllers.
	pass

class BlobController(server.BlobController, ParentController):
	
	# This is the base controller for blob-supporting default controllers.
	pass

class UploadController(server.UploadController, ParentController):
	
	# This is the base controller for blob-supporting upload controllers.
	pass

class DownloadController(server.DownloadController, ParentController):
	
	# This is the base controller for blob-supporting controllers.
	pass

class CustomController(server.CustomController, ParentController):
	
	# This is the base controller for low-level controllers.
	pass
