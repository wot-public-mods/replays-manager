package me.poliroid.rmanager.events
{
	import flash.events.Event;
	
	public class FilterEvent extends Event
	{		
		public static const FILTERS_CHANGED:String = "filtersChanged";
		
		private var _data:Object = null;
		
		public function FilterEvent(type:String, data:Object, bubbles:Boolean = true, cancelable:Boolean = false)
		{
			super(type, bubbles, cancelable);
			_data = data;
		}
		
		public function get data():Object
		{
			return _data;
		}
		
		public override function clone():Event
		{
			return new FilterEvent(type, data, bubbles, cancelable);
		}
	}
}