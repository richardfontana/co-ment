if (!core.So_Computation) {
    core.So_Computation = new function() {
		this.so_computeOccs = function(commentsArr) {
			var max = 0 ; 
			for (var j = 0 ; j < commentsArr.length ; j++) {
				if (max < commentsArr[j].end_word) {
					max = commentsArr[j].end_word ;
				}
			}
			max = max + 2 ; // security 

			// 1 initialize an array having the size of the text 
			// this array will be used to count the number of comments that apply to a word
			var c = [] ;
			for (var i = 0 ; i < max ; i++) {
				c.push(0) ;
			}
			
			// 2 count number of comments on each word
			for (var j = 0 ; j < commentsArr.length ; j++) {
				for (var u = commentsArr[j].start_word ; u <= commentsArr[j].end_word ; u++) {
					c[u] = c[u] + 1 ;
				}
			}
	
			// 3 turn this counter into an array of occs
			var occs = [] ;
			var lastci = -1 ;
			var i = 0 ;
			for (i = 0; i < c.length ; i++) {
				if (c[i] != lastci) {
					if (occs.length > 0)
						occs[occs.length - 1]["endWord"] = i - 1 ;
					occs.push({"endWord": -1, "startWord": i, "nbWord": c[i]}) ;
					lastci = c[i] ;
				}
			}
			if (occs.length > 0) // close last occ
				occs[occs.length - 1]["endWord"] = i-1 ;
				
			// 4 get rid of occs having nbWord at 0
			var filteredOccs = [] ;
			for (var j = 0 ; j < occs.length ; j++) {
				if (occs[j]["nbWord"] != 0) 
					filteredOccs.push(occs[j]) ;
			}
			return filteredOccs ;
    	},	
    	
		this.so_filter = function(filterData, commentsArr, disMap, tags) {
			
			var filteredComments = [] ;
			for (var i = 0 ; i < commentsArr.length ; i++) {
				filteredComments.push(commentsArr[i]) ;
			}
			
    		var filteredDis = [] ;
    		for (var c_id in disMap) {
	    		for (var i = 0 ; i < disMap[c_id].length ; i++) {
	    			filteredDis.push(disMap[c_id][i]) ;
	    		}
    		}
    		var tagId = filterData['tagId'] ;
    		
    		if (tagId != -1) {
    			var tagName = "" ;
    			for (var i = 0 ; i < tags.length ; i++) {
    				if (tags[i].id == tagId) {
    					tagName = tags[i].name ;
    					break ;
    				}
    			}
				filteredComments = this.so_filterOnTag(tagName, filteredComments) ;
				filteredDis = this.so_filterOnTag(tagName, filteredDis) ;
    		}
    		else {
				var textfilterselect = filterData['textfilterselect'] ;
				var textsearchfor = filterData['textsearchfor'] ;
				var datefilterselect = filterData['datefilterselect']  ; // example "createdafter" 
				var fromDate = coment.util.dateFromString(filterData['fromdatefield']) ;
				var toDate = coment.util.dateFromString(filterData['todatefield']) ;
				var statefilterselect = filterData['statefilterselect'] ;
				
				textsearchfor = textsearchfor.trim() ;
				
				filteredComments = this.so_filterOnTextSearchedFor(textfilterselect, textsearchfor, filteredComments) ;
				filteredComments = this.so_filterOnDate(datefilterselect, fromDate, toDate, filteredComments) ;
				filteredComments = this.so_filterOnState(statefilterselect, filteredComments) ;
				
	    		filteredDis = this.so_filterOnTextSearchedFor(textfilterselect, textsearchfor, filteredDis) ;
				filteredDis = this.so_filterOnDate(datefilterselect, fromDate, toDate, filteredDis) ;
				filteredDis = this.so_filterOnState(statefilterselect, filteredDis) ;
    		}

			// add the comment even if it didn't satisfy the filter because one of its replies does satisfy the filter
			for (var i = 0 ; i < filteredDis.length ; i++) {
				for (var j = 0 ; j < commentsArr.length ; j++) {
					if (filteredDis[i].comment_id == commentsArr[j].id)
						filteredComments.push(commentsArr[j]) ;
				}
			}
			
			// remove duplicates 
			var unique = new Array() ;
			var ret_filteredComments = new Array() ;
			for (var i = 0 ; i < filteredComments.length ; i++) {
				if (! unique.contains(filteredComments[i].id)) {
					unique.push(filteredComments[i].id) ;
					ret_filteredComments.push(filteredComments[i]) ;
				}
			}

			return ret_filteredComments ;
    	},
    	
   		this.so_filterOnTag = function(tagName, filteredComments) {
    		var ret_filteredComments = [] ;
			var re = new RegExp("," + tagName + ",","gi");
			for (var i = 0 ; i < filteredComments.length ; i++) {
				var tags = "," + filteredComments[i].tags + ","; //comment.and title
				if(re.exec(tags) != null){
					ret_filteredComments.push(filteredComments[i]) ;
				}
			}
			return ret_filteredComments ;
    	},
    	
   		this.so_filterOnTextSearchedFor = function(textfilterselect, textsearchfor, filteredComments) {
    		var ret_filteredComments = [] ;
			var re = new RegExp(textsearchfor,"gi");
			// test each comment and dis for a match
			for (var i = 0 ; i < filteredComments.length ; i++) {
				switch(textfilterselect) {
				case "text_and_title" :
					var content = filteredComments[i].content ; //comment.and title
					var title = filteredComments[i].title ; //comment.and title
					if(re.exec(content) != null || re.exec(title) != null){
						ret_filteredComments.push(filteredComments[i]) ;
					}
					break ;
				case "user" : 
					var username = filteredComments[i].username ; //comment.and title
					if(re.exec(username)){
						ret_filteredComments.push(filteredComments[i]) ;
					}
					break ;
				}
			}
			return ret_filteredComments ;
		},
		
		this.so_filterOnDate = function(datefilterselect, fromDate, toDate, filteredComments) {
	  		var ret_filteredComments = [] ;
			for (var i = 0 ; i < filteredComments.length ; i++) {
				var created = coment.util.dateFromString(filteredComments[i].created) ;
				
				var add = ((datefilterselect == "createdbetween") && (created >= fromDate) && (created <= toDate)) ;
				add = add || ((datefilterselect == "createdafter") && (created >= fromDate)) ;
				add = add || ((datefilterselect == "createdbefore") && (created <= toDate)) ;
				add = add || (datefilterselect == "") ;

				if (add)
					ret_filteredComments.push(filteredComments[i]) ;
			}
			return ret_filteredComments ;
		},
		
		this.so_filterOnState = function(statefilterselect, filteredComments) {
			var filterStates = Ext.util.JSON.decode('[' + statefilterselect + ']') ;
	  		var ret_filteredComments = [] ;
			for (var i = 0 ; i < filteredComments.length ; i++) {
				var state = filteredComments[i].state_id ;
				if (filterStates.contains(state))
					ret_filteredComments.push(filteredComments[i]) ;
			}
			return ret_filteredComments ;
		}
	};
}
