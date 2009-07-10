//global 
so_dis_datas = null ;

// core.TextMgr._attachMgr
core.CommentAttachMgr = function(attachController){
    this._attachController = attachController;
	this._cacheColoredIds = {} ;
};

core.CommentAttachMgr.prototype = {
	onFilterMgrApply : function(type, args, me) {
		me.clear() ;
	},
	
	_impCleanAttachFields : function() {
		YAHOO.util.Dom.get("edit_current_sel").innerHTML = core.LayoutMgr.getInitialSelectionContent() ; 
		YAHOO.util.Dom.get("current_sel").innerHTML = core.LayoutMgr.getInitialSelectionContent() ; 
		YAHOO.util.Dom.get("add_comment_title").value = "" ;
		YAHOO.util.Dom.get("add_comment_text").value  = "" ;
		YAHOO.util.Dom.get("add_comment_tags").value  = "" ;
	},
	
	// override
	_impGetAddAttachDoneMsg : function() {
	},
	
	_addAttach : function(sAttach, immediateLayoutUpdate) {
		// add to the list
		var a = new core.Attach(sAttach, this) ;
		a.addMe(immediateLayoutUpdate) ;
		this._attachController.addAttach(a) ;
	},
	
	_readDate : function(entity) {
		entity.created = coment.util.dateFromString(entity.created) ;
		return entity ;
	},
	
	updateAttachCount : function() {
		var count = Ext.ComponentMgr.get('attachsPanel').items.length ;
		core.LayoutMgr.updatePanelTitle('attachsPanel', gettext("List") + " (" + count +")") ;
	},
	
	_retrieveAttachsReturns : function(ret){
		var attachs = ret['attachs'] ;
		// be sure to draw the last one only
		for (var i = 0 ; i < attachs.length ; i++) {
			var immediateLayoutUpdate = (i == (attachs.length - 1)) ;
			this._addAttach(this._readDate(attachs[i]), immediateLayoutUpdate) ;
		}
		// still have to connect events on the previous ones :
		for (var i = 0 ; i < attachs.length - 1 ; i++) {
			this._attachController.getAttach(attachs[i].id).connect() ;
		}
    	Ext.ComponentMgr.get('attachsregion').el.unmask();
	},
		
	updateAttachState : function(attachId, stateId) {
		var done = core.ServerExchange.send("updateAttachState",{
			'comment_id': attachId, 'state_id':stateId
		},this.updateAttachStateReturns, this, gettext("comment state changed"), gettext("comment state could not be changed")) ;
	},
	
	updateAttachStateReturns : function(ret) {
		this._attachController.updateAttach(this._readDate(ret['attach'])) ;
	},
	
	updateDiscussionItemState : function(diId, stateId) {
		var done = core.ServerExchange.send("updateDiscussionItemState",{
			'discussionitem_id': diId, 'state_id':stateId
		},this.updateDiscussionItemStateReturns, this, gettext("reply state changed"), gettext("reply state could not be changed")) ;
	},
	
	updateDiscussionItemStateReturns : function(ret) {
		this._attachController.updateDiscussionItem(this._readDate(ret['discussionitem'])) ;
	},
	
	_retrieveAttachs : function(word) {
		var obj = core.FilterMgr.getCachedFilterData() ;
		obj.word = word ;
		if (!sv_so_b) {
			var done = core.ServerExchange.send("getAttachsOnWord", obj, this._retrieveAttachsReturns, this, null, gettext("comments could not be retrieved")) ;
		}
		else { 
			var as = [] ;
			var js_datas = Ext.util.JSON.decode(this.so_json_datas) ;
			for (var i = 0 ; i < js_datas['attachs'].length ; i++) {
				var cand = js_datas['attachs'][i]
				if ( cand.start_word <= word && cand.end_word >= word ) { 
					as.push(cand) ;
				}
			}
			this._retrieveAttachsReturns({'attachs':as}) ;
		}
	},
	
	// it all ends up in this function when rendering occurences 
	// lets try to use slocum's getEl function (cause ext elements are cached)
	_colorizeNode	 : function(markerId, color){
		//var node = YAHOO.util.Dom.get(markerId) ;
		var node = util.getElt(markerId) ;
		
		// about to be colored
		if (color != null) {
			if (this._cacheColoredIds[markerId] != color) {

				this._cacheColoredIds[markerId] = color ;

				node.setStyle('background-color', color) ;
				node.setStyle('cursor', 'pointer') ;
			}
		}
		else { // about to be erased
			if (this._cacheColoredIds[markerId]) {

				delete this._cacheColoredIds[markerId] ;

				node.setStyle('background-color', '') ;
				node.setStyle('cursor', '') ;
			}
		}
	},
		
	_color : function(infos, allatonce){
		var infoKeys = [] ;
		for (var inf in infos) {
			infoKeys[infoKeys.length] = inf ;
		}
		
		var me = this;
		var i = 0 ;
	    var fun = function() {
			while (i < infoKeys.length) {
			
				var markerId = infoKeys[i] ;
				var colorEstimate = infos[markerId] ;
				
				me._colorizeNode(markerId, colorEstimate) ;
				++i ;
	            if((!allatonce) && ( (i % coment.cst.colorizePacketSize) == 0)) {
	                window.setTimeout(fun, coment.cst.colorizePaintTimeout);
	                break;
	            }
			}
			/* these next 3 lines have been added to handle the case of the edit of a comment */
    		if (i == infoKeys.length) {
    			me._attachController._showAttachTextPart(me._attachController._activeAttach, true) ;
    		}
	    }
	    fun() ;
	},
	    
	_colorizeOccurences : function(from, to, occs){

		var infos = {} ;
		
		// I gather infos :
		
		// I.1 BLANK 
		if (from == -1) { // all, use the cache to do that quick
			for (markerId in this._cacheColoredIds) {
				infos[markerId] = null ;
			}
		}
		else {
			for (var word = from; word <= to ; word ++) {
				var markerId = coment.util.fromWordToMarkerId(word) ;
				infos[markerId] = null ;
			}
		}
		
		// I.2 COLORIZE
		
		for (var i = 0 ; i < occs.length ; i++ ) {
			var occ = occs[i] ;
			var colorEstimate = coment.util.testColorFunction1(occ.nbWord) ;
			for (var word = occ.startWord; word <= occ.endWord ; word ++) {
				var markerId = coment.util.fromWordToMarkerId(word) ;
				infos[markerId] = colorEstimate ;
			}
		}
		
		// II do it :
		this._color(infos) ;
	},

	populateTagCloud : function(){
		if (!sv_so_b) {
			var done = core.ServerExchange.send("getTagCloud", {}, this._populateTagCloudReturns, this, null, gettext("tag cloud could not be retrieved")) ;
		}
		else { 
			this._populateTagCloudReturns(Ext.util.JSON.decode(this.so_json_datas)) ;
		}
	},
	
	_populateTagCloudReturns : function(ret){
		var tags = ret['tags'] ;
		var content = "" ;
		for (var i = 0 ; i < tags.length ; i++) {
			var tag = tags[i] ;
			content = content + "<span id = 'tag-" + tag.id + "' class='tagsize" + tag.font_size + "'>"  + tag.name + "</span>&nbsp; " ;
		}
		if (content == "")
			content = gettext("no comment has been tagged yet") ;
			
		Ext.ComponentMgr.get('tagcloud').body.update(content) ;
		core.LayoutMgr.doLayout() ;
	},
	
	tagclicked : function(evt){
		var target = YAHOO.util.Event.getTarget(evt);
		if (target && target.id.indexOf("tag-") == 0) {
			var tagid = target.id.substring(4) ;
			core.FilterMgr.applytagbtnclick(tagid) ;
		}
	},

	_retrieveOccsReturns : function(ret){
    	//Ext.ComponentMgr.get('text_frame').el.unmask();
	
		var from = ret['fromWord'] ;
		var to = ret['toWord'] ;
		var occs = ret['occs'] ;
		// immediately render colours
		this._colorizeOccurences(from, to, occs) ;
		
		// in the case of a filter apply we'll display all comments in the list
		this._retrieveAttachsReturns(ret) ;
	    //core.LayoutMgr.updateInitialLoading() ;
	},
	
	// retrieve attachs from server
	_retrieveOccs : function(from, to){
		var obj = core.FilterMgr.getCachedFilterData() ;
		obj.fromWord = from ;
		obj.toWord = to ;
		if (!sv_so_b) {
			var done = core.ServerExchange.send("getOccs", obj, this._retrieveOccsReturns, this, null, gettext("comments could not be retrieved")) ;
		}
		else {
			if (from != -1)
				alert('OHHHHHHHHHHHHH from != -1') ;// TODOTOUDOU VIRER $$$ 
			this.so_json_datas = coment.util.getElt("so_datas").dom.innerHTML;
//			alert(this.so_json_datas) ;
			// apply filter client side :
			var js_datas = Ext.util.JSON.decode(this.so_json_datas) ;
			so_dis_datas = js_datas["discussionItems"] ;
			var tags = js_datas["tags"] ;
			var filteredComments = core.So_Computation.so_filter(obj, js_datas['attachs'], so_dis_datas, tags) ; 
			
			// compute new occs
			var filteredOccs = core.So_Computation.so_computeOccs(filteredComments) ; 
			
			js_datas['attachs'] = filteredComments ;
			js_datas['occs'] = filteredOccs ;
			
			this._retrieveOccsReturns(js_datas) ;
		}
	},
	
	renderOccurences : function(){
		//alert('about');
		Ext.ComponentMgr.get('attachsregion').el.mask(Ext.get('loadingindicatormsg').dom.innerHTML,"x-mask-loading");
		this._retrieveOccs(-1, -1) ;
	},

	clear : function(markerId, evt) {
		var attachs = this._attachController.getAttachs();
		for (var id in attachs) {
			var attach = attachs[id];
			this._attachController.removeAttach(attach);
			attach.removeMe() ;
		}
	},
	
	occClick : function(markerId, evt) {
		if (this._cacheColoredIds[markerId]) {
			Ext.ComponentMgr.get('attachsregion').expand() ;	
			this.clear() ;
			core.LayoutMgr.activateAttachListTab() ;
						
			var word = coment.util.fromMarkerIdToWord(markerId) ;
			// retrieve attach from server
			this._retrieveAttachs(word) ;
			YAHOO.util.Event.preventDefault(evt) ;
		}
	},
	
	_getFormFieldValue : function(name){
		var ret = null ;		
		var node = YAHOO.util.Dom.get(name) ;
		if (node)	
			ret = node.value ; 
		return ret ;
	},

// length are not checked yet !!
// use coment.util.checkLength
	validateAuthor : function(authorNode, emailNode, errors){
		if (!sv_loggedIn) { // NOT LOGGED IN
			var author = authorNode.value ;
			if (!coment.util.checkNonEmpty(author)) 
				errors[errors.length] = [authorNode.id, gettext("field is required")] ;
			var email = emailNode.value.toLowerCase() ;
			if (!coment.util.checkEmail(email)) 
				errors[errors.length] = [emailNode.id, gettext("email is invalid")] ;
		}
	},

	_clientValidateSelection : function(errors, id){
			var selection = YAHOO.util.Dom.get(id).innerHTML ;
			if (selection == core.LayoutMgr.getInitialSelectionContent()) 
				errors[errors.length] = [id, gettext("Select the part you wish to comment in the text diplayed on the right")] ;
	},

	validateComment : function(titleNode, textNode, errors){
		var comment_title = titleNode.value ;
		if (!coment.util.checkNonEmpty(comment_title)) 
				errors[errors.length] =[titleNode.id, gettext("field is required")] ;
		
		var comment_text = textNode.value ;
		if (!coment.util.checkNonEmpty(comment_text)) 
				errors[errors.length] = [textNode.id, gettext("field is required")] ;
				
		return errors ;
	},
	
	_saveAttachReturns : function(ret){
		this._impCleanAttachFields();
		if (ret == null) {
			alert(gettext("Thank you for your comment. It is being held for moderation."));
		}
		else {
			var attach = ret;
			this._retrieveOccs(attach.start_word, attach.end_word);
			
			// now we add the comment in the list
			this.clear();
			core.LayoutMgr.activateAttachListTab();
			this._addAttach(this._readDate(attach), true);
			this.populateTagCloud() ;
		}
	},
	
	// doesn't take into account wether tab is hidden
	_getCurrentEditAttachId: function()  {
		return YAHOO.util.Dom.get("edit_attach_id").value ;
	},
	
	_getCurrentEditDIId: function()  {
		return YAHOO.util.Dom.get("edit_di_id").value ;
	},
	
	_getCurrentEditIsReply: function()  {
		return YAHOO.util.Dom.get("edit_is_reply").value ;
	},
	
	_validateTagReturnsFromEdit : function(ret){
		if (ret != '') {
			this._displayFormErrors([['add_comment_tags', ret]]);
		}
		else {
			var isReply = this._getCurrentEditIsReply() ; // danger could be changed by the time the validation returns ....
			var attachId = this._getCurrentEditAttachId() ;
			var start_word = -1 ;
			var end_word = -1 ;
			if (isReply == 1)
				attachId = this._getCurrentEditDIId() ;
			else if (Ext.fly('edit_modif_scope').dom.checked) {
				start_word = core.SelectionMgr.getSelectionFromWord() ;
				end_word = core.SelectionMgr.getSelectionToWord() ;
			}
			
			var title = YAHOO.util.Dom.get("edit_comment_title").value ;
			var content = YAHOO.util.Dom.get("edit_comment_text").value ;
			var tags = Ext.util.Format.trim(YAHOO.util.Dom.get("edit_comment_tags").value) ;
			var done = core.ServerExchange.send("editAttach",{
				'comment_id': attachId, 'is_reply': isReply, 'title':title, 'content':content, 'start_word':start_word, 'end_word':end_word, 'tags':tags
			},this.editAttachReturns, this, gettext("comment changed"), gettext("comment could not be changed")) ;
		}
	},
	
	_validateTagReturnsFromAdd : function(ret){
		if (ret != '') {
			this._displayFormErrors([['add_comment_tags', ret]]);
		}
		else {
			var author = "";
			var email = "";
			if (!sv_loggedIn) {
				author = Ext.util.Format.trim(this._getFormFieldValue("add_author"));
				email = Ext.util.Format.trim(this._getFormFieldValue("add_email"));
				core.User.record(author, email);
			}
			
			var attach = {
				'title': YAHOO.util.Dom.get("add_comment_title").value,
				'content': YAHOO.util.Dom.get("add_comment_text").value,
				'tags': Ext.util.Format.trim(YAHOO.util.Dom.get("add_comment_tags").value),
				'start_word': core.SelectionMgr.getSelectionFromWord(),
				'end_word': core.SelectionMgr.getSelectionToWord(),
				'username': author,
				'email': email
			};
			var done = core.ServerExchange.send("addAttach", attach, this._saveAttachReturns, this, gettext("comment added"), gettext("comment could not be added"));
		}
	},
	
	_displayFormErrors : function(errors){
		// display errors
		for (var i = 0 ; i < errors.length ; i++) {
			var node = YAHOO.util.Dom.get("error_" + errors[i][0]) ;
			node.innerHTML = errors[i][1] ;
			coment.util.displayYesNo(node, true) ;
		}
	},
	
	_cleanFormErrors : function(topelt){
		// clean previous error messages
		var errorNodes = YAHOO.util.Dom.getElementsByClassName('field_error', 'div', topelt);
		for (var i = 0;i < errorNodes.length; i ++)  {
			coment.util.displayYesNo(errorNodes[i], false) ;
		}
	},
	
	editAttach : function(attach_id, di_id, replyYesNo, title, content, tags) {
		core.LayoutMgr.unhideEditAttachTab() ;
		this._cleanFormErrors("edit_attach_top") ;
		
		Ext.fly('edit_modif_scope').dom.checked = false ;
		this.editAttachModifScopeClick() ;
		
		YAHOO.util.Dom.get("edit_attach_id").value = attach_id;
		YAHOO.util.Dom.get("edit_di_id").value = di_id;
		YAHOO.util.Dom.get("edit_is_reply").value = replyYesNo;
		
		if (replyYesNo == 1)
			Ext.fly('edit_attach_sel').addClass('displaynone'); 
		else 
			Ext.fly('edit_attach_sel').removeClass('displaynone'); 

		YAHOO.util.Dom.get("edit_comment_title").value = title;
		YAHOO.util.Dom.get("edit_comment_text").value = content;
		YAHOO.util.Dom.get("edit_comment_tags").value = tags;
	},
	
	editAttachReturns : function(ret) {
		// back from the server, the comment/reply could possibly still be displayed in the comment list
		if (ret['attach']) {
			YAHOO.util.Dom.get("edit_current_sel").innerHTML = core.LayoutMgr.getInitialSelectionContent() ; 
			YAHOO.util.Dom.get("current_sel").innerHTML = core.LayoutMgr.getInitialSelectionContent() ; 
			var attach = this._readDate(ret['attach']) ;
			var prev_start_word = -1 ;
			var prev_end_word = -1 ;
			var previous_a = this._attachController.getAttach(attach.id)
			if (previous_a) {
				prev_start_word = previous_a.getStartWord() ;
				prev_end_word = previous_a.getEndWord() ;
			}
			this._attachController._showAttachTextPart(this._attachController._activeAttach, false) ;
			this._attachController.updateAttach(attach) ;
			var a = this._attachController.getAttach(attach.id) ;
			if (a) {
				// if the comment/reply is still displayed in the comment list, update its title, content and tags 
				a.refreshMe() ;
				
				if (prev_start_word != -1) {
					var start_word = a.getStartWord() ;
					var end_word = a.getEndWord() ;
					this._retrieveOccs(Math.min(prev_start_word, start_word), Math.max(prev_end_word, end_word)) ;
				}
			} 
		}
		if (ret['discussionitem']) {
			var di = this._readDate(ret['discussionitem']) ;
			this._attachController.updateDiscussionItem(di) ;
			var d = this._attachController.getDiscussionItem(di.id) ;
			if (d)
				d.refreshMe() ;
		}
		
		core.LayoutMgr.hideEditAttachTab() ;

		this.populateTagCloud() ;
	},
	
	editAttachModifScopeClick : function(){
		if (Ext.fly('edit_modif_scope').dom.checked) {
			Ext.fly("edit_current_sel").removeClass("displaynone") ;
			Ext.fly("edit_help_current_sel").removeClass("displaynone") ;
		}
		else {
			Ext.fly("edit_current_sel").addClass("displaynone") ;
			Ext.fly("edit_help_current_sel").addClass("displaynone") ;
		}
	},
	
	editAttachButtonClick : function(){
		core.SelectionMgr.clearSelection() ; 
		
		this._cleanFormErrors("edit_attach_top") ;
		
		var errors = [] ;
		if (Ext.fly('edit_modif_scope').dom.checked) 
			this._clientValidateSelection(errors, "edit_current_sel") ;
		 
		this.validateComment(YAHOO.util.Dom.get("edit_comment_title"), YAHOO.util.Dom.get("edit_comment_text"), errors) ;
		if (errors.length) 
			this._displayFormErrors(errors); 
		else { 
			var tagsvalue = Ext.util.Format.trim(YAHOO.util.Dom.get("edit_comment_tags").value) ;
			var done = core.ServerExchange.send("validateTags", {'tags': tagsvalue}, this._validateTagReturnsFromEdit, this);
		}
	},
	
	editCancelAttachButtonClick : function(){
		core.LayoutMgr.hideEditAttachTab() ;
	},
	
	addAttachButtonClick : function(){
		core.SelectionMgr.clearSelection() ;
		//core.LayoutMgr.removeSelectionHelpMessage() ;
		this._cleanFormErrors("add_attach_top") ;
		var errors = [] ;
		// we decided name and email would not be required anymore
		// this.validateAuthor(YAHOO.util.Dom.get('add_author'), YAHOO.util.Dom.get('add_email'), errors) ;
		this._clientValidateSelection(errors, "current_sel") ; 

		this.validateComment(YAHOO.util.Dom.get("add_comment_title"), YAHOO.util.Dom.get("add_comment_text"), errors) ;
		
		if (errors.length) 
			this._displayFormErrors(errors); 
		else { 
			var tagsvalue = Ext.util.Format.trim(YAHOO.util.Dom.get("add_comment_tags").value) ;
			var done = core.ServerExchange.send("validateTags", {'tags': tagsvalue}, this._validateTagReturnsFromAdd, this);
		}
	},
	
	deleteAttachReturns : function(ret) {
		var attachId = ret['attachId'] ;
		
		// close edit tab if necessary
		var editAttachId = this._getCurrentEditAttachId() ;
		if ((editAttachId == attachId))
			core.LayoutMgr.hideEditAttachTab() ;
		
		var attach = this._attachController.getAttach(attachId) ;
		if (attach) {
			this._retrieveOccs(attach.getStartWord(), attach.getEndWord());
			this._attachController.removeAttach(attach) ;
			attach.removeMe() ;
		}
		this.populateTagCloud() ;
	},
	
	deleteAttach : function(attach) {
		var done = core.ServerExchange.send("deleteAttach",{
			'comment_id': attach.getId()
		},this.deleteAttachReturns, this, gettext("comment deleted"), gettext("comment could not be deleted")) ;
	},
	
	setEditability : function(previousElt) {
		var previous = null ;
		var id = null ;
		if (previousElt) {
			if (previousElt.hasClass("disp_discussionitem")) { // di
				var previousid = previousElt.id.substr("disc-".length) ;
				previous = this._attachController.getDiscussionItem(previousid) ;
				id = previous.getDispId() ;
			}
			else { // comment
				var previousid = previousElt.id.substr("comment-".length) ;
				previous = this._attachController.getAttach(previousid) ;
				id = previous.getListId() ;
			}
		}
		if (previous != null && id != null) {
			if (previous.couldBeEdited(false)) {
				Ext.get("delete-"+id).removeClass("displaynone") ;
				Ext.get("edit-"+id).removeClass("displaynone") ;
			}
			else { 
				Ext.get("delete-"+id).addClass("displaynone") ;
				Ext.get("edit-"+id).addClass("displaynone") ;
			}
		}
	},
	
	deleteDiscussionItemReturns : function(ret) {
		var discussionItemId = ret['discussionItemId'] ;
		
		// close edit tab if necessary
		var editDIId = this._getCurrentEditDIId() ;
		if ((editDIId == discussionItemId))
			core.LayoutMgr.hideEditAttachTab() ;
		
		var di = this._attachController.getDiscussionItem(discussionItemId) ;
		if (di) {
			var parentAttachId = di.getParentAttachId();
			var previousreply = null ;
			var diElt = Ext.get(di.getDispId()) ;
			if (diElt)
				previousElt = diElt.prev('.disp_discussionitem', false) ;
			if (previousElt == null) 
				previousElt = diElt.findParent('.disp_comment', 10, true) ;
			var comment = this._attachController.getAttach(parentAttachId) ;
			if (comment)
				comment.deleteReply(di) ;
			this._attachController.removeDiscussionItem(discussionItemId);
			this.setEditability(previousElt) ;
		}
	},
	
	deleteDiscussionItem : function(di) {
		var done = core.ServerExchange.send("deleteDiscussionItem",{
			'discussionitem_id': di.getId()
		},this.deleteDiscussionItemReturns, this, gettext("reply deleted"), gettext("could not delete reply")) ;
	},

	// triggered when user clicks on the current comment state. Setup the select state choice.
	switchSelect : function(stateDisp, stateSelector, b){
		coment.util.displayYesNo(stateDisp, b) ;
		coment.util.displayYesNo(stateSelector, !b) ;
	}, 
	
	toStateChoice : function(stateDisp, stateSelector, stateId){
		
		stateSelector.selectedIndex = 0 ;
		for (var i = 0 ; i < stateSelector.options.length ; i++) {
			if (stateSelector.options[i].value == stateId) {
				stateSelector.selectedIndex = i ;
				break ;
			}
		}
	
		this.switchSelect(stateDisp, stateSelector, false) ;
	},
	
	// triggered when user chooses a state. Setup the current state choice.
	toCurrentState : function(stateDisp, stateSelector, stateId, id, fun, me){
		// interface
		stateDisp.innerHTML = stateSelector.options[stateSelector.selectedIndex].innerHTML ;
		
		this.switchSelect(stateDisp, stateSelector, true) ;
	
		var newStateId = stateSelector.options[stateSelector.selectedIndex].value ;
		if (stateId != newStateId) { 
			// real work
			//this.updateAttachState(id, newStateId) ;
			fun.call(me, id, newStateId) ;
			
		}
	}
};
