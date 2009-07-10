// this is inspired (and almost a copy) of slocum's State.js
if (!core.CookieHandler) {
    core.CookieHandler = new function() {
	    this.set = function(name, value){
	        if(typeof value == 'undefined' || value === null){
	            this.clear(name);
	            return;
	        }
	        this.setCookie(name, value);
	        //Ext.state.CookieProvider.superclass.set.call(this, name, value);
	    };
	        
	    this.clear = function(name){
	        this.clearCookie(name);
	        //Ext.state.CookieProvider.superclass.clear.call(this, name);
	    };
	        
	    this.readCookies = function(){
	        var cookies = {};
	        var c = document.cookie + ';';
	        var re = /\s?(.*?)=(.*?);/g;
	    	var matches;
	    	while((matches = re.exec(c)) != null){
	            var name = matches[1];
	            var value = matches[2];
	            if(name && name.substring(0,7) == 'coment-'){
	                cookies[name.substr(7)] = this.decodeValue(value);
	            }
	        }
	        return cookies;
	    };
	    
	    this.setCookie = function(name, value){
	        document.cookie = "coment-"+ name + "=" + this.encodeValue(value) + "; expires=Thu, 2 Aug 2030 20:47:11 UTC; path=/" ;	        
	    };
	    
	    this.clearCookie = function(name){
	        document.cookie = "coment-" + name + "=null; expires=Thu, 01-Jan-70 00:00:01 GMT; path=/"
	    };
	    
		this.decodeValue = function(cookie){
	        var re = /^(a|n|d|b|s|o)\:(.*)$/;
	        var matches = re.exec(unescape(cookie));
	        if(!matches || !matches[1]) return; // non state cookie
	        var type = matches[1];
	        var v = matches[2];
	        switch(type){
	            case 'n':
	                return parseFloat(v);
	            case 'd':
	                return new Date(Date.parse(v));
	            case 'b':
	                return (v == '1');
	            case 'a':
	                var all = [];
	                var values = v.split('^');
	                for(var i = 0, len = values.length; i < len; i++){
	                    all.push(this.decodeValue(values[i]))
	                }
	                return all;
	           case 'o':
	                var all = {};
	                var values = v.split('^');
	                for(var i = 0, len = values.length; i < len; i++){
	                    var kv = values[i].split('=');
	                    all[kv[0]] = this.decodeValue(kv[1]);
	                }
	                return all;
	           default:
	                return v;
	        }
	    };
    
    	this.encodeValue = function(v){
	        var enc;
	        if(typeof v == 'number'){
	            enc = 'n:' + v;
	        }else if(typeof v == 'boolean'){
	            enc = 'b:' + (v ? '1' : '0');
	        }else if(v instanceof Date){
	            enc = 'd:' + v.toGMTString();
	        }else if(v instanceof Array){
	            var flat = '';
	            for(var i = 0, len = v.length; i < len; i++){
	                flat += this.encodeValue(v[i]);
	                if(i != len-1) flat += '^';
	            }
	            enc = 'a:' + flat;
	        }else if(typeof v == 'object'){
	            var flat = '';
	            for(var key in v){
	                if(typeof v[key] != 'function'){
	                    flat += key + '=' + this.encodeValue(v[key]) + '^';
	                }
	            }
	            enc = 'o:' + flat.substring(0, flat.length-1);
	        }else{
	            enc = 's:' + v;
	        }
	        return escape(enc);        
	    } ;
	}
}