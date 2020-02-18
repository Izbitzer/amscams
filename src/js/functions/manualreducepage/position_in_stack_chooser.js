var HAVE_START = false;
var HAVE_END = false;

// Update selector position and corresponding data
function update_select_preview(top,left,margins,W_factor,H_factor,cursor_dim, cur_step_start,cursor_border_width,prev_W,prev_H,show_pos) {
   

   // Maximize the values
   if(top<=5) { top = 0; }
   if(left<=5) { left=0; }
   if(Math.abs(top-prev_W)<=5) { top = prev_W; }
   if(Math.abs(left-prev_H)<=5)  { left = prev_H; }

   // Move Selector
   $("#selector").css({
      top: top - cursor_dim/2,
      left: left - cursor_dim/2
   });

   sel_x = Math.floor(left)+margins - cursor_dim/2;
   sel_y = Math.floor(top)+margins - cursor_dim/2;

   if(show_pos) {
      cur_step_start = !cur_step_start

      if(cur_step_start) {
         // Update START X/Y
         //$('#res .start').html('<b>A</b> x:' + Math.floor(sel_x*W_factor)+ 'px ' + 'y:'+  Math.floor(sel_y*H_factor) +'px');
         //$('#selector').css('border-color','#ccc');

         // Put the static square on the view
         if($('#sel_start_static').length==0) {
            $('<div id="sel_start_static" style="width:'+cursor_dim+'px; height:'+cursor_dim+'px;position:absolute; border:'+cursor_border_width+'px solid #ccc; border-radius:50%">').appendTo($('#main_view'));
         }
         
         $('#sel_start_static').css({
            top: top - cursor_dim/2,
            left: left - cursor_dim/2
         });

         $('input[name=x_start]').val(Math.floor(left));
         $('input[name=y_start]').val(Math.floor(top));  

         HAVE_START = true;
      } else {
         // Update END X/Y
         //$('#res .end').html('<b>B</b> x:' + Math.floor(sel_x*W_factor)+ 'px ' + 'y:'+  Math.floor(sel_y*H_factor) +'px');
         //$('#selector').css('border-color','green');

          // Put the static square on the view
          if($('#sel_end_static').length==0) {
            $('<div id="sel_end_static" style="width:'+cursor_dim+'px; height:'+cursor_dim+'px;position:absolute; border:'+cursor_border_width+'px solid #ccc; border-radius:50%">').appendTo($('#main_view'));
          }

          $('#sel_end_static').css({
            top: top - cursor_dim/2,
            left: left - cursor_dim/2
         }); 
         
         $('input[name=x_end]').val(Math.floor(left));
         $('input[name=y_end]').val(Math.floor(top));  
          
         HAVE_END = true;
      }  
   }

   // Enable continue button 
   if(HAVE_END && HAVE_START) {
      $('#step1_btn').removeAttr('disabled').removeClass('disabled');

      // Add the rectangle
      if($('#sel_rectangle_static').length==0) {
         $('<div id="sel_rectangle_static" style="position:absolute; border:1px solid rgba(255,255,255,.6)">').appendTo($('#main_view'));
      }

      // We draw a rectangle & get the proper data to pass
      var h = parseInt($('input[name=y_end]').val())  - parseInt($('input[name=y_start]').val());
      var w = parseInt($('input[name=x_end]').val())  - parseInt($('input[name=x_start]').val());
      
      // Update "real w & h"
      $('input[name=w]').val(Math.abs(w)*W_factor);
      $('input[name=h]').val(Math.abs(h)*H_factor); 
 

      if(w<=0 && h>0) { 
         n_TOP  = parseInt($('input[name=y_start]').val());
         n_LEFT = parseInt($('input[name=x_end]').val());
         n_WIDTH = Math.abs(w);
         n_HEIGHT = h; 
      } else if(h<=0 && w>0) { 
         n_TOP  = parseInt($('input[name=y_end]').val());
         n_LEFT = parseInt($('input[name=x_start]').val());
         n_WIDTH = w;
         n_HEIGHT = Math.abs(h);
      } else if(h<=0 && w<=0) {
         n_TOP  = parseInt($('input[name=y_end]').val());
         n_LEFT = parseInt($('input[name=x_end]').val());
         n_WIDTH = Math.abs(w);
         n_HEIGHT = Math.abs(h);
      } else {
         n_TOP  = parseInt($('input[name=y_start]').val());
         n_LEFT = parseInt($('input[name=x_start]').val());
         n_WIDTH = Math.abs(parseInt($('input[name=x_start]').val())  - parseInt($('input[name=x_end]').val()));
         n_HEIGHT = Math.abs(parseInt($('input[name=y_start]').val())  - parseInt($('input[name=y_end]').val()));
      }

      $('#sel_rectangle_static').css({
         'top': n_TOP,
         'left': n_LEFT,
         'width': n_WIDTH ,
         'height': n_HEIGHT
      });
 
      // Update real x,y
      $('input[name=ys]').val(n_TOP*H_factor);
      $('input[name=xs]').val(n_LEFT*W_factor); 
       
   }
   
   return cur_step_start
}


// Create  select meteor position from stack
function create_meteor_selector_from_stack(image_src, is_it_for_sync, type='') {
   var cursor_dim = 8;            // Cursor dimension
   var margins = 15;              // Max position (x,y) of the meteor inside the cursor

   var real_W = 1920;
   var real_H = 1080;

   var prev_W = 1075;              // Preview
   var prev_H = 605; 
     
   var cursor_border_width  = 2; 
   
   var sel_x = prev_W/2-cursor_dim/2;
   var sel_y = prev_H/2-cursor_dim/2;

   var W_factor = real_W/prev_W;
   var H_factor = real_H/prev_H; 

   var cur_step_start = false;
 
   var init_top = prev_H/2-cursor_dim/2;
   var init_left = prev_W/2-cursor_dim/2;

 
   $('<div id="draggable_area" style="width:'+(prev_W+margins*2) + 'px; height:' +( prev_H+margins*2) + 'px;margin:0 auto;">\
     <div id="main_view" style="background-color:#000;background-image:url('+image_src+'); width:'+prev_W+'px; height:'+prev_H+'px; margin: 0 auto; position:relative; background-size: contain;">\
      <div id="selector" class="ng pa" style="; border-radius:50%; top:-9999px; left:-9999px;width:'+cursor_dim+'px; height:'+cursor_dim+'px; border:'+cursor_border_width+'px solid #fff;"></div>\
     </div></div></div></div><div class="text-right"><button id="step1_btn" class="btn btn-lg btn-primary disabled" disabled>Continue</button></div>').appendTo($('#step1_cont'));
   
   
   offset = $('#main_view').offset();

   // Move on click
   $('#main_view').click(function(e) {
      var top =  e.pageY - offset.top;
      var left = e.pageX - offset.left;
      cur_step_start = update_select_preview(top,left,margins,W_factor,H_factor,cursor_dim,cur_step_start,cursor_border_width,prev_W,prev_H,true);
      e.stopImmediatePropagation();
      return false;
   });
   


   if(type=='') {
      // Go to next step 
      if(is_it_for_sync) {
         // It's for the manual synchronization
         $('#step1_btn').click(function() {
            window.location = './webUI.py?cmd=manual_sync_chooser&json='+json+'&video_file='+video_file+'&x_start='+$('input[name=xs]').val()+'&y_start='+$('input[name=ys]').val()+'&w='+$('input[name=w]').val()+'&h='+$('input[name=h]').val()
         })


      } else {
         // It's for the manual reduction
         $('#step1_btn').click(function() {
            window.location = './webUI.py?cmd=manual_reduction_cropper&json='+json+'&video_file='+video_file+'&x_start='+$('input[name=xs]').val()+'&y_start='+$('input[name=ys]').val()+'&w='+$('input[name=w]').val()+'&h='+$('input[name=h]').val()
         })

      }
   } else if(type=='minute') {
      $('#step1_btn').click(function() {
         window.location = './webUI.py?cmd=automatic_detect_minute&stack='+stack+'&x_start='+$('input[name=xs]').val()+'&y_start='+$('input[name=ys]').val()+'&w='+$('input[name=w]').val()+'&h='+$('input[name=h]').val()
      })
   }

   

}
