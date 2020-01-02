
var frames_done=[];  // Just for the frames done
var frames_jobs=[];  // All the info for the frames done
var select_border_size = 3; // See css

// Fix the height of the chooser
function fix_pifc_ui() {

   var fh = $('#footer').outerHeight();
 
   // It's too small...
   if($(window).outerHeight()-fh-$('#main_container').outerHeight() > 60) {
      while($(window).outerHeight()-fh-$('#main_container').outerHeight() > 60) {
         $('#cropped_frame_selector').height($('#cropped_frame_selector').height()+1)
      }

      // Keep Ratio
      $('#cropped_frame_selector').width($('#cropped_frame_selector').height()*Math.round(w)/Math.round(h));
      $('#cropped_frame_selector').height($('#cropped_frame_selector').width()*Math.round(h)/Math.round(w));
   }

   $('#cropped_frame_selector').css('max-width','100%');

   // Change Markers 
   $('#org_lh, #lh').css('width','100%');
   $('#org_lv, #lv').css('height','100%');

}


// Load particular frame into the selecto
function load_frame(fd_id) {
   var $frame = $('.select_frame[data-rel='+fd_id+']');
   var scroll_to = fd_id-4;

   // Cur has changed
   $('.select_frame').removeClass('cur');
   $frame.addClass('cur');

   // Not "done" yet
   $('#cropped_frame_selector').removeClass('done');

   // We load the image
   $('#cropped_frame_selector').css({
      'background-image':'url('+$($frame.find('img')).attr('src')+')'
   }); 

   // Scroll to frame -1 on top if it exists
   if($('.select_frame[data-rel="'+scroll_to+'"]').length==0) {
      scroll_to-= 1;
      while($('.select_frame[data-rel="'+scroll_to+'"]').length==0 && scroll_to>=0) {
         scroll_to-= 1;
      }
   }
   $('#frame_select_mod').scrollTo($('.select_frame[data-rel="'+scroll_to+'"]'), 150 );
  

   // If we already have data: we show the circle
   // and the reset button
   var cur_f_done = false;
   $.each(frames_jobs, function(i,v){
      if(typeof v !=='undefined' && v['fn']==fd_id) {
          // Warning -5 because the circle has a 10px diameter 
         $('#cirl').css({
            'left': parseInt(v['pos_x']-5) + 'px',
            'top':  parseInt(v['pos_y']-5) + 'px' 
         }).show();
         
         $('#reset_frame').css('visibility','visible');
         cur_f_done = true;
      }
   });


   if(!cur_f_done){
      $('#cirl').hide();
      $('#reset_frame').css('visibility','hidden');
   }
 
}


// Go to Next Frame
function go_to_next(next_id) {
 
   // Does the next frame exist?
   var $next_frame = $('.select_frame[data-rel='+next_id+']');
    
   if($next_frame.length != 0) {
      load_frame(parseInt(next_id));
   } else {
      // We select the first one 
      load_frame(parseInt($($('#cropped_frame_select .select_frame').get(0)).attr('data-rel')));
   }

}


// Init actions
function setup_init_pos_choos_actions() {

   var selector_width = $('#cropped_frame_selector').outerWidth();
   var selector_height = $('#cropped_frame_selector').outerHeight();
 
   var factor  = w/selector_width; // Both are the same (or at least should be!)

   // By default
   $('#cirl').hide();

   // Select Frame
   $('.select_frame').unbind('click').click(function() {
      load_frame(parseInt($(this).attr('data-rel')));
   })

   // Click "Skip"
   $('#skip_frame').unbind('click').click(function() {
      // Which one is selected?
      var cur_fr_id = $('#cropped_frame_select .cur').attr('data-rel');
      go_to_next(parseInt(cur_fr_id)+1);
   });

   // Click "Reset"
   $('#reset_frame').unbind('click').click(function() {
      // Which one is selected?
      var cur_fr_id = $('#cropped_frame_select .cur').attr('data-rel'); 

      // Remove from frames_jobs
      $.each(frames_jobs, function(i,v){
         if(typeof v !=='undefined' && v['fn']==cur_fr_id) {
            frames_jobs.splice(i, 1); 
         }
      });

      $.each(frames_done, function(i,v){
         if(typeof v !=='undefined' && v==cur_fr_id) {
            frames_done.splice(i, 1); 
         }
      });
    

      // Remove the info from the selector
      $('#cropped_frame_select .cur').removeClass('done').find('.pos').html('');
      // Update counter
      $('#fr_cnt').html(parseInt($('#fr_cnt').html())-1);

      $('#cirl').hide();
   });

   // Select Meteor
   $("#cropped_frame_selector").unbind('click').click(function(e){
     
      var parentOffset = $(this).offset(); 
      var relX = e.pageX - parentOffset.left - select_border_size;
      var relY = e.pageY - parentOffset.top - select_border_size;

      // Convert into HD_x & HD_y
      // from x,y
      var realX = relX*factor+x;
      var realY = relY*factor+y;
 
      // Transform values
      if(!$(this).hasClass('done')) {
          $(this).addClass('done');
      } else {
          $('#lh').css('top',relY);
          $('#lv').css('left',relX); 
      }
 
      cur_fr_id = $('#cropped_frame_select .cur').attr('data-rel');

      // Add current frame to frame_done if not already there
      if($.inArray(cur_fr_id, frames_done )==-1) {
         frames_done.push(parseInt(cur_fr_id));  // We push an int so we can get the min
         $('#fr_cnt').html(parseInt($('#fr_cnt').html())+1);
      }

      // Add info to frames_jobs
      frames_jobs.push({
         'fn': cur_fr_id,
         'x': realX,
         'y': realY,
         'pos_x': relX,
         'pos_y': relY
      });
      
      // Add info to frame scroller
      $('#cropped_frame_select .cur').addClass('done').find('.pos').html('<br>x:' + parseInt(realX) + ' y:'  + parseInt(realY));
      
      // Go to next frame
      go_to_next(parseInt(cur_fr_id)+1);
      
  }).unbind('mousemove').mousemove(function(e) {
      
      var parentOffset = $(this).offset(); 
      var relX = e.pageX - parentOffset.left - select_border_size;
      var relY = e.pageY - parentOffset.top - select_border_size;

      // Cross
      if(!$(this).hasClass('done')) {
          $('#lh').css('top',relY-2);
          $('#lv').css('left',relX-2); 
      }
       
  });


  // Create them all
  $('#create_all').unbind('click').click(function() {

      // Update the temporary form and submit it (POST)
      $('#post_form input[name=frames]').val(JSON.stringify(frames_jobs))
      $('#post_form').submit();


      //window.location='./webUI.py?cmd=manual_reduction_create_final_json&frames=' + JSON.stringify(frames_jobs)+'&video_file='+video_file;
  })
}



// Function Init position chooser tools
function init_pos_choos() { 
  
   // Add first frame to picker
   var $first_img = $($('#cropped_frame_select').find('img').get(0))
   var $first_img_holder  = $first_img.closest('a');

   if(w>h) {
      new_w = $('.modal-header').width();
      ratio = new_w/w;
      w = new_w;
      h = h*ratio;
   }  
   
   $('#cropped_frame_selector').css({
      'background-image':'url('+$first_img.attr('src')+')',
      'background-size':  'contain',
      'background-repeat': 'no-repeat',
      'width': w + 'px',  // Defined on the page
      'height': h   + 'px', // Defined on the page
      'background-position':'50% 50%',
      'background-color':'#000'
   });

   $first_img_holder.addClass('cur');

   // Fix height
   fix_pifc_ui();

   // Setup action
   setup_init_pos_choos_actions();

   // Stop loading 
   loading_done();
 
}


 