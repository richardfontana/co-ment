commentListItemSelector = 'div.coment_comment';
										  
_paneltpl = new Ext.DomHelper.Template('<div id="{id}" class="disp_comment">' +
									    	 '<span id="delete-{id}" class="comment_btn comment_delete yunselectable {vis_remclass}" title="{delete_comment_tooltip}"><pre>   </pre></span>' +
									    	 '<span id="edit-{id}" class="comment_btn comment_edit yunselectable {vis_remclass}" title="{edit_comment_tooltip}"><pre>   </pre></span>' +
									    	 '<select id="select_state-{id}" class="displaynone comment_wfstate_select comment_btn">{select_options}</select>' +
									    	 '<span id="current_state-{id}" class="comment_wfstate comment_btn {vis_manclass}" title="{change_wfstate_tooltip}">{current_state}</span>' + 
									    	 '<div  id="comment_title-{id}" class="comment_title_cls">{title}</div>' +
									    	 '<div class="comment_authordate_cls">{authordate}</div>' +
									    	 '<div id="excerpt-{id}" class="comment_text_cls">{excerpt_text}</div>' +
									    	 '<div id="text-{id}" class="displaynone comment_text_cls">{text}</div>' +
											 '<div id="comment_tags-{id}" class="comment_tags_cls yunselectable">{comment_tags}</div>' +
											 '<div id="comment_nbreplies-{id}" class="comment_nbreplies yunselectable">{nbreplies}</div>' +
											 '<span id="read-{id}" class="{vis_readbtnclass} comment_readreply yunselectable">{read}</span>' +
											 '<span id="discs-{id}"></span>' +
											 '<span id="minimize-{id}" class="comment_readreply yunselectable displaynone">{minimize}</span>' +
											 '<span id="reply-{id}" class="{vis_replybtnclass} comment_readreply yunselectable">{reply}</span>' +
											 '<div id="replyform-{id}" class="displaynone discussattach yunselectable"></div>' +
									    	 '</div>');
_paneltpl.compile();


_replyformtpl = new Ext.DomHelper.Template('' +
			'<div id="add_attach_user-{id}" class="displaynone">' +
		        '<label>{authornamelabel}</label>' +
		        '<input type="text" size="22" id="discuss_author-{id}" name="author" value="{cook_name}" class="textinput"></input>' +
		        '<div class="field_error displaynone" id="error_discuss_author-{id}"></div>' +
		        '<label>{authoremaillabel}</label>' +
		        '<input type="text" size="22" id="discuss_email-{id}" name="email" value="{cook_email}" class="textinput"></input>' +
		        '<div class="field_error displaynone" id="error_discuss_email-{id}"></div>' +
			'</div>' +
			'<label>{replytitlelabel}<span class="requir">*</span></label>'+
			'<input type="text" size="22" id="discuss_comment_title-{id}" class="textinput" value="{replytitle}"></input>'+
			'<div id="error_discuss_comment_title-{id}" class="field_error displaynone"></div>'+
			'<label>{replytextlabel}<span class="requir">*</span></label>'+
			'<textarea rows="10" cols="40" id="discuss_comment_text-{id}" type="text" class="textinput"></textarea>'+
			'<div id="error_discuss_comment_text-{id}" class="field_error displaynone"></div>'+
			'<label >{tagslabel}</label>'+
			'<input type="text" class="textinput" id="discuss_comment_tags-{id}" size="22"></input>'+
			'<div class="field_error displaynone" id="error_discuss_comment_tags-{id}"></div>'+
			'<table><tr><td><div id="applyreply-{id}"></div></td><td><div id="cancelreply-{id}"></div></td></tr></table>');
_replyformtpl.compile();
			
core.Attach = function(attach, attachMgr){
	// the server attach entity
	this.attach = attach ; 

	// ID of dom element in Attach List Panel
	this._listid = "comment-" + this.attach.id ;
	this._panelid = "panel-comment-" + this.attach.id ;

    this._attachMgr = attachMgr	;
}

core.Attach.prototype = {
    getId : function(){
        return this.attach.id ;
    },

    getPanelId : function(){
        return this._panelid ;
    },
    
    getListId : function(){
        return this._listid ;
    },
    
    getStartWord : function(){
        return this.attach.start_word ;
    },
    
    getEndWord : function(){
        return this.attach.end_word ;
    },

    setAttach : function(attach){
        this.attach = attach ;
    },
	
	computeNbRepliesMsg : function(){
		ret = "" ;
		if (this.attach.discussion_count && this.attach.discussion_count > 0) {
			if (this.attach.discussion_count <= 1)
				ret = interpolate(gettext("%(count)s reply"), {count : this.attach.discussion_count}, true);
			else
				ret = interpolate(gettext("%(count)s replies"), {count : this.attach.discussion_count}, true);
		}
		return ret ;
	},
	
	_getExcerpt: function (){
		return Ext.util.Format.stripTags(this.attach.content).ellipse(90) ;
	},
		
	_getTags: function (){
		return coment.util.getTags(this.attach) ;
	},
	
	couldBeEdited: function(creationTime){
		var ret = false ;
		if (sv_remComPerm)
			ret = true ;
		else {
			if (sv_loggedIn && this.attach['username'] == sv_username && this.attach.state_id == sv_wrkf_initialstateid) {
				ret = (this.attach.discussion_count == 0) ; 
			}
		}
		return ret ;
	},
		
	toListItemPanel: function (){
		var discussion_count = this.computeNbRepliesMsg() ;
		var excerpt_txt = this._getExcerpt() ;
		var ad = coment.util.getAuthorAndDate(this.attach) ;
		/*var visRem = "displaynone" ;
		if ((sv_remComPerm) || (this.attach.discussion_count == 0 && sv_loggedIn && this.attach['username'] == sv_username && this.attach.state_id == sv_wrkf_initialstateid)) { 
			visRem = "" ;
		}*/
		var visRem = (this.couldBeEdited(true))?"":"displaynone" ;
		var visMan = (sv_so_b || sv_manageComPerm) ? "" : "displaynone" ;
		var viewReadBtn = ((excerpt_txt.length != this.attach.content.length)||(this.attach.discussion_count > 0)) ? "" : "displaynone" ;
		var viewReplyBtn = (sv_so_b) ? "displaynone" : "" ;
		var tags = this._getTags() ; 
		var com = _paneltpl.applyTemplate({ id: this._listid, 
											authordate:ad, 
											title: this.attach.title, 
											excerpt_text: excerpt_txt,
											comment_tags:tags, 
											text: this.attach.content, 
											delete_comment_tooltip :gettext("delete comment"),
											edit_comment_tooltip :gettext("edit comment"),
											vis_remclass :visRem , 
											vis_manclass :visMan , 
											change_wfstate_tooltip :gettext("click to change"),
											select_options :core.TextMgr.getStateOptions(),
											nbreplies: discussion_count,
											read:gettext("Read"),
											vis_readbtnclass:viewReadBtn , 
											vis_replybtnclass:viewReplyBtn , 
											reply:gettext("Reply"),
											minimize:gettext("Minimize"),
											current_state :core.TextMgr.getStateName(this.attach.state_id)});
		var pan = new Ext.Panel({
			id:this.getPanelId(),
			items:[{border:false, html:com}]
		}) ;

		return pan ;
	},
		
	refreshDiscussionItemCount : function(){
		var listElement = Ext.fly("comment_nbreplies-" + this._listid).update(this.computeNbRepliesMsg()) ;
	},

	activateMe : function(e){
		this._attachMgr._attachController.setActiveAttach(this) ;
	},

	deleteMe : function(e){
		if (!core.ServerExchange.callIsInProgress()) {
			if (confirm(gettext("Are you sure you want to delete this comment ?"))) {
				this._attachMgr.deleteAttach(this);
			}
		}
	},

	editMe : function(e){
		if (!core.ServerExchange.callIsInProgress()) {
			this._attachMgr.editAttach(this.attach.id, 0, 0, this.attach.title, this.attach.content, this.attach.tags);
		}
	},

// triggered when user clicks on the current comment state. Setup the select state choice.
	toStateChoice : function(e){
	
		var comment_wfstate = YAHOO.util.Dom.get('current_state-'+this._listid);
		var comment_wfstate_select = YAHOO.util.Dom.get('select_state-'+this._listid);
	
		this._attachMgr.toStateChoice(comment_wfstate, comment_wfstate_select, this.attach.state_id)
		//YAHOO.util.Event.stopPropagation(e);			
	},

	// triggered when user chooses a state. Setup the current state choice.
	toCurrentState : function(e){
		if (!core.ServerExchange.callIsInProgress()) {
			var comment_wfstate = YAHOO.util.Dom.get('current_state-' + this._listid);
			var comment_wfstate_select = YAHOO.util.Dom.get('select_state-' + this._listid);
			this._attachMgr.toCurrentState(comment_wfstate, comment_wfstate_select, this.attach.state_id, this.getId(), this._attachMgr.updateAttachState, this._attachMgr);
			//YAHOO.util.Event.stopPropagation(e);
		}			
	},
	
	// triggered when user chooses not to choose a state. 
	toNoState : function(e){
		var comment_wfstate = YAHOO.util.Dom.get('current_state-'+this._listid);
		var comment_wfstate_select = YAHOO.util.Dom.get('select_state-'+this._listid);
		this._attachMgr.switchSelect(comment_wfstate, comment_wfstate_select, true) ;
	
	},

    _onListOver : function(e, t){
		Ext.fly(this._panelid).addClass("selectAtt");
    },

    _onListOut : function(e, t){
		Ext.fly(this._panelid).removeClass("selectAtt");
    },

    _discsempty : function(){
		return Ext.fly("discs-" + this._listid).dom.innerHTML == "" ;
    },
	
    _emptydiscs: function(){
		Ext.fly("discs-" + this._listid).update("") ;
    },
	
    _isexpanded: function(){
		return Ext.fly("read-" + this._listid).hasClass("displaynone") ;
    },
	
    _read : function(doScroll){
		if (!core.ServerExchange.callIsInProgress()) {
			Ext.fly("read-" + this._listid).addClass("displaynone");
			Ext.fly("minimize-" + this._listid).removeClass("displaynone");
			
			Ext.fly("text-" + this._listid).removeClass("displaynone");
			Ext.fly("excerpt-" + this._listid).addClass("displaynone");
			
			Ext.fly("discs-" + this._listid).removeClass("displaynone");
			
			if (this._discsempty()) 
				this.getDiscussionItems((doScroll === true));
		}
    },
	
	getDiscussionItems : function(doScroll) {
		var returnFunc = (doScroll) ? this._getDiscussionItemsReturnsAndScroll : this._getDiscussionItemsReturns ;
		
		if (!sv_so_b) {		
			core.ServerExchange.send("getDiscussionItems",{'attachId':this.getId()},returnFunc, this, null, gettext("replies could not be retrieved")) ;
		}
		else {
			returnFunc.call(this, {"discussionItems" : so_dis_datas[this.getId()]}) ;
		}
	},
	
	_appendDiscussionItem : function(sdi) {
		var di = this._attachMgr._readDate(sdi) ;
		var ddi = new core.DiscussionItem(di, this._attachMgr) ;
		var diDom = ddi.toDom() ;
		// repeat this search each time important : .dom has changed !
		var discs = Ext.fly("discs-" + this._listid) ;
		discs.insertHtml('beforeEnd', diDom, false);
		ddi.connect();
		this._attachMgr._attachController.addDiscussionItem(ddi) ;
	},
	
	_getDiscussionItemsReturns : function(ret) {
		var discussionItems = ret['discussionItems'];
		for (var i = 0; i < discussionItems.length; i++) {
			this._appendDiscussionItem(discussionItems[i]);
		}
	},
	
	_getDiscussionItemsReturnsAndScroll : function(ret) {
		this._getDiscussionItemsReturns(ret) ;
		// now scroll :
		var p = Ext.ComponentMgr.get('attachsPanel').body;
		var discs = Ext.fly("discs-" + this._listid);
		if (discs) {
			var d = discs.last();
			var yOffset = d.getY() - (p.getY() - p.dom.scrollTop) - (p.getHeight() / 2); // - (p.getHeight() / 2) to have the top of reply in the middle
			p.scrollTo("top", yOffset, true);
		}
	},
	
	// when called with immediateLayoutUpdate == false there will be no connect call !
	addMe : function(immediateLayoutUpdate) {
		if (Ext.fly(this.getPanelId()) == null) {
			var asPanel = this.toListItemPanel();
			var parent = Ext.ComponentMgr.get('attachsPanel');
			parent.add(asPanel);
			if (immediateLayoutUpdate) {
				parent.doLayout();
				// only when rendered immediately do we connect 
				this.connect();
			}
		}
	},
	
	deleteReply : function(di) {
		Ext.fly("disc-" + di.getId()).remove() ;
		this.attach.discussion_count = this.attach.discussion_count - 1 ;
		this.refreshDiscussionItemCount() ;
	},
	
	refreshMe : function() {
		// updates only : title, content and tags
		var t = Ext.fly("comment_title-" + this._listid) ;
		if (t)
			t.update(this.attach.title) ;
		t = Ext.fly("excerpt-" + this._listid) ;
		if (t)
			t.update(this._getExcerpt()) ;
		t = Ext.fly("text-" + this._listid) ;
		if (t)
			t.update(this.attach.content) ;
		t = Ext.fly("comment_tags-" + this._listid) ;
		if (t)
			t.update(this._getTags()) ;
	},

	removeMe : function() {
		Ext.ComponentMgr.get('attachsPanel').remove(this._panelid) ;
	},

    _minimize : function(){
		Ext.fly("read-" + this._listid).removeClass("displaynone") ;
		Ext.fly("minimize-" + this._listid).addClass("displaynone") ;
		
		Ext.fly("text-" + this._listid).addClass("displaynone") ;
		Ext.fly("excerpt-" + this._listid).removeClass("displaynone") ;

		Ext.fly("discs-" + this._listid).addClass("displaynone") ;
    },

    _closereply : function(){
		Ext.fly("reply-" + this._listid).removeClass("displaynone") ;
		Ext.fly("replyform-" + this._listid).addClass("displaynone") ;
	},
		
    _reply : function(){
		Ext.fly("reply-" + this._listid).addClass("displaynone") ;

		var formlike = Ext.fly("replyform-" + this._listid) ;
		formlike.removeClass("displaynone") ;
		
		if (formlike.dom.innerHTML == "") {
			var com = _replyformtpl.applyTemplate({
				id:this._listid,
				tagslabel:gettext("Tags (comma separated)"),
				cook_name:core.User.getCookieAuthor(),
				cook_email:core.User.getCookieEMail(),
				authornamelabel:gettext("Name"),
				authoremaillabel:gettext("E-mail (will not be published)"),
				replytitle: gettext("Re:") + this.attach.title,
				replytitlelabel: gettext("Title (required)"),
				replytextlabel: gettext("Text (required)")
			}) ; 
			
			formlike.insertHtml('beforeEnd', com, false);
			
			var btn = new Ext.Button({
				id: "addreply-" + this._listid,
				renderTo: "applyreply-" + this._listid,
				text: gettext("add reply")
			});
			btn.on('click', this._addReplyBtnClick, this);
			btn = new Ext.Button({
				id: "canceladdreply-" + this._listid,
				renderTo: "cancelreply-" + this._listid,
				text: gettext("cancel")
			});
			btn.on('click', this._closereply, this);

			if (!sv_loggedIn) 
				Ext.fly("add_attach_user-" + this._listid).removeClass("displaynone");
		}
		
		Ext.ComponentMgr.get(this._panelid).doLayout() ;
		
		// now scroll :
		var p = Ext.ComponentMgr.get('attachsPanel').body ;
		var discs = Ext.fly("discs-" + this._listid) ;
		if (discs) {
			var d = Ext.fly("replyform-" + this._listid);
			var yOffset = d.getY() - (p.getY() - p.dom.scrollTop) - (p.getHeight() / 2); // - (p.getHeight() / 2) to have the top of reply in the middle
			p.scrollTo("top", yOffset, true);
		}		
    },

    _addReplyBtnClick : function(){
		if (!core.ServerExchange.callIsInProgress()) {
			var errors = this._validatereply();
			this._displayValidationErrors(errors);
			
			if (errors.length == 0) {
				var tags = {
					'tags': Ext.util.Format.trim(YAHOO.util.Dom.get("discuss_comment_tags-" + this._listid).value)
				};
				var done = core.ServerExchange.send("validateTags", tags, this._validateTagReturns, this);
			}
		}
	},
	
    _validateTagReturns : function(ret){
		if (ret != '') {
			this._displayValidationErrors([["discuss_comment_tags-" + this._listid, ret]]);
		}
		else {
			var author = "" ;
			var email = "" ;
			if (!sv_loggedIn) {
				author = YAHOO.util.Dom.get('discuss_author-'+this._listid).value ;
				email = YAHOO.util.Dom.get('discuss_email-'+this._listid).value ;
			   	core.User.record(author, email) ;
			}
			
			var di = { 
			'comment_id':this.getId(),
			'username':author,
			'email':email,
			'title':YAHOO.util.Dom.get("discuss_comment_title-"+this._listid).value,
			'content':YAHOO.util.Dom.get("discuss_comment_text-"+this._listid).value,
			'tags': YAHOO.util.Dom.get("discuss_comment_tags-"+this._listid).value} ;
			
			var done = core.ServerExchange.send("addDiscussionItem", di, this._addDiscussionItemReturns, this, gettext("reply added"), gettext("reply could not be added")) ;
		}
	},
	
	_addDiscussionItemReturns : function(discussionItem){
		// when in here reply has been added for real serverside, update the discussion count :
		this.attach.discussion_count = this.attach.discussion_count + 1;
		this.refreshDiscussionItemCount();
		
		this._cleanDiscussionItemFields();
		this._closereply();
		
		if (discussionItem == null) 
			alert(gettext("Thank you for your reply. It is being held for moderation."));
		else {
			if (!this._discsempty() && this._isexpanded()) {
				this._appendDiscussionItem(discussionItem);
				
				var di = this._attachMgr._attachController.getDiscussionItem(discussionItem.id) ;
				var diElt = Ext.get(di.getDispId()) ;
				if (diElt) {
					var previousreplyElt = diElt.prev('.disp_discussionitem', false) ;
					this._attachMgr.setEditability(previousreplyElt) ;
				}
			}
			else {
				this._emptydiscs();
				this._read(true);
			}
			
			this._attachMgr.setEditability(Ext.get(this._listid)) ;
			
			this._attachMgr.populateTagCloud() ;
		}
	},
		
    _validatereply : function(){
		//_attachMgr._save, this.attachMgr);
		
		this._cleanFormErrors() ;
		var errors = [] ;
		//this._attachMgr.validateAuthor(YAHOO.util.Dom.get('discuss_author-'+this._listid), YAHOO.util.Dom.get('discuss_email-'+this._listid), errors) ;
		this._attachMgr.validateComment(YAHOO.util.Dom.get('discuss_comment_title-'+this._listid), YAHOO.util.Dom.get('discuss_comment_text-'+this._listid), errors) ;
		return errors ;
    },
	
	_cleanFormErrors : function(){
		// clean previous error messages
		var errorNodes = YAHOO.util.Dom.getElementsByClassName('field_error', 'div', this._listid);
		for (var i = 0;i < errorNodes.length; i ++)  {
			coment.util.displayYesNo(errorNodes[i], false) ;
		}
	},
	
	_displayValidationErrors : function(errors){
		// display errors
		for (var i = 0 ; i < errors.length ; i++) {
			Ext.fly("error_" + errors[i][0]).update(errors[i][1]) ;
			Ext.fly("error_" + errors[i][0]).removeClass("displaynone") ;
		}
	},

    connect : function(){
		if (!sv_so_b) {
			Ext.fly("delete-" + this._listid).on("click", this.deleteMe, this) ;
			Ext.fly("edit-" + this._listid).on("click", this.editMe, this) ;
			Ext.fly("reply-" + this._listid).on("click", this._reply, this) ;
			Ext.fly("current_state-" + this._listid).on("click", this.toStateChoice, this) ;
			Ext.fly("select_state-" + this._listid).on("change", this.toCurrentState, this) ;
			Ext.fly("select_state-" + this._listid).on("blur", this.toNoState, this) ;
		}
		Ext.fly("read-" + this._listid).on("click", this._read, this) ;
		Ext.fly("minimize-" + this._listid).on("click", this._minimize, this) ;
		Ext.fly(this._listid).on("click", this.activateMe, this) ;
		Ext.fly(this._listid).on("mouseover", this._onListOver, this) ;
		Ext.fly(this._listid).on("mouseout", this._onListOut, this) ;

    },

	_cleanDiscussionItemFields : function() {
		YAHOO.util.Dom.get('discuss_comment_title-'+this._listid).value = "" ;
		YAHOO.util.Dom.get('discuss_comment_text-'+this._listid).value = "" ;
		YAHOO.util.Dom.get('discuss_comment_tags-'+this._listid).value = "" ;
	}
	
}

