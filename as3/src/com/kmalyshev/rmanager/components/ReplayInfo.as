package com.kmalyshev.rmanager.components
{
	import flash.display.MovieClip;
	import flash.text.TextField;
	import flash.text.TextFormat;
	
	import scaleform.clik.core.UIComponent;
	import scaleform.clik.constants.InvalidationType;
	import scaleform.clik.events.ButtonEvent;
	
	import net.wg.gui.components.advanced.DashLineTextItem;
	import net.wg.gui.components.controls.UILoaderAlt;
	import net.wg.gui.components.controls.SoundButton;
	import net.wg.gui.cyberSport.controls.CSVehicleButton;
	import net.wg.gui.rally.vo.VehicleVO;
	
	import com.kmalyshev.rmanager.lang.STRINGS;
	import com.kmalyshev.rmanager.events.ReplayActionEvent;
	import com.kmalyshev.rmanager.utils.Utils;
	import com.kmalyshev.rmanager.utils.Helpers;
	import com.kmalyshev.rmanager.utils.Logger;
	
	public class ReplayInfo extends UIComponent
	{
		
		public var battleResult:MovieClip;
		public var mapName:TextField;
		public var battleType:TextField;
		public var noMap:MovieClip;
		public var mapIcon:UILoaderAlt;
		public var mapOverlay:MovieClip;		
		public var vehicleIcon:CSVehicleButton;
		public var dateTime:TextField;
		public var frags:DashLineTextItem;
		public var damage:DashLineTextItem;
		public var credits:DashLineTextItem;
		public var xp:DashLineTextItem;
		public var spotted:DashLineTextItem;
		public var assist:DashLineTextItem;
		
		public var data:Object;
		
		public var btnShowResults:SoundButton;
		public var btnPlay:SoundButton;
		public var btnUpload:SoundButton;
		public var btnRemove:SoundButton;
		
		public var placeholder:TextField;
		
		private var _dashTF:TextFormat;
		
		public function ReplayInfo()
		{
			return;
		}
		
		override protected function configUI():void
		{
			super.configUI();
			
			this._dashTF = new TextFormat();
			this._dashTF.color = 0xFFFFFF;
			this._dashTF.size = 12;
			
			this.mapIcon.autoSize = false;
			this.vehicleIcon.enabled = false;
			this.frags.width = this.damage.width = this.credits.width = this.xp.width = this.spotted.width = this.assist.width = 235;
			this.frags.label = STRINGS.RMANAGER_FRAGS;
			this.damage.label = STRINGS.RMANAGER_DAMAGE;
			this.credits.label = STRINGS.RMANAGER_CREDITS;
			this.xp.label = STRINGS.RMANAGER_XP;						
			this.spotted.label = STRINGS.RMANAGER_SPOTTED;
			this.assist.label = STRINGS.RMANAGER_ASSIST;
			
			this.btnShowResults.width = 235;
			this.btnShowResults.label = STRINGS.RMANAGER_BTN_SHOW_RESULTS;
			this.btnShowResults.enabled = false;
			this.btnShowResults.addEventListener(ButtonEvent.CLICK, this.handleShowResultsButtonClick);
			
			this.btnPlay.width = 235;
			this.btnPlay.label = STRINGS.RMANAGER_BTN_PLAY;
			this.btnPlay.enabled = false;
			this.btnPlay.addEventListener(ButtonEvent.CLICK, this.handlePlayButtonClick);
			
			this.btnUpload.width = 235;
			this.btnUpload.label = STRINGS.RMANAGER_BTN_UPLOAD;
			this.btnUpload.enabled = false;
			this.btnUpload.addEventListener(ButtonEvent.CLICK, this.handleUploadButtonClick);
			
			this.btnRemove.width = 235;
			this.btnRemove.label = STRINGS.RMANAGER_BTN_REMOVE;
			this.btnRemove.enabled = false;
			this.btnRemove.addEventListener(ButtonEvent.CLICK, this.handleRemoveButtonClick);
			
			this.toggleVisible(false);
		}
		
		override protected function onDispose():void
		{
			this.mapIcon.dispose();
			this.mapIcon = null;
			this.vehicleIcon.dispose();
			this.vehicleIcon = null;
			this.frags.dispose();
			this.frags = null;
			this.damage.dispose();
			this.damage = null;
			this.credits.dispose();
			this.credits = null;
			this.xp.dispose();
			this.xp = null;
			this.spotted.dispose();
			this.spotted = null;
			this.assist.dispose();
			this.assist = null;
			this.btnShowResults.removeEventListener(ButtonEvent.CLICK, this.handleShowResultsButtonClick);
			this.btnPlay.removeEventListener(ButtonEvent.CLICK, this.handlePlayButtonClick);
			this.btnUpload.removeEventListener(ButtonEvent.CLICK, this.handleUploadButtonClick);
			this.btnRemove.removeEventListener(ButtonEvent.CLICK, this.handleRemoveButtonClick);
			this.data = null;
			
			super.onDispose();
		}
		
		private function handleShowResultsButtonClick(event:ButtonEvent):void
		{
			this.dispatchEvent(new ReplayActionEvent(ReplayActionEvent.REPLAY_ACTION, this.data.label, ReplayActionEvent.ACTION_TYPE_SHOW_RESULTS));
		}
		
		private function handlePlayButtonClick(event:ButtonEvent):void
		{
			this.dispatchEvent(new ReplayActionEvent(ReplayActionEvent.REPLAY_ACTION, this.data.label, ReplayActionEvent.ACTION_TYPE_PLAY));
		}
		
		private function handleUploadButtonClick(event:ButtonEvent):void
		{
			this.dispatchEvent(new ReplayActionEvent(ReplayActionEvent.REPLAY_ACTION, this.data.label, ReplayActionEvent.ACTION_TYPE_UPLOAD));
		}
		
		private function handleRemoveButtonClick(event:ButtonEvent):void
		{
			this.dispatchEvent(new ReplayActionEvent(ReplayActionEvent.REPLAY_ACTION, this.data.label, ReplayActionEvent.ACTION_TYPE_REMOVE));
		}
		
		override protected function draw():void
		{
			if (isInvalid(InvalidationType.DATA))
			{
				this.setup();
			}
		}
		
		private function setup():void
		{
			if (this.data)
			{
				this.toggleVisible(true);
				try
				{
					this.btnShowResults.enabled = this.data.hasBattleResults && this.data.canShowBattleResults;
					this.btnPlay.enabled = true;
					this.btnUpload.enabled = Helpers.WOTREPLAYS_API_STATUS;
					this.btnRemove.enabled = true;
					
					this.mapName.text = this.data.mapDisplayName;
					this.battleType.text = Utils.getBattleTypeLocalString(this.data.battleType);
					this.mapIcon.source = "../maps/icons/map/stats/" + this.data.mapName + ".png";
					this.dateTime.text = this.data.dateTime;
					
					if (this.data.hasBattleResults)
					{
						if (this.data.winnerTeam == 0)
						{
							this.battleResult.gotoAndStop("draw");
							this.battleResult.textfield.text = STRINGS.RMANAGER_BATTLE_RESULT_DRAW.toUpperCase();
						}
						else
						{
							if (this.data.isWinner)
							{
								this.battleResult.gotoAndStop("victory");
								this.battleResult.textfield.text = STRINGS.RMANAGER_BATTLE_RESULT_VICTORY.toUpperCase();
							}
							else
							{
								this.battleResult.gotoAndStop("defeat");
								this.battleResult.textfield.text = STRINGS.RMANAGER_BATTLE_RESULT_DEFEAT.toUpperCase();
							}
						}
					}
					else
					{
						this.battleResult.gotoAndStop("noresult");
						this.battleResult.textfield.text = STRINGS.RMANAGER_BATTLE_RESULT;
					}
					
					var vehData:Object = {level: this.data.tankInfo.vehicleLevel, nationID: this.data.tankInfo.vehicleNation, type: this.data.tankInfo.vehicleType, name: this.data.playerVehicle, smallIconPath: "../maps/icons/vehicle/small/" + this.data.playerVehicle + ".png", userName: this.data.tankInfo.userString, shortUserName: this.data.tankInfo.shortUserString};
					var vo:VehicleVO = new VehicleVO(vehData);
					this.vehicleIcon.setVehicle(vo);
					this.vehicleIcon.enabled = false;
					
					this.setDashLineValue(this.frags, this.data.kills.toString());
					this.setDashLineValue(this.damage, this.data.damage.toString());
					this.setDashLineValue(this.credits, this.data.credits.toString());
					this.setDashLineValue(this.xp, this.data.xp.toString());										
					this.setDashLineValue(this.spotted, this.data.spotted.toString());
					this.setDashLineValue(this.assist, this.data.damageAssistedRadio.toString());
					
				}
				catch (err:Error)
				{
					Logger.Error("ReplayInfo::setup " + err.getStackTrace());
				}
				
			}
		}
		
		private function clearData():void
		{
			this.mapName.text = "—";
			this.battleType.text = "—";
			this.mapIcon.source = "";
			this.mapIcon.unload();
			this.dateTime.text = "—";
			
			this.battleResult.gotoAndStop("noresult");
			this.battleResult.textfield.text = STRINGS.RMANAGER_BATTLE_RESULT;
			this.vehicleIcon.reset();
			
			this.frags.enabled = false;
			this.damage.enabled = false;
			this.credits.enabled = false;
			this.xp.enabled = false;
			this.spotted.enabled = false;
			this.assist.enabled = false;
			
			this.btnShowResults.enabled = false;
			this.btnPlay.enabled = false;
			this.btnUpload.enabled = false;
			this.btnRemove.enabled = false;
			
			this.toggleVisible(false);
		}
		
		private function setDashLineValue(item:DashLineTextItem, value:String):void
		{
			if (this.data.hasBattleResults)
			{
				item.enabled = true;
				item.validateNow();
				item.valueTextField.htmlText = value;
				item.valueTextField.defaultTextFormat = this._dashTF;
				item.valueTextField.setTextFormat(this._dashTF);
				item.dashLine.width = 235 - (item.labelTextField.textWidth + item.valueTextField.textWidth) - 2 ;
				item.dashLine.x = item.labelTextField.textWidth + 3;
				//item.valueTextField.y = item.valueTextField.y + 2;
				item.valueTextField.x = 235 - item.valueTextField.textWidth + 1;
				item.valueTextField.width = item.valueTextField.textWidth;
			}
			else
			{
				item.enabled = false;
			}
		}
		
		
		private function toggleVisible(visible:Boolean):void {			
			this.placeholder.text = STRINGS.RMANAGER_PLACEHOLDER;
			this.battleResult.visible = visible;
			this.mapName.visible = visible;
			this.battleType.visible = visible;
			this.noMap.visible = visible;
			this.mapIcon.visible = visible;
			this.mapOverlay.visible = visible;
			this.vehicleIcon.visible = visible;
			this.dateTime.visible = visible;
			this.frags.visible = visible;
			this.damage.visible = visible;
			this.credits.visible = visible;
			this.xp.visible = visible;			
			this.spotted.visible = visible;	
			this.assist.visible = visible;	

			this.btnShowResults.visible = visible;
			this.btnPlay.visible = visible;
			this.btnUpload.visible = visible;
			this.btnRemove.visible = visible;

			this.placeholder.visible = !visible;
		}
		
		public function setData(new_data:Object):void
		{
			if (new_data != null)
			{
				this.data = new_data;				
				this.btnShowResults.enabled = true;
				this.btnPlay.enabled = true;
				this.btnUpload.enabled = true;
				this.btnRemove.enabled = true;
				invalidate(InvalidationType.DATA);
			}
			else
			{
				this.clearData();				
			}
		}
	
	}

}
