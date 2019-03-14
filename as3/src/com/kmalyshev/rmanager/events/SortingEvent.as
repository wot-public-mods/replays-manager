package com.kmalyshev.rmanager.events
{
	import flash.events.Event;
	
	public class SortingEvent extends Event
	{
		
		public static const SORT_KEY_CHANGED:String = "sortKeyChanged";
		
		private var _sortKey:String = "";
		private var _asc:Boolean = true;
		
		public function SortingEvent(type:String, sortKey:String, ascending:Boolean, bubbles:Boolean = true, cancelable:Boolean = false)
		{
			super(type, bubbles, cancelable);
			_sortKey = sortKey;
			_asc = ascending;
		}
		
		public function get sortKey():String
		{
			return _sortKey;
		}
		
		public function get ascending():Boolean
		{
			return _asc;
		}
		
		public override function clone():Event
		{
			return new SortingEvent(type, sortKey, ascending, bubbles, cancelable);
		}
	}
}