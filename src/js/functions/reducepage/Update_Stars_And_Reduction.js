function update_star_and_reduction(callback) {
   var cmd_data = {
       json_file: json_file,          // Defined on the page + no-cache!!
       cmd: 'get_reduction_info'
   }

   loading({text:'Updating star list and reduction data...', overlay:true}); 
   
   // Remove All objects from Canvas
   remove_objects();

   $.ajaxSetup({ cache: false });
   $.ajax({ 
       url:  "/pycgi/webUI.py",
       data: cmd_data,
       success: function(data) {
       
           var json_resp = $.parseJSON(data); 
 
 
           if(json_resp['status']!==0) {
            
               // Remove All objects from Canvas
               remove_objects();
               
               
               // Update Stars
               update_stars_on_canvas_and_table(json_resp);
               
             
 
               // Update Reduction
               //update_reduction_on_canvas_and_table(json_resp);
               
               

               // Reload the actions
               //reduction_table_actions();

               // Callback (optional)
               typeof callback === 'function' && callback();
           }

           loading_done();
          

       }, error: function(data) {
           
           loading_done();
           bootbox.alert({
               message: "Something went wrong with this detection.",
               className: 'rubberBand animated error',
               centerVertical: true 
           });
       }
   });

}

$(function() {
   // Manual
   $('#refresh_data').click(function(){
       update_star_and_reduction();
   });
})