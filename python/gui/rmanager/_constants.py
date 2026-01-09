# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2026 Andrii Andrushchyshyn

import os
import BigWorld

# Language
LANGUAGE_FILES = 'mods/net.wargaming.rmanager/text'
LANGUAGE_DEFAULT = 'en'
LANGUAGE_FALLBACK = ('ru', 'be', 'kk', )

DEFAULT_UI_LANGUAGE = 'en'
WAITING_DELAY = 0.3

REPLAYS_MANAGER_WINDOW_ALIAS = 'ReplaysManagerWindow'
REPLAYS_MANAGER_UPLOADER_ALIAS = 'ReplaysManagerUploadWindow'

REPLAY_CM_HANDLER_TYPE = 'replayCMHandler'
REPLAY_FLAG_FILE = 'replay_need_to_play.killme'
DB_VERSION = 17

CLIENT_ROOT = '.'
REPLAYS_PATH = CLIENT_ROOT + '/replays/'
DB_FILENAME = REPLAYS_PATH + 'replays_manager/database'
UPLOAD_REPLAY_TEMP = 'temp_upload_data.dat'

WOTREPLAYS_API_URL = 'http://wotreplays.eu/index.php/api/upload/bwId/%s/username/%s/server/MOD_UPLOAD'
SUPPORTED_REALMS = ('EU', 'NA', 'ASIA')

class UPLOADER_STATUS:
	REPLAY_NOT_FOUND = 'NotFound'
	NOT_ACCOUNT = 'NotAccount'
	WRONG_ACCOUNT = 'WrongAccount'
	CONNECTION_ERROR = 'ConnectionError'
	REPLAY_FOUND = 'Found'
	LOADING = 'Loading'
	LOADING_COMPLETE = 'LoadingComplete'
	ERRORS = (REPLAY_NOT_FOUND, NOT_ACCOUNT, WRONG_ACCOUNT, CONNECTION_ERROR)

class REPLAY_ACTIONS:
	SHOW_RESULTS = 'typeShowResults'
	PLAY = 'typePlay'
	UPLOAD = 'typeUpload'
	FAVORITE_ADD = 'typeFavoriteAdd'
	FAVORITE_REMOVE = 'typeFavoriteRemove'
	REMOVE = 'typeRemove'

class DATABASE_STATES:
	INITED = 'inited'
	FINI = 'fini'
	READY = 'ready'
	PARSING = 'parsing'
	ERROR = 'error'

PROCESS_SUPPORTED_VERSION = (1, 29, 1, 0)
REPLAY_SUPPORTED_VERSION = (1, 29, 1, 0)
RESULTS_SUPPORTED_VERSION = (1, 29, 1, 0)

# number of bytes to pack data in replay file
DEFAULT_PACK_SIZE = 4

DEFAULT_SETTINGS = {
	'filters': {
		'originalXP': False,
		'favorite': -1,
		'battleType': -1,
		'mapName': '',
		'isWinner': -100,
		'tankInfo': {
			'vehicleNation': -1,
			'vehicleLevel': -1,
			'vehicleType': ''
		},
		'dateTime': 'all'
	},
	'sorting': {
		'key': 'timestamp',
		'reverse': True
	},
	'paging': {
		'pageSize': 10,
		'page': 1
	}
}

del os, BigWorld
