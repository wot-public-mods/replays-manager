package com.kmalyshev.rmanager.components
{
	import flash.display.MovieClip;
	import flash.events.MouseEvent;
	import flash.text.TextField;
	
	import scaleform.clik.constants.InvalidationType;	
	
	import net.wg.gui.components.controls.SoundListItemRenderer;
	import net.wg.gui.components.controls.UILoaderAlt;
	import net.wg.gui.events.UILoaderEvent;
	
	import com.kmalyshev.rmanager.utils.Logger;
	import com.kmalyshev.rmanager.utils.Utils;
	import com.kmalyshev.rmanager.utils.Helpers;
	
	public class ReplayItemRenderer extends SoundListItemRenderer
	{
		
		public var hitAreaA:MovieClip;
		public var mapIcon:UILoaderAlt;
		public var vehicleIcon:UILoaderAlt;
		
		public var no_map_mc:MovieClip;
		public var favorite_mc:MovieClip;
		public var battleResult:MovieClip;
		
		public var dateTimeTF:TextField;
		public var tankNameTF:TextField;
		public var mapName:TextField;
		public var replayName:TextField;
		public var fragsTF:TextField;
		public var damageTF:TextField;
		public var creditsTF:TextField;
		public var xpTF:TextField;
		public var spottedTF:TextField;
		public var assistTF:TextField;
		
		public function ReplayItemRenderer()
		{
			super();
			this.scaleY = 1;
			this.scaleX = 1;
			this.preventAutosizing = true;
			this.hitArea = this.hitAreaA;
		}
		
		override protected function onDispose():void
		{
			this.data = null;
			super.onDispose();
		}
		
		override public function setData(new_data:Object):void
		{
			if (new_data != null)
			{
				this.data = new_data;
				invalidate(InvalidationType.DATA);
			}
		}
		
		override protected function configUI():void
		{
			super.configUI();
			try
			{
				this.allowDeselect = false;
				this.useRightButton = true;
			}
			catch (err:Error)
			{
				Logger.Error("ReplayItemRenderer::configUI " + err.getStackTrace());
			}
			
			this.vehicleIcon.autoSize = false;

			this.mapIcon.autoSize = false;
			this.mapIcon.width = 231;
			this.mapIcon.height = 98;
			this.mapIcon.addEventListener(UILoaderEvent.COMPLETE, handleMapIconLoaded);

			if (this.data)
			{
				this.setup();
			}
		}
		
		private function handleMapIconLoaded():void
		{
			this.mapIcon.width = 231;
			this.mapIcon.height = 98;
		}
		
		override protected function draw():void
		{
			if (isInvalid(InvalidationType.DATA))
			{
				this.setup();
			}
			super.draw();
			
			visible = data != null;
			
			if (this.selected)
			{
				this.gotoAndStop("selected_up");
			}
		}
		
		private function setup():void
		{
			if (this.data)
			{
				try
				{
					this.mapIcon.visible = true;
					this.no_map_mc.visible = false;
					
					this.favorite_mc.visible = Boolean(this.data.favorite);
					
					this.dateTimeTF.text = this.data.dateTime;
					this.tankNameTF.text = this.data.tankInfo.shortUserString;
					
					var battleType:String = Utils.getBattleTypeLocalString(this.data.battleType);
					this.mapName.text = this.data.mapDisplayName + ", " + battleType;
					//this.replayName.text = Utils.truncateString(this.data.label, 48);
					
					this.fragsTF.text = this.data.hasBattleResults ? this.data.kills : "—";
					this.damageTF.text = this.data.hasBattleResults ? this.data.damage : "—";
					this.creditsTF.text = this.data.hasBattleResults ? this.data.credits : "—";
					this.xpTF.text = this.data.hasBattleResults ? this.data.xp : "—";
					this.spottedTF.text = this.data.hasBattleResults ? this.data.spotted : "—";
					this.assistTF.text = this.data.hasBattleResults ? this.data.damageAssistedRadio : "—";
					
					this.mapIcon.addEventListener(UILoaderEvent.IOERROR, this.onMapIconIOError);
					this.mapIcon.source = "../maps/icons/map/stats/" + this.data.mapName + ".png";
					this.vehicleIcon.addEventListener(UILoaderEvent.IOERROR, this.onVehicleIconIOError);
					this.vehicleIcon.source = "../maps/icons/vehicle/" + this.data.playerVehicle + ".png";
					
					if (this.data.winnerTeam == 0)
					{
						this.battleResult.gotoAndStop("draw");
					}
					else
					{
						this.battleResult.gotoAndStop(this.data.isWinner == 1 ? "victory" : "defeat");
					}
					
					this.battleResult.visible = this.data.hasBattleResults;
					if (this.data.hasBattleResults)
					{
						if (this.data.winnerTeam == 0)
						{
							this.battleResult.gotoAndStop("draw");
						}
						else
						{
							this.battleResult.gotoAndStop(this.data.isWinner == 1 ? "victory" : "defeat");
						}
					}
					
				}
				catch (err:Error)
				{
					Logger.Error("ReplayItemRenderer::setup " + err.getStackTrace());
				}
			}
		}
		
		override protected function handleMousePress(event:MouseEvent):void
		{
			if (App.utils.commons.isRightButton(event))
			{
				var replayData:Object = {
					replayName: this.data.label, 
					hasBattleResults: Boolean(this.data.hasBattleResults),
					canShowBattleResults: Boolean(this.data.canShowBattleResults),
					apiStatus: Helpers.WOTREPLAYS_API_STATUS, 
					isFavorite: Boolean(this.data.favorite)
				}
				App.contextMenuMgr.show(Helpers.REPLAY_CM_HANDLER_TYPE, this, replayData);
			}
		}
		
		private function onVehicleIconIOError(event:UILoaderEvent):void
		{
			this.vehicleIcon.source = "../maps/icons/vehicle/noImage.png";
			if (this.vehicleIcon.hasEventListener(UILoaderEvent.IOERROR))
			{
				this.vehicleIcon.removeEventListener(UILoaderEvent.IOERROR, this.onVehicleIconIOError);
			}
		}
		
		private function onMapIconIOError(event:UILoaderEvent):void
		{
			this.mapIcon.visible = false;
			this.no_map_mc.visible = true;
			if (this.mapIcon.hasEventListener(UILoaderEvent.IOERROR))
			{
				this.mapIcon.removeEventListener(UILoaderEvent.IOERROR, this.onMapIconIOError);
			}
		}
	
	}

}
