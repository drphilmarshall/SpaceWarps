/* ===========================================================================

Spotter's Guide Image Carousel

Adapted from tutorial at:
    http://www.scribd.com/doc/19581128/How-to-Create-A-JavaScript-Carousel-From-Scratch-In-Under-10-Minutes

=========================================================================== */

<script type="text/javascript" src="http://jqueryjs.googlecode.com/files/jquery-1.3.2.min.js"></script>
<script type="text/javascript">
  $(document).ready(function(){
    //Define the animation speed for the Carousel 
    var speed = 600;
    $('#navPrev').click(function(){
      //As the rest of our carousel is hidden, lets move it's margin left 
      // until it's in view. We use the jQuery animate() function to give 
      // this movement a nice smooth feel
      $('#carousel ul').animate({marginLeft:'-280px'}, speed);
    });

    $('#navNext').click(function(){
      //And now lets move back to the start of the Carousel
      $('#carousel ul').animate({marginLeft:'1px'}, speed);
    });
  }); 
</script>


