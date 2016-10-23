(function ($) {

 "use strict"; 
	$(document).ready(function(){
		//---------------------------------------------
		//Nivo slider
		//---------------------------------------------
			 $('#ensign-nivoslider').nivoSlider({
				effect: 'random',
				slices: 15,
				boxCols: 8,
				boxRows: 4,
				animSpeed: 500,
				pauseTime: 500000,
				startSlide: 0,
				directionNav: false,
				controlNavThumbs: false,
				pauseOnHover: true,
				manualAdvance: false
			 });
      


      
      
		//---------------------------------------------
		// scrollUp
		//---------------------------------------------	
			$.scrollUp({
				scrollText: '<i class="fa fa-angle-up"></i>',
				easingType: 'linear',
				scrollSpeed: 1000,
				animation: 'fade'
			});
		//---------------------------------------------
		 //jQuery MeanMenu
		//---------------------------------------------
			$('nav#dropdown').meanmenu();
		//---------------------------------------------
		// price slider 
		//---------------------------------------------
			  $( "#slider-range" ).slider({
			   range: true,
			   min: 100,
			   max: 450,
			   values: [ 100, 450 ],
			   slide: function( event, ui ) {
				$( "#amount" ).val( "" + ui.values[ 0 ] + " - " + ui.values[ 1 ] );
			   }
			  });
			  $( "#amount" ).val( "" + $( "#slider-range" ).slider( "values", 0 ) +
			   " - " + $( "#slider-range" ).slider( "values", 1 ) );
		//---------------------------------------------
		// bxslider
		//---------------------------------------------
			$('.single-zoom-thumb .bxslider').bxSlider({
				slideWidth: 117,
				slideMargin:15,
				minSlides: 4,
				maxSlides: 4,
				pager: false,
				speed: 500,
				pause: 3000,
				mode: 'vertical',
				adaptiveHeight: true
			});
		//---------------------------------------------
		//Wol Carousel
		//--------------------------------
			$(".features-curosel").owlCarousel({
				autoPlay: false,
				items: 4,
				navigation:true,
				itemsDesktop : [1199,4],
				itemsDesktopSmall : [979,3],
				itemsTablet: [767,1],
				rewindNav : false
			});	
      
      
      
        	$("#ProductThumbs").owlCarousel({
				autoPlay: false,
				items: 3,
				navigation:true,
				itemsDesktop : [1199,4],
				itemsDesktopSmall : [979,3],
				itemsTablet: [767,1],
				rewindNav : false
			});	
      
      
      
			$(".latest-carousel").owlCarousel({
				autoPlay: false,
				items: 2,
				navigation:true,
				itemsDesktop : [1199,2],
				itemsDesktopSmall : [979,2],
				itemsTablet: [757,1],
				rewindNav : false
			});
			$(".brand-carousel").owlCarousel({
				autoPlay: true,
				items: 5,
				navigation:true,
				itemsDesktop : [1199,4],
				itemsDesktopSmall : [979,3],
				itemsTablet: [600,3],
				rewindNav : false
			});
			$(".catagory-thumb-slide").owlCarousel({
				autoPlay: false,
				items: 4,
				navigation:true,
				itemsDesktop : [1199,4],
				itemsDesktopSmall : [979,3],
				itemsTablet: [600,2],
				rewindNav : false
			});
		//---------------------------------------------
		//Show boxnav on hover
		//---------------------------------------------
			$('.search-contain, .cart-area, .mega-collapse ul.nav li, .small-menu').on("mouseenter", function() {
				$(this).find(".search-content, .top-cart-content, .mega-menu, .smallmenu-list").stop(true).slideDown();
			});
			$('.search-contain, .cart-area, .mega-collapse ul.nav li, .small-menu').on("mouseleave", function() {
				$(this).find(".search-content, .top-cart-content, .mega-menu, .smallmenu-list").stop(true).slideUp();
			});
		//---------------------------------------------	
		//ElevateZoom
		//---------------------------------------------	
			$("#zoom1").elevateZoom({
				gallery:'gallery_01', 
				cursor: 'pointer', 
				galleryActiveClass: "active", 
				imageCrossfade: true
			});
      
      
            
     

	}); 
})(jQuery);