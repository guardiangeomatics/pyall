$(document).ready(function() {

	/* activate sidebar */
	$(&#39;#sidebar&#39;).affix({
	offset: {
		top: 235
	}
});

/* activate scrollspy menu */
var $body   = $(document.body);
var navHeight = $(&#39;.navbar&#39;).outerHeight(true) + 10;

$body.scrollspy({
	target: &#39;#leftCol&#39;,
	offset: navHeight
});

/* smooth scrolling sections */
$(&#39;a[href*=#]:not([href=#])&#39;).click(function() {
	if (location.pathname.replace(/^\//,&#39;&#39;) == this.pathname.replace(/^\//,&#39;&#39;)
	&amp;&amp; location.hostname == this.hostname) {
	var target = $(this.hash);
	target = target.length ? target : $(&#39;[name=&#39; + this.hash.slice(1) +&#39;]&#39;);
	if (target.length) {
	$(&#39;html,body&#39;).animate({
	scrollTop: target.offset().top - 50
	}, 1000);
	return false;
	}
	}
	});

});
		
