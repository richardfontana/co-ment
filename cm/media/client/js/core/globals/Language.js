if (!core.Language) {
    core.Language = new function() {
		this._format = "" ;
		this._shortformat = "" ;
		this.init = function(){
			
			
			this._format = gettext("F j, Y, \\a\\t g:i a") ;
			this._shortformat = gettext("n/j/Y") ;
			Date.monthNames = gettext("January|February|March|April|May|June|July|August|September|October|November|December").split("|") ;
			Date.dayNames = gettext("Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday").split("|") ;
		} ;

// UTILS		
		this.formatDate = function(date) {
			return date.dateFormat(this._format) ;
		} ;
		this.formatDateShort = function(date) {
			return date.dateFormat(this._shortformat) ;
		} ;
    };
}
   