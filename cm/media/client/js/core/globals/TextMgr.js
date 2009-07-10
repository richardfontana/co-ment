// core.TextMgr
if (!core.TextMgr) {
    core.TextMgr = new function() {
		this._attachMgr = null ;
		
		// workflow 
		this._comment_workflow_states = sv_comment_workflow_states ;
		
		// attach listener to click on text
		if (!coment.cst.framed)
			YAHOO.util.Event.addListener(coment.cst.textNodeId, "click", this.textClick, this, true); 
		// else the event listener is added directly from inside the iframe
	
		this.register = function(attachMgr){
			this._attachMgr = attachMgr ;
			var btn = Ext.get('add_btn') ;
			if (btn) 
				btn.on('click', attachMgr.addAttachButtonClick, attachMgr) ;
			btn = Ext.get('edit_btn') ;
			if (btn) 
				btn.on('click', attachMgr.editAttachButtonClick, attachMgr) ;
			btn = Ext.get('edit_cancel_btn') ;
			if (btn) 
				btn.on('click', attachMgr.editCancelAttachButtonClick, attachMgr) ;
			btn = Ext.get('edit_modif_scope') ;
			if (btn) 
				btn.on('click', attachMgr.editAttachModifScopeClick, attachMgr) ;
				
			Ext.ComponentMgr.get('tagcloud').body.on('click', attachMgr.tagclicked, attachMgr) ;
			
		};

		this.onFilterMgrApply = function(type, args, me) {
			me._attachMgr.renderOccurences() ; 
			me._attachMgr.populateTagCloud() ; 
	
			core.LayoutMgr.activateAttachListTab() ;
		};
		
		this.textClick = function(evt) {
			if (!core.ServerExchange.callIsInProgress()) {
				var target = YAHOO.util.Event.getTarget(evt);
				this._attachMgr.occClick(target.id, evt);
			}
		};
		// success message is handled on return
		this.applyAmendments = function() {
			if (!core.ServerExchange.callIsInProgress()) {
				var done = core.ServerExchange.send("applyAmendments", {}, this._applyAmendmentsReturns, this, "", gettext("amendments could not be added"));
			}
		};
		
		this._applyAmendmentsReturns = function(ret) {
			core.LayoutMgr.displayInfoMsg(ret['success_message']);
			// reload page ?
			window.location.href=ret['location'] ;
		};
		
		this.downOnFrame = function(evt) {
			core.LayoutMgr.hidemenus() ;
		};
		
		this.getStateOptions = function () {
			var ret = '' ;
			for (var state_id in this._comment_workflow_states) {
				ret = ret + '<option value="' + state_id + '">' + this._comment_workflow_states[state_id] + '</option>' ;
			}
			return ret ;
		};
		
		this.getWorkflowStates = function () {
			var ret = [] ;
			for (var state_id in this._comment_workflow_states) {
				ret[ret.length] = [state_id, this._comment_workflow_states[state_id]] ;
			}
			return ret ;
		};
		
		this.getWorkflowStateValues = function () {
			var ret = [] ;
			for (var state_id in this._comment_workflow_states) {
				ret[ret.length] = state_id ;
			}
			return ret ;
		};
		
		this.getStateName = function (state_id) {
			return this._comment_workflow_states[state_id] ;
		};
		
		this.onMailSubscribe = function() {
			var mailsub = (sv_mailsub)?'0':'1';
			if (!core.ServerExchange.callIsInProgress()) {
				var done = core.ServerExchange.send("mailSubscribe", {"mailsub":mailsub}, this._mailSubscribeReturns, this, "", gettext("could not subscribe"));
			}
		};
		
		this._mailSubscribeReturns = function(ret) {
			core.LayoutMgr.displayInfoMsg(ret['success_message']);
			sv_mailsub = ret['new_sub'] ;
			core.LayoutMgr.updateMailLnk() ;
		};
		
	};
}


