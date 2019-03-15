
import ast
import collections
import itertools
import mimetools
import os
import types
import urllib

import BigWorld
import ResMgr
from constants import CURRENT_REALM

__all__ = ('byteify', 'override', 'readFromVFS', 'parseLangFields', 'MultiPartForm', 'requestProgress', \
			'versionTuple', 'openURL', 'getTankType', 'convertData')

def override(holder, name, target=None):
	"""using for override any staff"""
	if target is None:
		return lambda target: override(holder, name, target)
	original = getattr(holder, name)
	overrided = lambda *a, **kw: target(original, *a, **kw)
	if not isinstance(holder, types.ModuleType) and isinstance(original, types.FunctionType):
		setattr(holder, name, staticmethod(overrided))
	elif isinstance(original, property):
		setattr(holder, name, property(overrided))
	else:
		setattr(holder, name, overrided)

def byteify(data):
	"""using for convert unicode key/value to utf-8"""
	result = data
	if isinstance(data, types.DictType):
		result = {byteify(key): byteify(value) for key, value in data.iteritems()}
	elif isinstance(data, (types.ListType, tuple, set)):
		result = [byteify(element) for element in data]
	elif isinstance(data, types.UnicodeType):
		result = data.encode('utf-8')
	return result

def parseLangFields(langFile):
	"""split items by lines and key value by ':'
	like yaml format"""
	result = {}
	langData = readFromVFS(langFile)
	if langData:
		for item in langData.splitlines():
			if ': ' not in item:
				continue
			key, value = item.split(": ", 1)
			result[key] = value
	return result

def readFromVFS(path):
	"""using for read files from VFS"""
	file = ResMgr.openSection(path)
	if file is not None and ResMgr.isFile(path):
		return str(file.asBinary)
	return None

def openURL(url):
	if url.startswith('/'):
		targetDomain = 'ru' if CURRENT_REALM == 'RU' else 'eu'
		url = 'http://wotreplays.%s%s' % (targetDomain, url)
	BigWorld.wg_openWebBrowser(url)

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

		parts.extend( \
			[part_boundary, \
			  'Content-Disposition: form-data; name="%s"' % name, \
			  '', \
			  value, \
			] \
			for name, value in self.form_fields \
			)

		parts.extend( \
			[part_boundary, \
			  'Content-Disposition: file; name="%s"; filename="%s"' % \
				 (field_name, filename), \
			  'Content-Type: %s' % content_type, \
			  '', \
			  body, \
			] \
			for field_name, filename, content_type, body in self.files \
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
		except: #NOSONAR
			result = str(data)
	elif isinstance(data, collections.Mapping):
		result = dict(map(convertData, data.iteritems()))
	elif isinstance(data, collections.Iterable):
		result = type(data)(map(convertData, data))
	return result
