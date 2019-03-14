
import ResMgr
import types
import itertools
import collections
import mimetools
import os
from ast import literal_eval

__all__ = ('byteify', 'override', 'readFromVFS', 'parseLangFields', 'MultiPartForm', 'requestProgress', 'versionTuple', 'getTankType', 'convertKeys', 'convertData')

def overrider(target, holder, name):
	"""using for override any staff"""
	original = getattr(holder, name)
	overrided = lambda *a, **kw: target(original, *a, **kw)
	if not isinstance(holder, types.ModuleType) and isinstance(original, types.FunctionType):
		setattr(holder, name, staticmethod(overrided))
	elif isinstance(original, property):
		setattr(holder, name, property(overrided))
	else:
		setattr(holder, name, overrided)
def decorator(function):
	def wrapper(*args, **kwargs):
		def decorate(handler):
			function(handler, *args, **kwargs)
		return decorate
	return wrapper
override = decorator(overrider)

def byteify(data):
	"""using for convert unicode key/value to utf-8"""
	if isinstance(data, types.DictType): 
		return { byteify(key): byteify(value) for key, value in data.iteritems() }
	elif isinstance(data, types.ListType) or isinstance(data, tuple) or isinstance(data, set):
		return [ byteify(element) for element in data ]
	elif isinstance(data, types.UnicodeType):
		return data.encode('utf-8')
	else: 
		return data

def parseLangFields(langCode):
	"""split items by lines and key value by : 
	like yaml format"""
	from gui.rmanager.rmanager_constants import LANGUAGE_FILE_PATH
	result = {}
	langData = readFromVFS(LANGUAGE_FILE_PATH % langCode)
	if langData:
		for item in langData.splitlines():
			if ': ' not in item: continue
			key, value = item.split(": ", 1)
			result[key] = value
	return result

def readFromVFS(path):
	"""using for read files from VFS"""
	file = ResMgr.openSection(path)
	if file is not None and ResMgr.isFile(path):
		return str(file.asBinary)
	return None

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
			[ part_boundary,
			  'Content-Disposition: form-data; name="%s"' % name,
			  '',
			  value,
			]
			for name, value in self.form_fields
			)

		parts.extend(
			[ part_boundary,
			  'Content-Disposition: file; name="%s"; filename="%s"' % \
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
	types = { 'heavyTank', 'mediumTank', 'lightTank', 'AT-SPG', 'SPG' }
	for type in types:
		if type in tags:
			return type
	return ''

def convertKeys(d):
	output_dict = dict()
	for k,v in d.iteritems():
		try:
			new_key = int(k)
		except:
			new_key = convertData(k)
		output_dict[new_key] = v
	return output_dict

def convertData(data):
	if isinstance(data, basestring):
		try:
			return literal_eval(data)
		except:
			return str(data)
	elif isinstance(data, collections.Mapping):
		return dict(map(convertData, data.iteritems()))
	elif isinstance(data, collections.Iterable):
		return type(data)(map(convertData, data))
	else:
		return data