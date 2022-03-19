//Beampy script is inspired by DzSlides javascript code (https://github.com/paulrouget/dzslides)
 
var Beampy = {
    id_slide: -1,
    html: null,
    slides: null,
    params: {}
};
Beampy.init = function() {
    document.body.className = "loaded";
    this.slides = Object.keys(slides); 
    this.html = document.body.parentNode;
    
    this.setup();
    this.onhashchange();
    this.setupTouchEvents();
    this.onresize();
    this.initmouse();
}
Beampy.setup = function() {
    var p = window.location.search.substr(1).split('&');
    p.forEach(function(e, i, a) {
        var keyVal = e.split('=');
        Beampy.params[keyVal[0]] = decodeURIComponent(keyVal[1]);
    });

    //pause autoplay videos
    $('video').each(function(){
        if (this.autoplay) {
            this.pause();
            this.currentTime = 0;
        }
    })
}
Beampy.onkeydown = function(aEvent) {
    // Don't intercept keyboard shortcuts
    if (aEvent.altKey
        || aEvent.ctrlKey
        || aEvent.metaKey
        || aEvent.shiftKey) {
        return;
    }
    if ( aEvent.keyCode == 37 // left arrow
      || aEvent.keyCode == 38 // up arrow
      || aEvent.keyCode == 33 // page up
    ) {
        aEvent.preventDefault();
        this.back();
    }
    if ( aEvent.keyCode == 39 // right arrow
      || aEvent.keyCode == 40 // down arrow
      || aEvent.keyCode == 34 // page down
    ) {
        aEvent.preventDefault();
        this.forward();
    }
    if (aEvent.keyCode == 35) { // end
        aEvent.preventDefault();
        this.goEnd();
    }
    if (aEvent.keyCode == 36) { // home
        aEvent.preventDefault();
        this.goStart();
    }
    if (aEvent.keyCode == 32) { // space
        aEvent.preventDefault();
        $("#html_store_slide_"+this.id_slide+"-"+this.layer+" video").each(function(){
        if (this.paused || this.ended){
              this.play();
          } else {
              this.pause();
          }
        });
    }
    if (aEvent.keyCode == 70) { // f
        aEvent.preventDefault();
        this.goFullscreen();
    }
}
/* Mouse scroll event */
Beampy.onmousewheel = function(event) {
    
    //Test if their is a bokeh figure to prevent conflict
    var bokeh = $('#html_store_slide_'+Beampy.id_slide+' .plotdiv');
    if (bokeh.length == 0) {
        event.preventDefault();
        //console.log(event);
        //Compute +1 for up and -1 for down
        var delta = Math.max(-1, Math.min(1, (event.wheelDelta || -event.detail)));
        
        if (delta == -1){
            this.forward();
        }
        
        if (delta == 1){
            this.back();
        } 
        
        return false;
    }
}
/* Touch Events */
Beampy.setupTouchEvents = function() {
    var orgX, newX;
    var tracking = false;
    var db = document.body;
    db.addEventListener("touchstart", start.bind(this), false);
    db.addEventListener("touchmove", move.bind(this), false);
    function start(aEvent) {
        aEvent.preventDefault();
        tracking = true;
        orgX = aEvent.changedTouches[0].pageX;
    }
    function move(aEvent) {
        if (!tracking) return;
        newX = aEvent.changedTouches[0].pageX;
        if (orgX - newX > 100) {
            tracking = false;
            this.forward();
        } else {
            if (orgX - newX < -100) {
                tracking = false;
                this.back();
            }
        }
    }
}
/* Resize trick for bokeh */
Beampy.resizebokeh = function() {    
    //For bokeh plot don't do a rescale
    var bkplt = $("#html_store_slide_"+this.id_slide+"-"+this.layer+" #bk_resizer");

    
    if (bkplt.length > 0){
        var db = document.body;
        var sx = db.clientWidth / window.innerWidth;
        var sy = db.clientHeight / window.innerHeight;
        var scale = Math.max(sx, sy);

        bkplt.css("width", "calc("+bkplt.attr("width")+"*"+1/scale+")");
        bkplt.css("height", "calc("+bkplt.attr("height")+"*"+1/scale+")");
        bkplt.css("transform", "scale("+scale+")");
    }
}			  


/* Adapt the size of the slides to the window */
Beampy.onresize = function() {
    var db = document.body;
    var sx = db.clientWidth / window.innerWidth;
    var sy = db.clientHeight / window.innerHeight;
    var scale = Math.round((1/Math.max(sx, sy)) * 100 + Number.EPSILON)/100;
    var transform = "scale(" + scale + ")";
    db.style.WebkitTransform = transform;
    db.style.transform = transform;
    this.resizebokeh();
}
Beampy.toggleContent = function() {
    //get the video in the store for the current id_slide
    var videos = $("#html_store_slide_"+this.id_slide+"-"+this.layer+" video");
    //get the div in html_store_slide to set their visibility
    var div = $("#html_store_slide_"+this.id_slide+"-"+this.layer);
    if (div.css('display') == 'block'){
        div.css('display', 'none');

        //reset the video to position 0 in time and pause it
        videos.each(function(){
            this.pause();
            this.currentTime = 0;
        });
    } else {
        div.css('display', 'block');
        videos.each(function(){
            if (this.autoplay) {
                this.currentTime = 0;
                this.play();
            }
        });
        videos.focus();
    }
}
Beampy.animatesvg = function(anim_number, fps, number_of_frames){
    //Count can be donne via javascript maingroup.childElementCount - 1
    var frameCount = number_of_frames;
    var anim_number = anim_number;
    //Reset frame view NO JQUERY FOR SVG !!!
    var maingroup = document.getElementById('svganimate_slide_'+this.id_slide+'-'+this.layer+'_'+anim_number);
    var curslide = slides['slide_'+this.id_slide];
    var i = 1;
    var frames = maingroup.childNodes;
    var display_frames = function(){
        if( curslide.hasOwnProperty('svganimates') ){
              maingroup.innerHTML = curslide['svganimates'][anim_number]['frames'][i] ;
          }
        i++;
        if (i == frameCount){
            //console.log("test stop");
            clearInterval(intervalometer);        
        }
    }
    var intervalometer = setInterval(function () { 
        display_frames();
    }, 1000*1/fps);
}

Beampy.setCursor = function(aIdx, layer) {
    // If the user change the slide number in the URL bar, jump
    // to this slide.
    window.location.hash = "#" + aIdx + "-" + layer ;
}
Beampy.onhashchange = function() {
    var cursor = window.location.hash.split("#"),
        newidx = 0,
    newstep = 0;
    
    if (cursor.length == 2) {
        tmpcursor = cursor[1].split('-');
    newidx = ~~tmpcursor[0];
    newstep = ~~tmpcursor[1];
    }
    if (newidx != this.id_slide || newstep != this.layer) {
        this.setSlide(newidx, newstep);
    }
}
Beampy.back = function() {
    if (this.id_slide == 0) {
        if (this.layer == 0 ){
            return;
        } else {
            this.setCursor(this.id_slide, this.layer-1);
        }
    } else {
        if (this.layer == 0) {
            last_layer = ~~slides['slide_'+(this.id_slide-1)]['svg'].length - 1;
            this.setCursor(this.id_slide-1, last_layer);
        } else {
            this.setCursor(this.id_slide, this.layer-1);
        }
    }
}
Beampy.forward = function() {
    if (this.id_slide >= this.slides.length-1 ) {
        if (this.layer <= this.maxlayer - 1){
            this.setCursor(this.id_slide, this.layer + 1);
        } else {
            return;
        }
    } else {
        if (this.layer <= this.maxlayer - 1){
            this.setCursor(this.id_slide, this.layer + 1);
        } else {
            this.setCursor(this.id_slide + 1, 0);
        }
    }
}
Beampy.goStart = function() {
    this.setCursor(0,0);
}
Beampy.goEnd = function() {
    var lastIdx = this.slides.length - 1;
    this.setCursor(lastIdx, this.maxlayer-1);
}
Beampy.setSlide = function(aIdx, layer) {
    //Deselect the previous store
    Beampy.toggleContent();
    this.id_slide = aIdx;
    this.layer = layer;
    this.maxlayer = 0;
    if (this.id_slide <= this.slides.length - 1 ) {
        
        var curslide = slides['slide_'+aIdx];
        this.maxlayer = curslide['svg'].length - 1;
        if (this.layer <= this.maxlayer){
            $("section").html( curslide.svg_header + curslide.svg[layer] + curslide.svg_footer );
            Beampy.toggleContent();
            //Pour bokeh (test if the object Bokeh exist)
            //Bokeh change the structure of it's div from 0.13 version
        var bokeh = $('#html_store_slide_'+this.id_slide+'-'+this.layer+' .bk-root');
                
            //console.log(bokeh);
        if (bokeh.length>0) {
            //clean div content before loading the plot
            bokeh.html("");
            //load the bokeh plot		
            scripts_slide['slide_'+this.id_slide].load_bokeh();
            //Update the size
            this.resizebokeh();		
            }
            //Test si des residus de bokeh
            //var bokeh_trash = $('.bk-bs-modal');
            //if (bokeh_trash.length) {
            //    bokeh_trash.remove(); //Remove these remainings divs
        //}
        } else {
            this.layer = -1;
            console.warn("Layer doesn't exist.");
        }
    } else {
        // That should not happen
        this.id_slide = -1;
        console.warn("Slide doesn't exist.");
    }
}
Beampy.goFullscreen = function() {
    var html = document.documentElement,
        requestFullscreen = html.requestFullscreen || html.requestFullScreen || html.mozRequestFullScreen || html.webkitRequestFullScreen;
    if (requestFullscreen) {
        requestFullscreen.apply(html);
    }
}

//Function to hide the mouse when it is idle taken from https://gist.github.com/josephwegner/1228975
Beampy.initmouse = function() {  
    var idleMouseTimer;
    var forceMouseHide = false;
    $("html").css('cursor', 'none');
    $("html").mousemove(function(ev) {
        if(!forceMouseHide) {
            $("html").css('cursor', '');
            clearTimeout(idleMouseTimer);
            idleMouseTimer = setTimeout(function() {
                $("html").css('cursor', 'none');
                forceMouseHide = true;
                setTimeout(function() {
                    forceMouseHide = false;
                }, 200);
            }, 500);
        }
    }); 
}

function init() {
    Beampy.init();
    window.onkeydown = Beampy.onkeydown.bind(Beampy);
    window.onresize = Beampy.onresize.bind(Beampy);
    window.onhashchange = Beampy.onhashchange.bind(Beampy);
    //For chrome, safari, ie, opera
    window.onmousewheel = Beampy.onmousewheel.bind(Beampy);
    //For firefox
    window.addEventListener("DOMMouseScroll", Beampy.onmousewheel.bind(Beampy), false);
}
window.onload = init;