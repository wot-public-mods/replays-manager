# SPDX-License-Identifier: MIT
# Copyright (c) 2015-2025 Andrii Andrushchyshyn

import ast
import collections
import importlib
import functools
import itertools
import logging
import mimetools
import os
import types

import BigWorld
import ResMgr
from constants import CURRENT_REALM
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

__all__ = ('byteify', 'override', 'vfs_dir_list_files', 'vfs_file_read', 'parse_localization_file',
			'MultiPartForm', 'requestProgress', 'versionTuple', 'openURL', 'getTankType', 
			'convertData', 'fixBadges', 'safeImport', 'cacheResult', 'cache_result', 'getLogger')

def override(holder, name, wrapper=None, setter=None):
	"""Override methods, properties, functions, attributes
	:param holder: holder in which target will be overrided
	:param name: name of target to be overriden
	:param wrapper: replacement for override target
	:param setter: replacement for target property setter"""
	if wrapper is None:
		return lambda wrapper, setter=None: override(holder, name, wrapper, setter)
	target = getattr(holder, name)
	wrapped = lambda *a, **kw: wrapper(target, *a, **kw)
	if not isinstance(holder, types.ModuleType) and isinstance(target, types.FunctionType):
		setattr(holder, name, staticmethod(wrapped))
	elif isinstance(target, property):
		prop_getter = lambda *a, **kw: wrapper(target.fget, *a, **kw)
		prop_setter = target.fset if not setter else lambda *a, **kw: setter(target.fset, *a, **kw)
		setattr(holder, name, property(prop_getter, prop_setter, target.fdel))
	else:
		setattr(holder, name, wrapped)

def byteify(data):
	"""Encodes data with UTF-8
	:param data: Data to encode"""
	result = data
	if isinstance(data, dict):
		result = {byteify(key): byteify(value) for key, value in data.iteritems()}
	elif isinstance(data, (list, tuple, set)):
		result = [byteify(element) for element in data]
	elif isinstance(data, unicode):
		result = data.encode('utf-8')
	return result

def vfs_file_read(path):
	"""using for read files from VFS"""
	fileInst = ResMgr.openSection(path)
	if fileInst is not None and ResMgr.isFile(path):
		return str(fileInst.asBinary)
	return None

def vfs_dir_list_files(folder_path):
	"""using for list files in VFS dir"""
	result = []
	folder = ResMgr.openSection(folder_path)
	if folder is not None and ResMgr.isDir(folder_path):
		for item_name in folder.keys():
			item_path = '%s/%s' % (folder_path, item_name)
			if item_name not in result and ResMgr.isFile(item_path):
				result.append(item_name)
	return result

def parse_localization_file(file_path):
	"""split items by lines and key value by ':'
	like yaml format"""
	result = {}
	file_data = vfs_file_read(file_path)
	if file_data:
		for test_line in file_data.splitlines():
			if ': ' not in test_line:
				continue
			key, value = test_line.split(': ', 1)
			result[key] = value.replace('\\n', '\n').strip()
	return result

def cache_result(function):
	memo = {}
	@functools.wraps(function)
	def wrapper(*args):
		try:
			return memo[args]
		except KeyError:
			rv = function(*args)
			memo[args] = rv
			return rv
	return wrapper

def openURL(url):
	if url.startswith('/'):
		targetDomain = 'ru' if CURRENT_REALM == 'RU' else 'eu'
		url = 'http://wotreplays.%s%s' % (targetDomain, url)
	BigWorld.wg_openWebBrowser(url)

def cacheResult(function):
	memo = {}
	@functools.wraps(function)
	def wrapper(cache_key):
		try:
			return memo[cache_key]
		except KeyError:
			rv = function(cache_key)
			memo[cache_key] = rv
			return rv
	return wrapper

def getParentWindow():
	uiLoader = dependency.instance(IGuiLoader)
	if uiLoader and uiLoader.windowsManager:
		return uiLoader.windowsManager.getMainWindow()

class MultiPartForm(object):
	"""using for send multipart form data to server"""

	def __init__(self):
		self.form_fields = []
		self.files = []
		self.boundary = mimetools.choose_boundary()

	def getContentType(self):
		return 'multipart/form-data; boundary=%s' % self.boundary

	def add_field(self, name, value):
		self.form_fields.append((name, value))

	def add_file(self, fieldname, filename, fileHandle, mimetype=None):
		body = fileHandle.read()
		mimetype = 'application/octet-stream'
		self.files.append((fieldname, filename, mimetype, body))

	def __str__(self):
		parts = []
		part_boundary = '--' + self.boundary

		parts.extend(
			[part_boundary,
			  'Content-Disposition: form-data; name="%s"' % name,
			  '',
			  value,
			]
			for name, value in self.form_fields
			)

		parts.extend(
			[part_boundary,
			  'Content-Disposition: file; name="%s"; filename="%s"' %
				 (field_name, filename),
			  'Content-Type: %s' % content_type,
			  '',
			  body,
			]
			for field_name, filename, content_type, body in self.files
			)

		flattened = list(itertools.chain(*parts))
		flattened.append('--' + self.boundary + '--')
		flattened.append('')
		return '\r\n'.join(flattened)

class requestProgress(file):
	"""using for track file read progress"""

	def __init__(self, path, mode, callback, *args):
		file.__init__(self, path, mode)
		self.seek(0, os.SEEK_END)
		self._total = self.tell()
		self.seek(0)
		self._callback = callback
		self._args = args

	def __len__(self):
		return self._total

	def read(self, size):
		data = file.read(self, size)
		self._callback(self._total, len(data))
		return str(data)

def versionTuple(stringVersion):
	"""using for get version tuple from string"""
	if ',' not in stringVersion and '.' not in stringVersion:
		return ()
	return tuple(map(int, stringVersion.split(',' if ',' in stringVersion else '.')[:4]))

def getTankType(tags):
	for type in 'heavyTank', 'mediumTank', 'lightTank', 'AT-SPG', 'SPG':
		if type in tags:
			return type
	return ''

def convertData(data):
	result = data
	if isinstance(data, basestring):
		try:
			result = ast.literal_eval(data)
		except:
			result = str(data)
	elif isinstance(data, collections.Mapping):
		result = dict(map(convertData, data.iteritems()))
	elif isinstance(data, collections.Iterable):
		result = type(data)(map(convertData, data))
	return result

def fixBadges(data, indent=0):
	for key in data.keys():
		if key == 'badges':
			badge = data[key]
			if not badge or isinstance(badge[0], int):
				badge = [badge, [1]]
			data[key] = badge
		elif isinstance(data[key], dict):
			data[key] = fixBadges(data[key], indent + 1)
	return data

def safeImport(path, target):
	try:
		module = importlib.import_module(path)
		return getattr(module, target, None)
	except ImportError:
		return None

def getLogger(name):
	logger = logging.getLogger(name)
	logger.setLevel(logging.DEBUG if os.path.isfile('.debug_mods') else logging.ERROR)
	return logger
