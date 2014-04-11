from lib import server

class ParentController(server.BaseController):
	pass

class Controller(server.Controller, ParentController):
	pass

class ModelController(server.ModelController, ParentController):
	pass

class AJAXController(server.AJAXController, ParentController):
	pass
