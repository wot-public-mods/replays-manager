# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2026 Andrii Andrushchyshyn

from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ViewSettings, ScopeTemplates
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

from .._constants import REPLAYS_MANAGER_WINDOW_ALIAS, REPLAYS_MANAGER_UPLOADER_ALIAS
from .managerWindow import ReplaysManagerWindow
from .uploaderWindow import ReplaysManagerUploader

def getViewSettings():
	viewSettings = []
	viewSettings.append(ViewSettings(REPLAYS_MANAGER_WINDOW_ALIAS, ReplaysManagerWindow, 'ReplaysManagerWindow.swf',
						WindowLayer.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE, isModal=False, canClose=True, canDrag=True))
	viewSettings.append(ViewSettings(REPLAYS_MANAGER_UPLOADER_ALIAS, ReplaysManagerUploader, 'ReplaysManagerUpload.swf',
						WindowLayer.WINDOW, None, ScopeTemplates.GLOBAL_SCOPE, isModal=True, canClose=True, canDrag=True))
	return viewSettings

guiLoader = dependency.instance(IGuiLoader)

for item in getViewSettings():
	guiLoader.entitiesFactory.addSettings(item)
