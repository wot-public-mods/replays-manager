package com.kmalyshev.rmanager.utils
{
	
	public class Utils
	{
		
		public function Utils()
		{
			super();
		}
		
		public static function objectToString(obj:Object):String
		{
			var result:String = "";
			for (var i:*in obj)
			{
				result += i + ":" + obj[i] + ", ";
			}
			return result;
		}
		
		public static function getDataFromList(list:*):*
		{
			return list.dataProvider[list.selectedIndex].data;
		}
		
		public static function traceObject(oObj:Object, sPrefix:String = ""):void
		{
			sPrefix == "" ? sPrefix = "---" : sPrefix += "---";
			for (var i:*in oObj)
			{
				Logger.Debug(sPrefix, i + " : " + oObj[i], "  ");
				if (typeof(oObj[i]) == "object")
				{
					traceObject(oObj[i], sPrefix);
				}
			}
		}
		
		public static function getBattleTypeLocalString(battleTypeNum:String):String
		{
			var result:* = null;
			result = "#menu:loading/battleTypes/" + battleTypeNum;
			if (MENU.LOADING_BATTLETYPES_ENUM.indexOf(result) != -1) {
				result = App.utils.locale.makeString(result);
				return result;
			}
			return "";
		}
		
		public static function truncateString(str:String, maxLength:Number, addAfter:String = "..."):String
		{
			var strLen = str.length;
			var sliceChars = maxLength - strLen;
			if (sliceChars < 0)
			{
				str = str.slice(0, sliceChars - 3) + addAfter;
			}
			return str;
		}
		
		public static function getRangeArray(start:Number, end:Number):Array
		{
			var result:Array = new Array();
			for (var i:int = start; i <= end; i++)
			{
				result.push(i);
			}
			return result;
		}
		
		public static function isOdd(num:int):Boolean
		{
			if (num % 2 == 0)
			{
				return false;
			}
			else
			{
				return true;
			}
		}
		
		public static function mergeObjects(obj0:Object, obj1:Object):Object
		{
			var obj:Object = {};
			for (var key in obj0)
			{
				obj[key] = (obj1[key] != null) ? obj1[key] : obj0[key];
			}
			return obj;
		}
	
	}

}