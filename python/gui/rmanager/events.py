
import Event

__all__ = ('g_eventsManager', )

class EventsManager(object):

	def __init__(self):

		self.onAppFinish = Event.Event()
		self.onLoginViewLoaded = Event.Event()

		self.onUpdatingDatabaseStart = Event.Event()
		self.onUpdatingDatabaseStop = Event.Event()
		self.onParsingReplay = Event.Event()

		self.onNeedToUpdateReplaysList = Event.Event()

		self.onUploaderStatus = Event.Event()
		self.onUploaderProgress = Event.Event()
		self.onUploaderResult = Event.Event()

g_eventsManager = EventsManager()
