core.DiscussionItem = function(sDiscussionItem, attachMgr){
	// the server DiscussionItem entity
	this._discussionItem = sDiscussionItem ; 
	this._dispId = "disc-" + this._discussionItem.id ; 

    this._attachMgr = attachMgr	;

	this._tpl = new Ext.DomHelper.Template('<div id="{id}" class="disp_discussionitem">' +
											'<span id="delete-{id}" class="comment_btn comment_delete yunselectable {vis_remclass}" title="{delete_reply_tooltip}"><pre>   </pre></span>' +
											'<span id="edit-{id}" class="comment_btn comment_edit yunselectable {vis_remclass}" title="{edit_reply_tooltip}"><pre>   </pre></span>' +
											'<select id="select_state-{id}" class="displaynone comment_wfstate_select comment_btn">{select_options}</select>' +
											'<span id="current_state-{id}" class="comment_wfstate comment_btn {vis_manclass}" title="{change_wfstate_tooltip}">{current_state}</span>' +
											'<div id="reply_title-{id}" class="comment_title_cls yunselectable">{title}</div>' +
											'<div class="comment_authordate_cls yunselectable">{authordate}</div>' +
											'<div id="reply_text-{id}" class="comment_text_cls yunselectable">{text}</div>' +
											'<div id="reply_tags-{id}" class="comment_tags_cls yunselectable">{thetags}</div></div>');
	
	this._tpl.compile();
} ;
core.DiscussionItem.prototype = {
	couldBeEdited: function(creationTime){
		var ret = false ;
		if (sv_remComPerm)
			ret = true ;
		else {
			if (sv_loggedIn && this._discussionItem['username'] == sv_username && this._discussionItem.state_id == sv_wrkf_initialstateid) {
				var attach = this._attachMgr._attachController.getAttach(this.getParentAttachId()) ;
				if (attach.attach.discussion_count == 1)
					ret = true ;
				else {
					var discs = Ext.get("discs-comment-"+attach.getId()) ;
					if (discs) {
						if (creationTime) {// to check if this is the last reply we compare comment discussion count with current number of replies in dom : 
							ret = (discs.dom.childNodes.length == (attach.attach.discussion_count - 1)) ;
						}
						else 
							ret = (discs.dom.childNodes[discs.dom.childNodes.length-1].id == this._dispId) ;
					}
				}
			}
		}
		return ret ;
	},

	toDom: function(){
		var ad = coment.util.getAuthorAndDate(this._discussionItem);
		
		var visRem = (this.couldBeEdited(true))?"":"displaynone" ;
		var visMan = (sv_so_b || sv_manageComPerm) ? "" : "displaynone";
		var tags = this._getTags() ;
		
		var d = {
			id: this._dispId,
			authordate: ad,
			title: this._discussionItem.title,
			delete_reply_tooltip: gettext("delete reply"),
			edit_reply_tooltip :gettext("edit comment"),
			text: this._discussionItem.content,
			vis_remclass: visRem,
			vis_manclass: visMan,
			thetags:tags,
			change_wfstate_tooltip: gettext("click to change"),
			select_options: core.TextMgr.getStateOptions(),
			current_state: core.TextMgr.getStateName(this._discussionItem.state_id)
		};
		
		return this._tpl.applyTemplate(d);
	},
	
	_getTags:function(){
		var tags = this._discussionItem.tags ;
		if (tags != "")
			tags = gettext("tags:") + tags ;
		return tags 
	},
	
	deleteMe: function(e){
		if (!core.ServerExchange.callIsInProgress()) {
			if (confirm(gettext("Are you sure you want to delete this reply ?"))) {
				// now we may have to change the editability and deletebility of previous reply
				this._attachMgr.deleteDiscussionItem(this);
				this._attachMgr.populateTagCloud();
			}
			// to prevent a selection of the list item (works fine)
			YAHOO.util.Event.stopPropagation(e);
		}
	},
	
	editMe : function(e){
		if (!core.ServerExchange.callIsInProgress()) {
			this._attachMgr.editAttach(this.getParentAttachId(), this.getId(), 1, this._discussionItem.title, this._discussionItem.content, this._discussionItem.tags);
		}
	},

	getId: function(){
		return this._discussionItem.id;
	},
	
	getParentAttachId: function(){
		return this._discussionItem.comment_id;
	},
	
	getState: function(){
		return this._discussionItem.state;
	},
	
	isVisible: function(){
		return this._discussionItem.state.visible;
	},
	
	getDispId: function(){
		return this._dispId;
	},
	
	setDiscussionItem: function(sDi){
		return this._discussionItem = sDi;
	},
	
	// triggered when user clicks on the current comment state. Setup the select state choice.
	toStateChoice: function(e){
		var comment_wfstate = YAHOO.util.Dom.get('current_state-' + this._dispId);
		var comment_wfstate_select = YAHOO.util.Dom.get('select_state-' + this._dispId);
		
		this._attachMgr.toStateChoice(comment_wfstate, comment_wfstate_select, this._discussionItem.state_id)
	},
	
	// triggered when user chooses a state. Setup the current state choice.
	toCurrentState: function(e){
	
		if (!core.ServerExchange.callIsInProgress()) {
			var comment_wfstate = YAHOO.util.Dom.get('current_state-' + this._dispId);
			var comment_wfstate_select = YAHOO.util.Dom.get('select_state-' + this._dispId);
			this._attachMgr.toCurrentState(comment_wfstate, comment_wfstate_select, this._discussionItem.state_id, this.getId(), this._attachMgr.updateDiscussionItemState, this._attachMgr);
		}
		YAHOO.util.Event.stopPropagation(e);
	},
	
	refreshMe : function() {
		// updates only : title, content and tags
		var t = Ext.fly("reply_title-" + this._dispId) ;
		if (t)
			t.update(this._discussionItem.title) ;
		t = Ext.fly("reply_text-" + this._dispId) ;
		if (t)
			t.update(this._discussionItem.content) ;
		t = Ext.fly("reply_tags-" + this._dispId) ;
		if (t)
			t.update(this._getTags()) ;
	},

	// triggered when user chooses not to choose a state. 
	toNoState: function(e){
		var comment_wfstate = YAHOO.util.Dom.get('current_state-' + this._dispId);
		var comment_wfstate_select = YAHOO.util.Dom.get('select_state-' + this._dispId);
		this._attachMgr.switchSelect(comment_wfstate, comment_wfstate_select, true);
		
	},
	
	connect: function(){
		Ext.fly("delete-" + this._dispId).on("click", this.deleteMe, this);
		Ext.fly("edit-" + this._dispId).on("click", this.editMe, this) ;
		Ext.fly("current_state-" + this._dispId).on("click", this.toStateChoice, this);
		Ext.fly("select_state-" + this._dispId).on("change", this.toCurrentState, this);
		Ext.fly("select_state-" + this._dispId).on("blur", this.toNoState, this);
	}
}
