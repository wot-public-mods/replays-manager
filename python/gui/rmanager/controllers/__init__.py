from gui.rmanager.events import g_eventsManager

__all__ = ('g_controllers', )

class ControllersHolder():

	def __init__(self):
		self.actions = None
		self.database = None
		self.parser = None
		self.uploader = None

	def init(self):

		from gui.rmanager.controllers.actions import ActionsController
		from gui.rmanager.controllers.database import DataBaseController
		from gui.rmanager.controllers.parser import ParserController
		from gui.rmanager.controllers.uploader import UploaderController

		self.actions = ActionsController()
		self.database = DataBaseController()
		self.parser = ParserController()
		self.uploader = UploaderController()

		self.actions.init()
		self.database.init()
		self.parser.init()
		self.uploader.init()

		g_eventsManager.onAppFinish += self.fini

	def fini(self):

		self.actions.fini()
		self.database.fini()
		self.parser.fini()
		self.uploader.fini()

		self.actions = None
		self.database = None
		self.parser = None
		self.uploader = None

g_controllers = ControllersHolder()
