
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

from gui.rmanager.controllers import g_controllers
from gui.rmanager.events import g_eventsManager
from gui.rmanager.lang import l10n
from gui.rmanager.utils import openURL

__all__ = ('ReplaysManagerUploader', )

class ReplaysManagerUploaderMeta(AbstractWindowView):

	def as_setLocalizationS(self, data):
		if self._isDAAPIInited():
			return self.flashObject.as_setLocalization(data)

	def as_onUpdateStatusS(self, status):
		if self._isDAAPIInited():
			return self.flashObject.as_onUpdateStatus(status)

	def as_onUpdateProgressS(self, total, seen, percent):
		if self._isDAAPIInited():
			return self.flashObject.as_onUpdateProgress(total, seen, percent)

	def as_onPopulateResponceS(self, response):
		if self._isDAAPIInited():
			return self.flashObject.as_onPopulateResponce(response)

class ReplaysManagerUploader(ReplaysManagerUploaderMeta):

	def __init__(self, ctx=None):
		super(ReplaysManagerUploader, self).__init__()

	def _populate(self):
		self.as_setLocalizationS(self.__getLocalizationVO())
		super(ReplaysManagerUploader, self)._populate()
		g_eventsManager.onUploaderStatus += self.__onUploaderStatus
		g_eventsManager.onUploaderProgress += self.__onUploaderProgress
		g_eventsManager.onUploaderResult += self.__onUploaderResult
		g_eventsManager.onNeedToClose += self.onWindowClose
		self.as_onUpdateStatusS(g_controllers.uploader.status)

	def _dispose(self):
		g_eventsManager.onUploaderStatus -= self.__onUploaderStatus
		g_eventsManager.onUploaderProgress -= self.__onUploaderProgress
		g_eventsManager.onUploaderResult -= self.__onUploaderResult
		g_eventsManager.onNeedToClose -= self.onWindowClose
		if g_controllers.uploader:
			g_controllers.uploader.clean()
		super(ReplaysManagerUploader, self)._dispose()

	def __onUploaderResult(self, response):
		self.as_onPopulateResponceS(response)

	def __onUploaderStatus(self, status):
		self.as_onUpdateStatusS(status)

	def __onUploaderProgress(self, total, done, percent):
		self.as_onUpdateProgressS(total, done, percent)

	def openURL(self, data):
		openURL(data)

	def upload(self, replayName, replayDescription, isSecret):
		g_controllers.uploader.upload(replayName, replayDescription, isSecret)

	def onWindowClose(self):
		self.destroy()

	def as_isModalS(self):
		if self._isDAAPIInited():
			return False

	def __getLocalizationVO(self):
		result = dict()
		uploaderLangKeys = ('windowTitle', 'labelStatus', 'statusNotFound', 'statusFound', 'statusLoading', \
						'statusConnectionError', 'statusLoadingComplete', 'statusWrongAccount', 'statusNotAccount', \
						'linkLabel', 'statusErrorOccure', 'error0', 'error1', 'error2', 'error3', 'error4', 'error5', \
						'error6', 'progressLabel', 'statusSucces', 'responceLabel', 'buttonStartUpload', 'inputTitle', \
						'inputDescription', 'checkBoxIsSecretLabel', 'checkBoxIsSecretInfo')
		for langKey in uploaderLangKeys:
			result[langKey] = l10n('ui.uploader.%s' % langKey)
		return result
