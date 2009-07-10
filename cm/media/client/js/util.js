coment.util.alert = function() {
	alert('util alert');
}
coment.util.getAuthorAndDate = function(entity){
	var username = (entity.username == "") ? gettext("anonymous") : entity.username ;
	var date = entity['created'] ;
	
 	var whoWhen = interpolate(gettext("By %(author)s on %(date)s"), {author:username, date:core.Language.formatDate(date)}, true) ;
	return whoWhen ;
}

coment.util.getTags = function(a){
	var ret = a.tags ;
	if (ret != "")
		ret = gettext("tags:") + ret ;
	return ret 
}

coment.util.getLocation = function( )
{
	var regexS = "[^?]*";
	var regex = new RegExp( regexS );
	var loc = regex.exec( window.location.href );
	if( loc == null )
		return "";
	else 
		return loc[0];
}

coment.util.getPageArgs = function( )
{
	var ret = "" ;
	var qmIndex = window.location.href.indexOf("?") ;
	if (qmIndex != -1) {
		ret = window.location.href.substring(qmIndex+1)
	}
	return ret ;
}

coment.util.gup = function( name )
{
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var tmpURL = window.location.href;
  var results = regex.exec( tmpURL );
  if( results == null )
    return "";
  else 
    return results[1];
}

coment.util.displayYesNo = function(elt, doDisplay){
	var fn = (doDisplay) ? YAHOO.util.Dom.removeClass : YAHOO.util.Dom.addClass ;
	fn.call(YAHOO.util.Dom, elt, 'displaynone') ;
}

// orders an array. to order the arr entirely call quicksort(arr, 0, arr.length - 1)
coment.util.quicksort = function (a, lo, hi) {
//  lo is the lower index, hi is the upper index of the region of array a that is to be sorted
   var i=lo, j=hi, h;
   var x=a[Math.floor((lo+hi)/2)];

   //  partition
   do
   {
       while (a[i].val() < x.val()) i++;
       while (a[j].val() > x.val()) j--;
       if (i<=j)
       {
           h=a[i]; a[i]=a[j]; a[j]=h;
           i++; j--;
       }
   } while (i<=j);

   //  recursion
   if (lo<j) coment.util.quicksort(a, lo, j);
   if (i<hi) coment.util.quicksort(a, i, hi);
}

String.prototype.ellipse = function(maxLength){
    if(this.length > maxLength){
        return this.substr(0, maxLength-3) + '...';
    }
    return this;
}

coment.util.fromMarkerIdToWord = function (spanId) {
	var prefix = coment.cst.textWordIdPref ;
	return parseInt(spanId.substr(prefix.length)) ;
}

coment.util.fromWordToMarkerId = function (word) {
	return coment.cst.textWordIdPref + word ;
}

coment.util.checkLength = function (string, atLeast, atMost) {
	var longEnough = true ;
	if (atLeast)
		longEnough = string.length >= atLeast ;

	var notTooLong = true ;
	if (atMost)
		longEnough = string.length <= atMost ;
		
	return (longEnough && notTooLong) ;
}

coment.util.checkNonEmpty = function (string) {
	var s = coment.util.trim(string) ;
	return coment.util.checkLength(s, 1) ;
}

// Removes leading whitespaces
coment.util.LTrim = function( value ) {
	
	var re = /\s*((\S+\s*)*)/;
	return value.replace(re, "$1");
	
}

// Removes ending whitespaces
coment.util.RTrim = function( value ) {
	
	var re = /((\s*\S+)*)\s*/;
	return value.replace(re, "$1");
	
}

// Removes leading and ending whitespaces
coment.util.trim = function( value ) {
	
	return coment.util.LTrim(coment.util.RTrim(value));
	
}

coment.util.checkEmail = function (string) {
	
  //var regex = /^(.+)@(.+)\\.(\\w+)$/;
  var regex =   /^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*$/
  return regex.test(string);
}

// maybe this is "too clever" and should instead eliminate only whitespaces in selections 
coment.util.containsSeparatorsOnly = function (s) {
	//	"^" for start of the string 
	//	"\s" for space character
	//	"\.\!\?" for . ! and ?
	//	";:," for ; : , 
	//	"$" for end of the string 
		var reg = /^[\s\.\!\?;:,]*$/
		return reg.test(s) ;
}
	
coment.util.testColorFunction1 = function (p) {
	var max = 12 ;
	var pp = (p > max) ? max : p ;
		
	var n = 255 - Math.floor((145 / max) * pp) ;
	var s = n.toString(16) ;
	while (s.length < 2)
		s = "0" + s ; 
	
	
//	return "#ff" + s + "6e"  ;
	return "#ff" + s + "9a"  ;
}

coment.util.emptyDomNode = function (node) {
	while (node.hasChildNodes()) {
		node.removeChild(node.firstChild);
	}
}

coment.util.setValue = function (id, value) {
	var node = YAHOO.util.Dom.get(id) ;
	if (node)	
		node.value = value; 
}

coment.util.setInnerHTML = function (id, html) {
	var node = YAHOO.util.Dom.get(id) ;
	if (node)	
		node.innerHTML = html; 
}

coment.util.getTextDocument = function(){
	if (coment.cst.framed) {
		var w = this.getTextWindow() ;
		if (w) 
			return w.document;
		return null ;
	}
	else 
		return document ;
/*	var myf = top.document.getElementById("frameid");
	var doc = myf.contentWindow.document || myf.contentDocument;
	return doc ;*/
};

coment.util.getTextWindow = function(){
	if (coment.cst.framed)
		return frames['frameid'] ; // $$$ dangerous
	else 
		return window ;
/*	var myf = top.document.getElementById("frameid");
	var doc = myf.contentWindow.document || myf.contentDocument;
	return doc ;*/
};
	
// get elements from Slocum's cache when possible
coment.util.getElt = function(id){
	var w = this.getTextWindow() ;
	var elt = w.Ext.Element.cache[id] ;
	if (!elt) 
		elt = w.Ext.Element.get(id) ;
	return elt ;
}
// cf client.py on the server ("%Y-%m-%d %H:%M:%S")
// http://fr.php.net/date
coment.util.dateFromString = function(str){
	return Date.parseDate(str, "Y-m-d H:i:s" );
}

coment.util.dateToString = function(d){
	return d.dateFormat("Y-m-d H:i:s" );
}