if (!core.ServerExchange) {
    core.ServerExchange = new function(){
		this.isCallInProgress = function() {
			if (this.oo)
				return YAHOO.util.Connect.isCallInProgress(this.oo) ;
			return false; 
		};
		
		this.callIsInProgress = function() {
			if (this.isCallInProgress()) {
				core.LayoutMgr.displayErrorMsg(gettext("Please wait ..."));
				return true;
			}
			return false; 
		};
		
		// WARNING
		// checkNoCallInProgress : default is false
		this.send = function(functionName, obj, retFunc, scope, infoMsg, errorMsg, checkNoCallInProgress){
			
			var makeThatCall = true ;
			if (checkNoCallInProgress === true) {
				makeThatCall = !this.isCallInProgress();
			}
				
			if (makeThatCall) {
				var scp = scope || this;
				// this.graphMgr.processBegin() ;
				
				var callback = {
					success: function(oResponse){
						if (infoMsg) 
							core.LayoutMgr.displayInfoMsg(infoMsg);
						var ret = {};
						if (oResponse.responseText) 
							ret = Ext.util.JSON.decode(oResponse.responseText);
						retFunc.call(this, ret);
					},
					failure: function(o){
						var status = o.status ;
						if (status = 403) 
							core.LayoutMgr.displayErrorMsg(gettext("unauthorized"));
						else if (errorMsg) 
							core.LayoutMgr.displayErrorMsg(errorMsg);
						else  
							core.LayoutMgr.displayErrorMsg(gettext("unknown error"));
					},
					scope: scp
				};
				
				obj["versionId"] = sv_versionId;
				obj["fun"] = functionName;
				this.oo = YAHOO.util.Connect.asyncRequest("post", '/client/', callback, Ext.urlEncode(obj));
			}
			return makeThatCall ;
		};
	}
};
	