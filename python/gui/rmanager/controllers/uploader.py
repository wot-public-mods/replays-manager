
import math
import os
import threading
import urllib2
from adisp import adisp_async, adisp_process

import BigWorld
from account_helpers import getAccountDatabaseID
from constants import CURRENT_REALM
from helpers import isPlayerAccount
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from ..events import g_eventsManager
from .._constants import (WAITING_DELAY, WOTREPLAYS_API_URL, REPLAYS_PATH,
											UPLOADER_STATUS, UPLOAD_REPLAY_TEMP)
from ..utils import MultiPartForm, requestProgress

__all__ = ('UploaderController', )

class ReplayInfo(object):

	def __init__(self):
		self.name = None
		self.description = None
		self.fileName = None
		self.userDBID = None
		self.userName = None
		self.secret = False

class UploaderController(object):

	@property
	def status(self):
		return self.__status

	def __init__(self):
		self.__replay = ReplayInfo()
		self.__status = None
		self.__sended = 0.0

	def init(self):
		self.clean()

	def fini(self):
		self.clean()

	def clean(self):
		self.__replay = ReplayInfo()
		self.__status = None
		self.__sended = 0.0

	@staticmethod
	@adisp_async
	@adisp_process
	def apiStatus(callback):
		url = 'http://wotreplays.%s' % ('ru' if CURRENT_REALM == 'RU' else 'eu')
		response = yield lambda callback: BigWorld.fetchURL(url, callback)
		LOG_DEBUG('UploaderController.apiStatus %s' % response.responseCode, response.body)
		callback(response.responseCode == 200)

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

		self.__replay.fileName = replayFileName
		self.__replay.userDBID = replayUserDBID
		self.__replay.userName = replayUserName

		self.__setStatus(UPLOADER_STATUS.REPLAY_FOUND)

		return True

	def upload(self, replayName, replayDescription, isSecret):

		if self.__status in UPLOADER_STATUS.ERRORS:
			return

		self.__replay.name = replayName
		self.__replay.description = replayDescription
		self.__replay.secret = isSecret

		thread = threading.Thread(target=self.__uploaderThread)
		thread.daemon = True
		BigWorld.callback(WAITING_DELAY, thread.start)

	def __uploaderThread(self):

		fileStream = open(REPLAYS_PATH + self.__replay.fileName, 'rb')

		form = MultiPartForm()

		if self.__replay.name:
			form.add_field('Replay[title]', str(self.__replay.name))

		if self.__replay.description:
			form.add_field('Replay[description]', str(self.__replay.description))

		form.add_field('Replay[isSecret]', str(int(self.__replay.secret)))

		form.add_file('Replay[file_name]', self.__replay.fileName, fileStream)

		targetDomain = 'ru' if CURRENT_REALM == 'RU' else 'eu'
		targetURL = WOTREPLAYS_API_URL % (targetDomain, str(self.__replay.userDBID), str(self.__replay.userName))

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
		except: #NOSONAR
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
