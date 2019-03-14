package com.kmalyshev.rmanager.utils
{
	import flash.events.EventDispatcher;
	
	import com.kmalyshev.rmanager.events.LoggerEvent;
	
	public class Logger
	{
		
		public static const globalDispatcher:EventDispatcher = new EventDispatcher();
		
		public function Logger()
		{
		}
		
		public static function Error(... args):void
		{
			args.unshift("ERROR");
			__doLog.apply(null, args);
		}
		
		public static function Debug(... args):void
		{
			args.unshift("DEBUG");
			__doLog.apply(null, args);
		}
		
		private static function __doLog():void
		{
			var results:Array = [];
			while (arguments.length)
			{
				results.push(String(arguments.shift()));
			}
			globalDispatcher.dispatchEvent(new LoggerEvent(LoggerEvent.LOG, results));
		}
	
	}

}
