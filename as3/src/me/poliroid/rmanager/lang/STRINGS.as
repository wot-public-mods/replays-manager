package me.poliroid.rmanager.lang
{	
	public class STRINGS extends Object
	{
		
		private static var _data:Object = {};
		
		public function STRINGS()
		{
			return;
		}
		
		public static function setData(data:Object) : void 
		{
			for (var name:String in data)
			{
				_data[name] = data[name];
			}
		}
		
		public static function l10n(key:String) : String 
		{
			if (_data.hasOwnProperty(key))
			{
				return _data[key];
			}
			return key
		}
	}
}
