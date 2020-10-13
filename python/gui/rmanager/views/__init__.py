from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from frameworks.wulf import WindowLayer

from gui.rmanager.rmanager_constants import REPLAYS_MANAGER_WINDOW_ALIAS, REPLAYS_MANAGER_UPLOADER_ALIAS
from gui.rmanager.views.managerWindow import ReplaysManagerWindow
from gui.rmanager.views.uploaderWindow import ReplaysManagerUploader

def getViewSettings():
	viewSettings = []
	viewSettings.append(ViewSettings(REPLAYS_MANAGER_WINDOW_ALIAS, ReplaysManagerWindow, 'ReplaysManagerWindow.swf',
						WindowLayer.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE, isModal=True, canClose=True, canDrag=False))
	viewSettings.append(ViewSettings(REPLAYS_MANAGER_UPLOADER_ALIAS, ReplaysManagerUploader, 'ReplaysManagerUpload.swf',
						WindowLayer.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE, isModal=True, canClose=True, canDrag=True))
	return viewSettings

for item in getViewSettings():
	g_entitiesFactories.addSettings(item)
