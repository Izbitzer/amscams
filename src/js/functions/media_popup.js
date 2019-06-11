$(function() {
      $('.img-link').magnificPopup({
        type: 'image' ,
        removalDelay: 300, 
        mainClass: 'mfp-fade'
      });

      $('.img-link-gal').magnificPopup({
        type: 'image' ,
        removalDelay: 300, 
        preloader: true,
        mainClass: 'mfp-fade',
        gallery:{
          enabled:true
        }
      });
      
      $('.vid-link').magnificPopup({
        type: 'iframe',
        preloader: true
      });

      $('.vid_link_gal').magnificPopup({
        type: 'iframe',
        preloader: true,
        gallery:{
          enabled:true
        },
        iframe: {
          markup: '<div class="mfp-iframe-scaler">'+
            '<div class="mfp-close"></div>'+
            '<iframe class="mfp-iframe" frameborder="0" allowfullscreen></iframe>TOTOTO'+
          '</div>',
           
        }
      });
});



