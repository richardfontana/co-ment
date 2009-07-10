if (!core.SelectionMgr) {
    core.SelectionMgr = new function() {

		this._fromWord = null ;
		this._toWord = null ;
	
		this._lastSelection = "" ;
	
		this.cachedSelectedColors = {} ;
			
		this.clearSelection = function(){
			if (YAHOO.util.Event.isIE) {
				var doc = coment.util.getTextDocument();
				doc.selection.empty();
			}
			else {
				var win = coment.util.getTextWindow();
				var selected = win.getSelection();
				if (selected) 
					selected.removeAllRanges();
			}					
		};
	
		this.init = function () {
			if (coment.cst.framed) {
				// although the event we are interested in is the mouseup in frame, it is of course not triggered
				// when the mousedown happened in the frame and the mouseup out of the frame.
				// We need to catch the mouseup on the out of frame document.
				YAHOO.util.Event.addListener(document, "mouseup", this.onRetrieveSelection, this, true);
				// note : the rest of the event listeners are added directly from inside the iframe
			}
			else {
				YAHOO.util.Event.addListener(window, "keyup", this.onRetrieveSelection, this, true);
				var panel = YAHOO.util.Dom.get(coment.cst.textNodeId).parentNode.parentNode;
				YAHOO.util.Event.addListener(panel, "mouseup", this.onRetrieveSelection, this, true);
			}
		};
	
	
		// returns an array : [[attid of selection start, attid of selection end], text]
		this._getSelection = function () {
			var ret = [] ;
			var text = "" ;
			var maxLength = coment.cst.maxSelectedTxtLength ;
		 	var msg = interpolate(gettext("Selected text is too long (selection is limited to %(count)s characters). \nPlease retry."), {count:maxLength}, true) ;
			var doc = coment.util.getTextDocument() ;
			var win = coment.util.getTextWindow() ;
			
			if (YAHOO.util.Event.isIE) {
				var r = doc.selection.createRange() ;
				var selectedText = r.text ;					
				if ((selectedText.length > 0)) {
					// check text length because of performance issues
					if (selectedText.length > maxLength) 
						alert(msg) ;
					else {
						var selected = r.htmlText ;
						// TODO : move regexp (instanciate only once)
						var reg = new RegExp("id=" + coment.cst.textWordIdPref, "i") ;
						if (!reg.test(selected)) { // a letter or part of inside of the span
							var word = coment.util.fromMarkerIdToWord(r.parentElement().id) ;
							ret = [word, word] ;
						}
						else {
							var arr = selected.split(reg) ;
							
							var startIndex = 1 ;
							if (arr.length > 1) {
								var u = arr[1].indexOf(">") ;	// should be the one that ends the open span tag 
								var v = arr[1].lastIndexOf("</") ; // should be the one that starts the close span tag
								var firstSpanContent = arr[1].substring(u + 1, v) ;
					
								var realFirstSpanContent = doc.getElementById(coment.util.fromWordToMarkerId(parseInt(arr[1]))).innerHTML ;
					
								// why why firstSpanContent != realFirstSpanContent ? because of an isolated ? for example
								if ((firstSpanContent != realFirstSpanContent) && coment.util.containsSeparatorsOnly(firstSpanContent))
									startIndex = 2 ;
							}
							
							for (var i = startIndex ; i < arr.length ; i++) {
								var id = parseInt(arr[i]) ;
								if (id > -1) {
									ret.push(id) ; 
									break ;
								}	
							}
							
							for (var i = arr.length - 1 ; i > startIndex-1  ; i--) {
								var id = parseInt(arr[i]) ;
								if (id > -1) {
									ret.push(id) ; 
									break ;
								}	
							}
						}
					}
				}
			}
			else {	// cf. http://www.quirksmode.org/dom/range_intro.html
				var selected = null ;
				if (win.getSelection) 
					selected = win.getSelection() ;
				else if (doc.selection)  // should come last; Opera!
					selected = doc.selection.createRange();
				if (selected) {
					var selectedText = selected.toString() ;					
					if (selectedText.length > 0) {// && selectedText != this._lastSelection) {
	//					this._lastSelection = selectedText ; 
						
						// check text length because of performance issues
						if (selectedText.length > maxLength) {
							alert(msg)  ;
	//						this._lastSelection = win.getSelection().getRangeAt(0).toString() ; // save it again because selection might have changed under FF
						}
						else {
							var range = selected.getRangeAt(0) ;
		
							var startTextNode = range.startContainer ;
							var endTextNode = range.endContainer ;
							
							var startNode = startTextNode.parentNode ;
							var endNode = endTextNode.parentNode ;
							
							if (startNode.tagName.toUpperCase() == 'SPAN' && startNode.id && (startNode.id.indexOf("w_") == 0) && endNode.tagName.toUpperCase() == 'SPAN' && endNode.id && (endNode.id.indexOf("w_") == 0)) { 
								ret = [coment.util.fromMarkerIdToWord(startNode.id), coment.util.fromMarkerIdToWord(endNode.id)] ;
								
								/* it might happen that 'firefox range selection' starts at the end of the preceding 'word' 
								 * this code will check such situation for the start and the end of the selection 
								 * (when one word is selected this happens)
								 */ 
								var s =  coment.util.fromMarkerIdToWord(startNode.id) ;
	
								var r = doc.createRange();
								r.selectNode(doc.getElementById(startNode.id));
								r.setStart(range.startContainer, range.startOffset) ;
								
								if (r.toString() == "")
									ret[0] = ret[0] + 1 ;
								r.detach() ;
								
								var r = doc.createRange();
								r.selectNode(doc.getElementById(endNode.id));
								r.setEnd(range.endContainer, range.endOffset) ;
								
								if (r.toString() == "" && ret[1] > ret[0])
									ret[1] = ret[1] - 1 ;
								r.detach() ;
								
							}
						}
					}
				}
			}
			
			for (var i = ret[0] ; i < ret[1] + 1 ; i++) 
				text = text + doc.getElementById(coment.util.fromWordToMarkerId(i)).innerHTML ;
 
			return [ret, text] ;
			
		};
		
		this._previewSelectionInAddAttachPanel = function (text) {
			var maxLength = coment.cst.currentSelDispLength ;
			var textLength = text.length ;
			var current_sel = YAHOO.util.Dom.get("current_sel") ;
			var edit_current_sel = YAHOO.util.Dom.get("edit_current_sel") ;
			if (textLength <= maxLength) {
				current_sel.innerHTML = text ;
				if (edit_current_sel)
					edit_current_sel.innerHTML = text ;
			}
			else {
				var sep = "[...]" ;
				var midMaxLength = ( maxLength - sep.length ) / 2 ;
				
				var s_start = text.substring(0, midMaxLength) ;
				var l = s_start.lastIndexOf(" ") ;
				if (l != -1 && l < midMaxLength - 1)
					s_start = s_start.substring(0, l + 1) ;
	
				var s_end = text.substring(text.length - midMaxLength) ;
				var l = s_end.indexOf(" ") ;
				if (l != -1 && l > 0)
					s_end = s_end.substring(l) ;
				
				current_sel.innerHTML = s_start + sep + s_end ;
				if (edit_current_sel)
					edit_current_sel.innerHTML = s_start + sep + s_end ;
			}
		};

		this.getSelectionFromWord = function () {
			return this._fromWord ;	
		};
		
		this.getSelectionToWord = function () {
			return this._toWord ;	
		};
		
		this.onRetrieveSelection = function (text) {
			if (sv_addComPerm) {
				var out = this._getSelection();
				if (out[0].length == 2) {
					this._fromWord = out[0][0];
					this._toWord = out[0][1];
					
					this._previewSelectionInAddAttachPanel(out[1]);
					//this._previewSelectionInText(this._fromWord, this._toWord) ;
					
					//core.LayoutMgr.removeSelectionHelpMessage();
				}
			}
		};
	};
}

