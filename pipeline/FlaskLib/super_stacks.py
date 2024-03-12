from flask import Flask, request
from FlaskLib.FlaskUtils import get_template, make_default_template
from FlaskLib.Pagination import get_pagination
import time

import glob
from lib.PipeUtil import load_json_file, save_json_file, cfe, get_file_info
from lib.PipeAutoCal import fn_dir

def stacks_main(amsid, data) :
   remote = 1
   json_file = "/mnt/ams2/SD/proc2/json/" + "main-index.json"
   json_conf = load_json_file("../conf/as6.json")
   if cfe("/mnt/ams2/meteors", 1) == 0:
      return("Problem: data drive is not mounted. ")
   if cfe(json_file) == 0:
      return("Problem: main index file doesn't exist. ")
   stats_data = load_json_file(json_file)

   del_cams = [] 
   for cam in json_conf['cameras']:
      print(cam, json_conf['cameras'][cam])
      if "status" in json_conf['cameras'][cam]:
         if json_conf['cameras'][cam]['status'] == "disabled":
            del_cams.append(cam)

   if data['stack_type'] is not None:
      stack_type = data['stack_type']
      json_conf['stack_type'] = stack_type
      save_json_file("../conf/as6.json", json_conf)
   else:
      stack_type = "default"

   if stack_type == "default":
      toggle = "<a href=?stack_type=night>Show Night Stacks Only</a>"
   else:
      toggle = "<a href=?stack_type=default>Show All Stacks</a>"

   if stats_data == 0:
      return("Problem: main index file is corrupted. ")

   out = """
      <div class='h1_holder d-flex justify-content-between'>
         <h1>Review Stacks by Day </h1>""" + toggle + """
           
         <!--<input value='' type='text' data-display-format='YYYY/MM/DD'  data-action='reload' data-url-param='limit_day' data-send-format='YYYY_MM_DD' class='datepicker form-control'></h1>
         <div class='page_h'>Page  1/10</div>-->
      </div>
         <div id='main_container' class='container-fluid h-100 mt-4 lg-l'>
   """
   if data['days_per_page'] is not None:
      days_per_page = int(data['days_per_page'])
   else:
      days_per_page = 10

   if data['p'] is not None:
      page = int(data['p'])
   else:
      page = 1



   sdirs = glob.glob("/mnt/ams2/meteor_archive/" + amsid + "/STACKS/*")


   pagination = get_pagination(page, len(sdirs), "/stacks/" + amsid + "/?days_per_page=" + str(days_per_page), days_per_page)

   start_ind = (page - 1) * days_per_page
   end_ind = start_ind + days_per_page
   if end_ind > len(sdirs):
      end_ind = len(sdirs)



   template = make_default_template(amsid, "super_stacks_main.html", json_conf)


   if "stack_type" in json_conf:
      stack_type = json_conf['stack_type']
   else:
      stack_type = "default"
   if data['stack_type'] is not None:
      stack_type = data['stack_type']


   rand = str(time.time())
   for sdir in sorted(sdirs, reverse=True)[start_ind:end_ind]:
      vdir = sdir.replace("/mnt/ams2", "")
      if cfe(sdir,1) == 1:
         stack_day, trash = fn_dir(sdir)
         if stack_day in stats_data:
            data = stats_data[stack_day]
            mets = data['meteor_files']
            non_meteors = data['failed_files']
         else:
            #continue
            non_meteors = "???"
            mets = "???"
         date = stack_day
         dsp_date = date.replace("_", "/")
         out += """
         <div class='h2_holder d-flex justify-content-between'>
	       <h2>""" + dsp_date + """ 
               - <a class='btn btn-primary' href=/meteor/""" + amsid + "/?start_day=" + date + ">" + str(mets) + """ Meteors </a>
	      </h2><p><a href=/trash/""" + amsid + "/?start_day=" + date + """>""" + str(non_meteors) + """ Non-Meteors </a>  </a>
         </div>
         Night Stacks
         <div class='gallery gal-resize row text-center text-lg-left mb-5'>
         """

         for cam in json_conf['cameras']:
            cams_id = json_conf['cameras'][cam]['cams_id']
            print(json_conf['cameras'][cam])
            if "status" in json_conf['cameras'][cam]:
               if json_conf['cameras'][cam]['status'] == "disabled":
                  continue
            night_stack_file = vdir + "/" + cams_id + "-night-stack.jpg"
            print("NIGHT STACK FILE!", night_stack_file)
            if cfe("/mnt/ams2/" + night_stack_file) == 0:
               print("NOT FOUND NIGHT", "/mnt/ams2/" + night_stack_file)
               night_stack_file = "/blank.jpg"               
            else:
               print("FOUND", "/mnt/ams2/" + night_stack_file)
            if cams_id in data:
               minutes = data[cams_id]
            else:
               minutes = ""
            out += """
	       <div class='preview'>
	          <a class='mtt' href='/stacks_day/""" + amsid + "/" + date + """/' title='Browse all day'>
                  <img width=320 height=180 alt='""" + date + """' class='img-fluid ns lz' src='""" + night_stack_file + """?""" + rand + """'>
                  </a><span class='pre-b'>Cam #""" + cams_id + " " + str(minutes) + """ minutes</span>
               </div>
            """
         out += "</div>"
         if stack_type == "default":
            # Dusk
            out += """
               Dusk Stacks
               <div class='gallery gal-resize row text-center text-lg-left mb-5'>
            """


            for cam in json_conf['cameras']:
               cams_id = json_conf['cameras'][cam]['cams_id']
               dusk_stack_file = vdir + "/" + cams_id + "-dusk-stack.jpg"
               print("DUSK STACK FILE!", dusk_stack_file)
               if cfe("/mnt/ams2/" + dusk_stack_file) == 0:
                  print("NOT FOUND DUSK" + dusk_stack_file)
                  dusk_stack_file = "/blank.jpg" 
               else:
                  print("FOUND", dusk_stack_file)
               if cams_id in data:
                  minutes = data[cams_id]
               else:
                  minutes = ""
            
               out += """
	          <div class='preview'>
	             <a class='mtt' href='/stacks_day/""" + amsid + "/" + date + """/' title='Browse all day'>
                     <img width=320 height=180 alt='""" + date + """' class='img-fluid ns lz' src='""" + dusk_stack_file + """?""" + rand + """'>
                     </a><span class='pre-b'>Cam #""" + cams_id + " " + str(minutes) + """ minutes</span>
                  </div>
               """
            out += "</div>"


   
            out += """ Day Stacks <div class='gallery gal-resize row text-center text-lg-left mb-5'>"""
            for cam in json_conf['cameras']:
               cams_id = json_conf['cameras'][cam]['cams_id']
               day_stack_file = vdir + "/" + cams_id + "-day-stack.jpg"
               print("DAY STACK FILE!", day_stack_file)
               fsize, tdiff = get_file_info("/mnt/ams2" + day_stack_file)
               if cfe("/mnt/ams2" + day_stack_file) == 0 or fsize == 0:
                  print("NOT FOUND DAY", "/mnt/ams2/" + day_stack_file + " " + str(fsize))
                  day_stack_file = "/blank.jpg" 
               else:
                  print("FOUND", day_stack_file)
               if cams_id in data:
                  minutes = data[cams_id]
               else:
                  minutes = ""
               if day_stack_file is not None:
                  out += """
                  <div class='preview'>
                     <a class='mtt' href='/stacks_day/""" + amsid + "/" + date + """/' title='Browse all day'>
                     <img width=320 height=180 alt='""" + date + """' class='img-fluid ns lz' src='""" + day_stack_file + """?""" + rand + """'>
                     </a><span class='pre-b'>Cam #""" + cams_id + " " + str(minutes) + """ minutes</span>
                  </div>
                  """
            out += "</div>"

            # Dawn
            out += """
               Dawn Stacks
               <div class='gallery gal-resize row text-center text-lg-left mb-5'>
            """


            for cam in json_conf['cameras']:
               cams_id = json_conf['cameras'][cam]['cams_id']
               dawn_stack_file = vdir + "/" + cams_id + "-dawn-stack.jpg"
               print("DAWN STACK FILE!", "/mnt/ams2/" + dawn_stack_file)
               fsize, ftime = get_file_info("/mnt/ams2" + dawn_stack_file) 
               if cfe("/mnt/ams2/" + dawn_stack_file) == 0 or fsize == 0:
                  print("DAWN STACK NOT FOUND")
                  dawn_stack_file = "/blank.jpg"               
               else:
                  print("DAWN STACK FOUND", "/mnt/ams2/" + dawn_stack_file)
               if cams_id in data:
                  minutes = data[cams_id]
               else:
                  minutes = ""
            
               out += """
	          <div class='preview'>
	             <a class='mtt' href='/stacks_day/""" + amsid + "/" + date + """/' title='Browse all day'>
                     <img width=320 height=180 alt='""" + date + """' class='img-fluid ns lz' src='""" + dawn_stack_file + """?""" + rand + """'>
                     </a><span class='pre-b'>Cam #""" + cams_id + " " + str(minutes) + """ minutes</span>
                  </div>
               """
            out += "</div>"


   out += "</div><!--main container!--> <div class='page_h'><!--Page  " + format(page) + "/" +  format(pagination[2]) + "--></div></div> <!-- ADD EXTRA FOR ENDING MAIN PROPERLY. --> <div>"
   out += pagination[0]

         #all_stacks = glob.glob(sdir + "/*.jpg")
         #for img in all_stacks:
         #   out += img + "<BR>"

   #template = template.replace("{HEADER}", header)
   template = template.replace("{MAIN_TABLE}", out)
   #template = template.replace("{FOOTER}", footer)
   #template = template.replace("{NAV}", nav)
   template = template.replace("{AMSID}", amsid)
   if "obs_name" in json_conf:
      template = template.replace("{OBS_NAME}", json_conf['site']['obs_name'])
   else:
      template = template.replace("{OBS_NAME}", "")
   if "location" in json_conf:
      template = template.replace("{LOCATION}", json_conf['site']['location'])
   else:
      template = template.replace("{LOCATION}", "")
   return(template)

def stacks_day_hours(amsid, day, req):
   date = day
   header = get_template("FlaskTemplates/header.html")
   footer = get_template("FlaskTemplates/footer.html")
   nav = get_template("FlaskTemplates/nav.html")
   template = get_template("FlaskTemplates/super_stacks_main.html")
   json_conf = load_json_file("../conf/as6.json")
   sdirs = glob.glob("/mnt/ams2/meteor_archive/" + amsid + "/STACKS/*")

   out = ""
   glob_dir = "/mnt/ams2/meteor_archive/" + amsid + "/STACKS/" + day + "/"
   stack_files = glob.glob(glob_dir + day + "*.jpg")
   last_hour = None 
   
   for sf in sorted(stack_files, reverse=False):
      if "orig" in sf:
         continue
      vsf = sf.replace("/mnt/ams2", "")
      sfn,sd = fn_dir(sf)
     
      el = sfn.split("_")
      hour = el[3]
      cam = el[4].replace(".jpg", "")
      
     
      if last_hour is not None and last_hour != hour:
         out += "</div>"
      if last_hour != hour:
         dsp_date = day.replace("_", "/") + " " + hour + " UTC"
         out += """
         <div class='h2_holder d-flex justify-content-between'>
               <h2>""" + dsp_date + """
              </h2>  </a>
         </div>
         <div class='gallery gal-resize row text-center text-lg-left mb-5'>
         """
      out += """
            <div class='preview'>
               <a class='mtt' href='/stacks_hour/""" + amsid + "/" + date + """/""" + hour + """/' title='Browse hour'>
                  <img width=320 height=180 alt='""" + date + """' class='img-fluid ns lz' src='""" + vsf + """'>
               </a><span class='pre-b'>Cam #""" + cam + """ </span>
            </div>
      """

      last_hour  = hour


   template = template.replace("{MAIN_TABLE}", out)
   template = template.replace("{HEADER}", header)
   template = template.replace("{MAIN_TABLE}", out)
   template = template.replace("{FOOTER}", footer)
   template = template.replace("{NAV}", nav)
   template = template.replace("{AMSID}", amsid)
   if "obs_name" in json_conf:
      template = template.replace("{OBS_NAME}", json_conf['site']['obs_name'])
   else:
      template = template.replace("{OBS_NAME}", "")
   if "location" in json_conf:
      template = template.replace("{LOCATION}", json_conf['site']['location'])
   else:
      template = template.replace("{LOCATION}", "")


   return(template)

def stacks_hour(amsid, day, hour):
   date = day
   out = ""
   json_conf = load_json_file("../conf/as6.json")
   glob_dir = "/mnt/ams2/SD/proc2/" + day + "/" 
   stack_files = glob.glob(glob_dir + day + "_" + hour + "*.mp4")
   day_glob_dir = "/mnt/ams2/SD/proc2/daytime/" + day + "/" 
   day_stack_files = glob.glob(day_glob_dir + day + "_" + hour + "*.mp4")
   print(glob_dir)
   print(day_glob_dir)
   for dsf in day_stack_files:
      if "orig" in dsf:
         continue
      stack_files.append(dsf)
   min_files = {}
   template = make_default_template(amsid, "super_stacks_main.html", json_conf)

   del_cams = []
   for cam in json_conf['cameras']:
      print(cam, json_conf['cameras'][cam])
      if "status" in json_conf['cameras'][cam]:
         if json_conf['cameras'][cam]['status'] == "disabled":
            del_cams.append(cam)

   for sf in sorted(stack_files, reverse=False):
      if "orig" in sf:
         continue
      if "trim" in sf or "crop" in sf:
         continue
      fn, dir = fn_dir(sf)
      el = fn.split("_")
      min = el[4]
      cam = el[7].replace(".mp4", "")
      vsf = sf.replace("/mnt/ams2", "")
      sfn = fn.replace(".mp4", "-stacked-tn.jpg") 
      simg = dir + "images/" + sfn
      vsimg = simg.replace("/mnt/ams2", "")
      #out += fn + "<BR>"
      if min not in min_files:
         min_files[min] = {}
         for cam_num in sorted(json_conf['cameras']):
            if cam_num in del_cams:
               continue
            cams_id = json_conf['cameras'][cam_num]['cams_id']
            min_files[min][cams_id] = ""
      min_files[min][cam] = vsimg 


   for min in sorted(min_files.keys()):

      dsp_date = day.replace("_", "/") + " " + hour + " " + min + " UTC"
      out += """
      <div class='h2_holder d-flex justify-content-between'>
         <h2>""" + dsp_date + """
         </h2>  </a>
      </div>
      <div class='gallery gal-resize row text-center text-lg-left mb-5'>
      """

      for cam in min_files[min]:
         #print(cam, min_files[min][cam])
         min_file, min_dir = fn_dir(min_files[min][cam])
         min_link = min_file.replace("-stacked-tn.jpg", "")
         out += """
            <div class='preview'>
                  <a class='mtt' href='/min_detail/""" + amsid + "/" + date + "/" + min_link + """/' title='View Minute'>
                  <img width=320 height=180 alt='""" + date + """' class='img-fluid ns lz' src='""" + min_dir + min_file + """'>
                  </a><span class='pre-b'>Cam #""" + cam + """</span>
            </div>
         """
      out += "</div>"

   template = template.replace("{MAIN_TABLE}", out)

   return(template)

def make_default_template_old(amsid, main_template, json_conf):
   header = get_template("FlaskTemplates/header.html")
   footer = get_template("FlaskTemplates/footer.html")
   nav = get_template("FlaskTemplates/nav.html")
   template = get_template("FlaskTemplates/" + main_template  )
   template = template.replace("{HEADER}", header)
   template = template.replace("{FOOTER}", footer)
   template = template.replace("{NAV}", nav)
   template = template.replace("{AMSID}", amsid)
   if "obs_name" in json_conf:
      template = template.replace("{OBS_NAME}", json_conf['site']['obs_name'])
   else:
      template = template.replace("{OBS_NAME}", "")
   if "location" in json_conf:
      template = template.replace("{LOCATION}", json_conf['site']['location'])
   else:
      template = template.replace("{LOCATION}", "")
   return template

 
