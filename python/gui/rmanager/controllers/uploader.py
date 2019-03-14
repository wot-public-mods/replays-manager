
import os
import threading
import BigWorld
import time
import math
import json
import urllib
import urllib2
from helpers import isPlayerAccount
from account_helpers import getAccountDatabaseID
from adisp import async, process
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from constants import CURRENT_REALM
from gui.rmanager.controllers import g_controllers
from gui.rmanager.events import g_eventsManager
from gui.rmanager.rmanager_constants import WAITING_DELAY, WOTREPLAYS_API_URL, REPLAYS_PATH, \
											UPLOADER_STATUS, UPLOAD_REPLAY_TEMP
from gui.rmanager.utils import MultiPartForm, requestProgress

__all__ = ('UploaderController', )

class UploaderController(object):
	
	status = property(lambda self: self.__status)

	def init(self):
		self.clean()
	
	def fini(self):
		self.clean()
	
	def clean(self):
		self.__replayName = None
		self.__replayDescription = None
		self.__replayFileName = None
		self.__replayUserDBID = None
		self.__replayUserName = None
		self.__replaySecret = False
		self.__status = None
		self.__sended = 0.0
	
	@async
	@process
	def apiStatus(self, callback):
		status = yield lambda callback: self.__parseApiStatus(callback)
		
		LOG_DEBUG('UploaderController.apiStatus %s' % status)
		
		callback(status)
	
	def prepare(self, replayFileName, replayUserDBID, replayUserName):
		
		LOG_DEBUG('UploaderController.prepare', replayFileName, replayUserDBID, replayUserName)
		
		if not isPlayerAccount():
			self.__setStatus(UPLOADER_STATUS.NOT_ACCOUNT)
			return False
		
		LOG_DEBUG('UploaderController.prepare', getAccountDatabaseID(), replayUserDBID)
		
		if getAccountDatabaseID() != long(replayUserDBID):
			self.__setStatus(UPLOADER_STATUS.WRONG_ACCOUNT)
			return False
		
		if not os.path.exists(REPLAYS_PATH + replayFileName):
			self.__setStatus(UPLOADER_STATUS.REPLAY_NOT_FOUND)
			return False
		
		self.__replayFileName = replayFileName
		self.__replayUserDBID = replayUserDBID
		self.__replayUserName = replayUserName
		
		self.__setStatus(UPLOADER_STATUS.REPLAY_FOUND)

		return True
	
	def upload(self, replayName, replayDescription, isSecret):
		
		if self.__status in UPLOADER_STATUS.ERRORS:
			return
		
		self.__replayName = replayName
		self.__replayDescription = replayDescription
		self.__replaySecret = isSecret
		
		self._uploadThread = threading.Thread(target=self.__uploaderThread)
		self._uploadThread.daemon = True
		BigWorld.callback(WAITING_DELAY, self._uploadThread.start)
	
	def __parseApiStatus(self, callback):
		try:
			targetDomen = 'ru' if CURRENT_REALM == 'CURRENT_REALM' else 'eu'
			status = urllib.urlopen('http://wotreplays.%s' % targetDomen).getcode() == 200
		except:
			status = False
		callback(status)
	
	def __uploaderThread(self):
		
		fileStream = open(REPLAYS_PATH + self.__replayFileName, 'rb')
		
		form = MultiPartForm()
		
		if self.__replayName:
			form.add_field('Replay[title]', str(self.__replayName))
		
		if self.__replayDescription:
			form.add_field('Replay[description]', str(self.__replayDescription))
		
		form.add_field('Replay[isSecret]', str(int(self.__replaySecret)))

		form.add_file('Replay[file_name]', self.__replayFileName, fileStream)
		
		targetDomen = 'ru' if CURRENT_REALM == 'CURRENT_REALM' else 'eu'
		targetURL = WOTREPLAYS_API_URL % (targetDomen, str(self.__replayUserDBID), str(self.__replayUserName))

		LOG_DEBUG('UploaderController.__uploaderThread endpoint', targetURL)

		request = urllib2.Request(targetURL)
		body = str(form)
		request.add_header('Content-type', form.getContentType())
		request.add_header('Content-length', len(body))
		
		with open(UPLOAD_REPLAY_TEMP, 'wb') as f:
			f.write(body)
		
		requestWithProgress = requestProgress(UPLOAD_REPLAY_TEMP, 'rb', self.__setProgress, 'data')
		request.add_data(requestWithProgress)
			
		try:
			self.__setStatus(UPLOADER_STATUS.LOADING)
			r = urllib2.urlopen(request)
		except:
			LOG_ERROR('UploaderController.__uploaderThread')
			LOG_CURRENT_EXCEPTION()
			self.__setStatus(UPLOADER_STATUS.CONNECTION_ERROR)
		else:
			self.__setResponce(r.read())
		
		requestWithProgress.close()
		os.remove(UPLOAD_REPLAY_TEMP)
	
	def __setResponce(self, responce):
		LOG_DEBUG("UploaderController.__setResponce responce: %s" % str(responce))
		if responce:
			self.__setStatus(UPLOADER_STATUS.LOADING_COMPLETE)
			g_eventsManager.onUploaderResult(responce)
	
	def __setProgress(self, total, size):
		self.__sended += size
		percent = math.trunc(self.__sended / total * 100.0)
		g_eventsManager.onUploaderProgress(total, self.__sended, percent)
	
	def __setStatus(self, status):
		LOG_DEBUG('UploaderController.__setStatus => status:%s' % status)
		if status != self.__status:
			self.__status = status
			g_eventsManager.onUploaderStatus(status)
	
	def openURL(self, data):
		if data.startswith('/'):
			targetDomen = 'ru' if CURRENT_REALM == 'CURRENT_REALM' else 'eu'
			data = ('http://wotreplays.%s' % targetDomen) + data
		BigWorld.wg_openWebBrowser(data)