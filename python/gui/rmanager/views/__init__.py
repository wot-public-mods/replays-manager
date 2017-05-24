
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ViewTypes, ScopeTemplates

from gui.rmanager.rmanager_constants import REPLAYS_MANAGER_WINDOW_ALIAS, REPLAYS_MANAGER_UPLOADER_ALIAS
from gui.rmanager.views.managerWindow import ReplaysManagerWindow
from gui.rmanager.views.uploaderWindow import ReplaysManagerUploader

def getViewSettings():
	return (ViewSettings(REPLAYS_MANAGER_WINDOW_ALIAS, ReplaysManagerWindow, 'ReplaysManagerWindow.swf', ViewTypes.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE),
			ViewSettings(REPLAYS_MANAGER_UPLOADER_ALIAS, ReplaysManagerUploader, 'ReplaysManagerUpload.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.GLOBAL_SCOPE), )

for item in getViewSettings():
	g_entitiesFactories.addSettings(item)