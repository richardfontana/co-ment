if (!core.User) {
    core.User = new function() {
// UTILS		
		this.getCookieAuthor = function() {
			var auth = core.CookieHandler.readCookies()["author"] ;
			if (auth == null)
				auth = "" ;
			return auth ;
		} ;
		
		this.getCookieEMail = function() {
			var auth = core.CookieHandler.readCookies()["email"] ;
			if (auth == null)
				auth = "" ;
			return auth ;
		} ;
		
		this.record = function(author, email) {
		   	core.CookieHandler.set("author", author) ;
	      	core.CookieHandler.set("email", email) ;
		} ;
    } ;
}
   