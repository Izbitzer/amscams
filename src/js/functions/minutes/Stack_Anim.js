var $allstacks;
var totalStacks;
var animationStackDuration;
var timePerStack;
var timeWhenLastUpdateStack;
var timeFromLastUpdateStack;
var stackNumber; 
var stackplaying; 
var sens = "+"

// Modal With Player
function addAnimMinuteModalTemplate($allstacks,cam_id) {
  

   // Get Day 
   var d = $('input[ data-url-param="limit_day"]').val();
  

   $('#anim_min_modal').remove();

   $('<div id="anim_min_modal" class="modal fade" tabindex="-1" role="dialog"><div class="modal-dialog modal-dialog-centered"  style="min-width: 800px;" role="document">\
   <div class="modal-content"><div class="modal-body"><div id="anim_header" class="d-flex justify-content-between"><p>Stack animation <b>'+d+' Cam#'+cam_id+'</p><p><span id="cur_f"></span></b></p></div><div id="anim_holder" style="width:688px;">\
   </div><div class="modal-footer d-flex justify-content-between p-0 pb-2 pr-2">\
   <div class="pt-2"><input type="range" value="1" id="marStack" max="10" min="-10"/> <span id="cur_sp"></span></div>\
   <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button></div></div></div></div>').appendTo('body');
   
   // Add all the frames
   $allstacks.each(function(i,v) {
       $(this).clone().attr('style','').addClass('to_anim to_anim-'+i).appendTo('#anim_holder');
   });

   animationStackDuration = 1000; //$allstacks.length; // Duration get the 
}


// 'step' function will be called each time browser rerender the content
// we achieve that by passing 'step' as a parameter to 'requestAnimationFrame' function
function step_minute(startTime) {
  
   // 'startTime' is provided by requestAnimationName function, and we can consider it as current time
   // first of all we calculate how much time has passed from the last time when frame was update
   if (!timeWhenLastUpdateStack) timeWhenLastUpdateStack = startTime;
   timeFromLastUpdateStack = startTime - timeWhenLastUpdateStack;
 
   // then we check if it is time to update the frame
   if (timeFromLastUpdateStack > timePerStack) {
     
     $('.to_anim').css('opacity', 0); 
     $(`.to_anim-${stackNumber}`).css('opacity', 1);  
     timeWhenLastUpdateStack = startTime;
      

     if(sens=='+') {
         if (stackNumber >= totalStacks-1) {
            stackNumber = 0;
         } else {
            stackNumber = stackNumber + 1;
         } 
     } else {
         if (stackNumber <= 0) {
            stackNumber = totalStacks;
         } else {
            stackNumber = stackNumber - 1;
         }

     }


       
 
     $('#cur_f').text($(`.to_anim-${stackNumber}`).attr('data-rel'));
     //console.log("FN" + stackNumber);
   }
 
   if(stackplaying) requestAnimationFrame(step_minute);
 }

function minute_anim(cam_id) {
   $allstacks = $('.cam_'+cam_id);
   $allstacks = $allstacks.reverse();
   totalStacks = $allstacks.length;
   addAnimMinuteModalTemplate($allstacks,cam_id);
   $('#anim_min_modal').modal();
   $('#anim_min_modal').on('hidden.bs.modal', function () {
        stackplaying = false; 
        $('#anim_min_modal').remove(); 
   })

   if(totalStacks==0) {
      bootbox.alert({
          message: "No stack found. Error 452b",
          className: 'rubberBand animated error',
          centerVertical: true
      });
      return false;
  }

  timePerStack = 1000; //animationStackDuration / totalStacks;
  stackNumber = 0; 
  stackplaying = true;
  requestAnimationFrame(step_minute);

  // Inpur range for animation speed
  $('#marStack').val(0).on('input', function () { 
      var val = parseInt($(this).val()), text ='';
      if(val<0) {
         sens = "-";
         text = "<<";
      } 
      else {
         sens = "+"
         text = ">>";
      }

      val+= 1;
      timePerStack = animationStackDuration*1/Math.abs(val); 
      $('#cur_sp').text(text + ' x'+val);
      requestAnimationFrame(step_minute); 
   });  
}

$(function() {
    $('.play_anim_thumb').click(function() {
       stackplaying = true;
       minute_anim($(this).attr('data-rel'));
       $('.to_anim').css({'width':'683px','height':'395px'});
    });  
})

