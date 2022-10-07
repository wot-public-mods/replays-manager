package me.poliroid.rmanager.events
{
	import flash.events.Event;
	
	public class PagingEvent extends Event
	{
		
		public static const PAGE_CHANGED:String = "pageChanged";
		
		private var _currentPage:Number = 0;
		
		public function PagingEvent(type:String, currentPage:Number, bubbles:Boolean = true, cancelable:Boolean = false)
		{
			super(type, bubbles, cancelable);
			_currentPage = currentPage;
		}
		
		public function get currentPage():Number
		{
			return _currentPage;
		}
		
		public override function clone():Event
		{
			return new PagingEvent(type, currentPage, bubbles, cancelable);
		}
	}
}