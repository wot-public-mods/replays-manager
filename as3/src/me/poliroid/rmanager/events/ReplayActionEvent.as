package me.poliroid.rmanager.events
{
	import flash.events.Event;
	
	public class ReplayActionEvent extends Event
	{
		
		public static const REPLAY_ACTION:String = "replayAction";
		public static const ACTION_TYPE_SHOW_RESULTS:String = "typeShowResults";
		public static const ACTION_TYPE_PLAY:String = "typePlay";
		public static const ACTION_TYPE_UPLOAD:String = "typeUpload";
		public static const ACTION_TYPE_REMOVE:String = "typeRemove";
		public var replayName:String = "";
		public var actionType:String = "";
		
		public function ReplayActionEvent(type:String, replayName:String, actionType:String, bubbles:Boolean = true, cancelable:Boolean = false)
		{
			super(type, bubbles, cancelable);
			this.actionType = actionType;
			this.replayName = replayName;
		}
		
		public override function clone():Event
		{
			return new ReplayActionEvent(type, this.replayName, this.actionType, bubbles, cancelable);
		}
	
	}

}
