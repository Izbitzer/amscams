#!/usr/bin/python3 

import numpy as np
import sys
from lib.PipeUtil import load_json_file, save_json_file , mfd_roi, get_file_info
import os
import cv2
from lib.ASAI_Predict import predict_images
import glob
import tensorflow as tf
import os
from tensorflow import keras
from tensorflow.keras.models import *
import tensorflow.keras
from tensorflow.keras.models import load_model
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img

img_height = 150
img_width = 150
selected_class = "meteors"
data_dir = "/mnt/ams2/datasets/learning/scan_results/" + selected_class + "/"

# LABELS
labels = load_json_file("labels.json")
class_names = sorted(labels['labels'])

def load_my_model(model_file = None):
   if model_file is None:
      model_file = "multi_class_model.h5"

   model = Sequential()

   model =load_model(model_file)
   model.compile(loss='categorical_crossentropy',
      optimizer='rmsprop',
      metrics=['accuracy'])
   return(model)

def predict_image(imgfile, model):
   firefly_months = ['6', '7', '8']
   firefly_stations = ['AMS1', 'AMS7', 'AMS9', 'AMS15', 'AMS41', 'AMS42', 'AMS48']
   fel = imgfile.split("_")
   img_month = fel[2] 
   station_id = fel[0] 

   #img = keras.utils.load_img(
   img = load_img(
      imgfile, target_size=(img_height, img_width)
   )
   show_img = cv2.imread(imgfile)
   img_array = img_to_array(img)
   img_array = tf.expand_dims(img_array, 0) # Create a batch

   predictions = model.predict(img_array)

   score = tf.nn.softmax(predictions[0])

   score_list = np.argsort(-score)


   #confidence = int(100 * np.max(score))



   print("SCORE:", score_list)

   predicted_class = class_names[np.argmax(score)]

   predicted_class_one = class_names[score_list[0]]
   predicted_class_two = class_names[score_list[1]]
   predicted_class_three = class_names[score_list[2]]

   conf1 = int(100 * score[score_list[0]])
   conf2 = int(100 * score[score_list[1]])
   conf3 = int(100 * score[score_list[2]])

   if predicted_class_one == "fireflies" or predicted_class_one == "firefilies":
      if img_month not in firefly_months:
         predicted_class_one = "meteor_bright_dashed"
      if station_id not in firefly_stations:
         predicted_class_one = "meteor_bright_dashed"

   print("0", predicted_class,  int(100 * np.max(score)))

   print(predicted_class_one, conf1)
   print(predicted_class_two, conf2)
   print(predicted_class_three, conf3)

   confidence = int(100 * np.max(score))

   print(
       "This image most likely belongs to {} with a {:.2f} percent confidence."
       .format(class_names[np.argmax(score)], 100 * np.max(score))
   )
   resp_data = [
      [predicted_class_one, conf1],
      [predicted_class_two, conf2],
      [predicted_class_three, conf3]
   ]
   return(resp_data)

def which_cnts(cnt_res):
   if len(cnt_res) == 3:
      (_, cnts, xx) = cnt_res
   elif len(cnt_res) == 2:
      (cnts, xx) = cnt_res
   return(cnts)

def check_roi(roi_img, roi_file):
   # check the roi and make sure it is not cropped too tight (there should be some margin around the object)
   # if the obj is flush with the edges make the ROI bigger

   station_id = roi_file.split("/")[-1].split("_")[0]
   rfn = roi_file.split("/")[-1]
   meteor_file = roi_file.split("/")[-1].replace(station_id + "_", "").replace("-ROI.jpg", ".json")
   mdir = "/mnt/ams2/meteors/" + meteor_file[0:10] + "/" 
   msdir = "/mnt/ams2/METEOR_SCAN/" + meteor_file[0:10] + "/" 
   mjrf = meteor_file.replace(".json", "-reduced.json")
   stack_file = mjrf.replace("-reduced.json", "-stacked.jpg")
   if os.path.exists(mdir + mjrf) is False:
      print("NO FILE:", mdir + mjrf)
      return()
   mjr = load_json_file(mdir + mjrf)
   if "meteor_frame_data" not in mjr:
      print("NO MFD!")
      return()   
   if len(mjr['meteor_frame_data']) == 0:
      print("0 FRAME MFD!")
      return()   
   x1,y1,x2,y2 = mfd_roi(mjr['meteor_frame_data'])


   if len(roi_img.shape) > 2:
      gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
   else:
      gray = roi_img
   min_val, max_val, min_loc, (mx,my)= cv2.minMaxLoc(gray) 
   thresh_val = max_val * .7
   _, thresh_img = cv2.threshold(gray.copy(), thresh_val, 255, cv2.THRESH_BINARY)
   cv2.imwrite("/mnt/ams2/test.jpg", thresh_img)
   print("MAX VAL:", max_val)
   if True:
      xs = []
      ys = []
      cnt_res = cv2.findContours(thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
      cnts = which_cnts(cnt_res)

      conts = []
      for (i,c) in enumerate(cnts):
         x,y,w,h = cv2.boundingRect(cnts[i])
         intensity = int(np.sum(gray[y:y+h,x:x+w]))
         px_avg = intensity / (w*h)
         if w >= 1 and h >= 1 and px_avg > 3:
            conts.append((x,y,w,h,intensity,px_avg))
            xs.append(x)
            xs.append(x+w)
            ys.append(y)
            ys.append(y+h)
   min_x = min(xs)
   min_y = min(ys)
   max_x = max(xs)
   max_y = max(ys)
   h,w = roi_img.shape[:2]
   x_left_margin = min_x
   x_right_margin = w - max_x 
   y_top_margin = min_y
   y_bottom_margin = h - max_y 
   print("MARGIN X:", x_left_margin, x_right_margin)
   print("MARGIN Y:", y_top_margin, y_bottom_margin)
   print("CONT:", conts)
   if x_left_margin >= 10 and x_right_margin >= 10 and y_top_margin > 10 and y_bottom_margin > 10:
      print("ROI MARGINS GOOD!")
      
      return(roi_img)
   else:
      print("ROI MARGIN IS TOO SMALL!")
      print("ORG X1,Y1,X2,Y2:", x1,y1,x2,y2)
      ex = int(w * .25)
      ey = int(h * .25)
      if ex >= ey:
         ey = ex
      else:
         ex = ey
      x1,y1,x2,y2 = mfd_roi(mjr['meteor_frame_data'], None, None, ex, ey)
      print("EX EY:", ex, ey)
      print("NEW X1,Y1,X2,Y2:", x1,y1,x2,y2)
      # Add a buffer of 25 px to the MFD and remake the x1,y1
      print("READ ", mdir +stack_file)
      img = cv2.imread(mdir + stack_file)
      img = cv2.resize(img, (1920,1080))
      roi_img = img[y1:y2,x1:x2]
      cv2.imwrite("/mnt/ams2/test2.jpg", roi_img)
      print("SAVED NEW ROI FILE")
      cv2.imwrite(roi_file, roi_img)
      if "trim-0296" in roi_file:
         print("ROI:", roi_file)

      #cv2.imwrite(learning_file, roi_img)
      return(roi_img)

def remake_roi(meteor_file):
   mdir = "/mnt/ams2/meteors/" + meteor_file[0:10] + "/" 
   msdir = "/mnt/ams2/METEOR_SCAN/" + meteor_file[0:10] + "/" 
   mjrf = meteor_file.replace(".json", "-reduced.json")
   stack_file = mjrf.replace("-reduced.json", "-stacked.jpg")
   if os.path.exists(mdir + mjrf) is False:
      print("NO FILE:", mdir + mjrf)
      return()
   mjr = load_json_file(mdir + mjrf)
   roi_file = meteor_file.replace(".json", "-ROI.jpg")
   if "meteor_frame_data" not in mjr:
      print("NO MFD!")
      return()   
   if len(mjr['meteor_frame_data']) == 0:
      print("0 FRAME MFD!")
      return()   
   x1,y1,x2,y2 = mfd_roi(mjr['meteor_frame_data'])
   img = cv2.imread(mdir + stack_file)
   nw = x2 - x1
   nh = y2 - y1
   if nw != nh:
      print("W/H CROP PROBLEM!", msdir + roi_file)
      input("wait")
      print(mdir + stack_file)
   try:
      img = cv2.resize(img, (1920,1080))
      roi_img = img[y1:y2,x1:x2]
   except:
      print("Failed to make image!", mdir + stack_file )
      return() 

   try:
      #cv2.imshow('pepe', roi_img)
      #cv2.waitKey(30)
      cv2.imwrite(msdir + roi_file, roi_img)
      print("SAVED:", msdir + roi_file )
   except:
      print("FAILED TO MAKE ROI")

def fix_repo_images():
   shape_file = "/mnt/ams2/datasets/repo_shapes.json"
   if os.path.exists(shape_file) is True:
      shapes = load_json_file(shape_file)
   else:
      shapes = {}
   meteor_files = glob.glob("/mnt/ams2/datasets/images/repo/nonmeteors/*")
   #non_meteor_files = glob.glob("/mnt/ams2/datasets/images/repo/nonmeteors/*")
   cc = 0
   for mf in meteor_files:

      fn = mf.split("/")[-1]
      bad = 0
      if fn in shapes:
         w,h = shapes[fn]
      else:
         img = cv2.imread(mf)
         try:
            h,w = img.shape[:2]
         except:
            bad = 1
      if w != h:
         #print("BAD CROP:", fn, h,w)
         bad = 1
      #if w < 150 or h < 150:
         #print("BAD SIZE:", fn, h,w)
         #bad = 1
      shapes[fn] = [w,h]
      if bad == 1:
         cmd = "mv " + mf + " " + "/mnt/ams2/datasets/images/repo/bad/"
         print(cmd)
         os.system(cmd)
         if fn in shapes:
            del shapes[fn]

      print(w,h)
      cc += 1
   save_json_file(shape_file, shapes)
      


def get_mfiles(mdir):
   temp = glob.glob(mdir + "/*.json")
   mfiles = []
   for json_file in temp:
      if "import" not in json_file and "report" not in json_file and "reduced" not in json_file and "calparams" not in json_file and "manual" not in json_file and "starmerge" not in json_file and "master" not in json_file:
         vfn = json_file.split("/")[-1].replace(".json", ".mp4")
         mfiles.append(vfn)
   return(mfiles)

def mfd_roi_old(mfd=None, xs=None, ys=None):
   if mfd is not None:
      if len(mfd) == 0:
         return(0,0,1080,1080)
      xs = [row[2] for row in mfd]
      ys = [row[3] for row in mfd]
   x1 = min(xs) 
   y1 = min(ys) 
   x2 = max(xs) 
   y2 = max(ys) 
   mx = int(np.mean(xs))
   my = int(np.mean(ys))
   w = x2 - x1
   h = y2 - y1
   if w >= h:
      h = w
   else:
      w = h 
   if w < 150 or h < 150:
      w = 150
      h = 150
   if w > 1079 or h > 1079 : 
      w = 1060
      h = 1060 
   x1 = mx - int(w / 2)
   x2 = mx + int(w / 2)
   y1 = my - int(h / 2)
   y2 = my + int(h / 2)
   w = x2 - x1
   h = y2 - y1
   print("WH:", w,h)
   print("WH:", w,h)

   if x1 < 0:
      x1 = 0
      x2 = w
   if y1 < 0:
      y1 = 0
      y2 = h
   if x2 >= 1920:
      x2 = 1919 
      x1 = 1919 - w
   if y2 >= 1080:
      y2 = 1079 
      y1 = 1079 - h
   return(x1,y1,x2,y2)

def load_meteors_for_day(date, station_id):
   dataset_dir = "/mnt/ams2/datasets/"
   if os.path.isdir(dataset_dir) is False:
      os.makedirs(dataset_dir)
   if os.path.isdir(dataset_dir + "/images/") is False:
      os.makedirs(dataset_dir + "/images/")
   if os.path.isdir(dataset_dir + "/images/repo/") is False:
      os.makedirs(dataset_dir + "/images/repo/")
   if os.path.isdir(dataset_dir + "/images/repo/meteors/") is False:
      os.makedirs(dataset_dir + "/images/repo/meteors/")
   if os.path.isdir(dataset_dir + "/images/repo/nonmeteors/") is False:
      os.makedirs(dataset_dir + "/images/repo/nonmeteors/")
   if os.path.isdir(dataset_dir + "/images/repo/trash/") is False:
      os.makedirs(dataset_dir + "/images/repo/trash/")
   

   human_data_file = "/mnt/ams2/datasets/human_data.json"
   label = "meteors"
   machine_data_file = "/mnt/ams2/datasets/machine_data.json"
   if os.path.exists(human_data_file):
      human_data = load_json_file(human_data_file)
   else:
      human_data = {}

   mdir = "/mnt/ams2/meteors/" + date + "/"
   msdir = "/mnt/ams2/METEOR_SCAN/" + date + "/"

   ai_day_file = mdir + station_id + "_" + date + "_AI_SCAN.info"
   if os.path.exists(ai_day_file):
      ai_day_data = load_json_file(ai_day_file)
   else:
      ai_day_data = {}


   if os.path.isdir(msdir) is False:
      os.makedirs(msdir)
   mfiles = get_mfiles(mdir)
   if len(ai_day_data) == len(mfiles):
      print("This day has already been completed!")
      return([])


   roi_files = []
   for ff in sorted(mfiles, reverse=True):
      print(ff)
      if "/" in ff:
         ff = ff.split("/")[-1]
      if "\\" in ff:
         ff = ff.split("\\")[-1]
      json_file = ff.replace(".mp4", ".json")
      roi_file = station_id + "_" + ff.replace(".mp4", "-ROI.jpg")
       
      if roi_file in machine_data:
         print("DONE ALREADY, DOING AGAIN!", roi_file)
         #continue
      else:
         print(roi_file, " NOT IN machine data!")
      stack_file = ff.replace(".mp4", "-stacked.jpg")
      mjrf = json_file.replace(".json", "-reduced.json")
      remake = 0
      roi = None
      if os.path.exists(msdir + roi_file) is True:
         roi = cv2.imread(msdir + roi_file)
         if roi is None:
            print("BAD ROI IMAGE!")
            continue
         if roi.shape[0] < 150 or roi.shape[1] < 150:
            print("BAD ROI SHAPE REMAKE!")
            remake = 1
         if roi.shape[0] != roi.shape[1]:
            remake = 1
            print("BAD SHAPE:", msdir + roi_file)
         print("CHECKROI")
      if os.path.exists(msdir + roi_file) is True:
         if roi is None:
            roi = cv2.imread(msdir + roi_file)
         roi = check_roi(roi, msdir + roi_file)
      if remake == 1:
         print("REMAKE ROI:", msdir + roi_file)
      if os.path.exists(msdir + roi_file) is False or remake == 1:
         if os.path.exists(mdir + mjrf):
            try:
               mjr = load_json_file(mdir + mjrf)      
            except:
               continue
            if "meteor_frame_data" not in mjr:
               continue
            #print("MFD:", len(mjr['meteor_frame_data']))
            if len(mjr['meteor_frame_data']) == 0:
               continue
               

            x1,y1,x2,y2 = mfd_roi(mjr['meteor_frame_data'])
            img = cv2.imread(mdir + stack_file)
            nw = x2 - x1
            nh = y2 - y1
            if roi_file not in ai_day_data:
               ai_day_data[roi_file] = {}
               ai_day_data[roi_file]['roi'] = [x1,y1,x2,y2]
            if nw != nh:
               print("W/H CROP PROBLEM!", msdir + roi_file)
               input("wait")
            print(mdir + stack_file)
            try:
               img = cv2.resize(img, (1920,1080))
               roi_img = img[y1:y2,x1:x2]
            except:
               continue
 
            try:
               #cv2.imshow('pepe', roi_img)
               #cv2.waitKey(30)
               cv2.imwrite(msdir + roi_file, roi_img)
            except:
               continue
         else:
            print("NOT REDUCED :", mdir , mjrf)
      else:
         print("GOOD ROI !", msdir + roi_file)
      if os.path.exists(msdir + roi_file) is True:
         if roi_file not in human_data : 
            roi_files.append(msdir + roi_file)
   model = "./first_try_model.h5"
   label = "meteors"
   print(len(roi_files), " ROI FILES READY TO ANALYZE")
   save_json_file(ai_day_file, ai_day_data)
   return(roi_files, ai_day_data)
   #predict_images(roi_files, model, label )


if __name__ == "__main__":
   model = load_my_model()
   json_conf = load_json_file("../conf/as6.json")
   station_id = json_conf['site']['ams_id']
   date = sys.argv[1]

   if date == "all" or date == "ALL":
      all_days = glob.glob("/mnt/ams2/meteors/*")
      for daydir in sorted(all_days, reverse=True):
         print(daydir)
         if os.path.isdir(daydir) is True:
            if "/" in daydir:
               date = daydir.split("/")[-1]
            if "\\" in daydir:
               date = daydir.split("\\")[-1]
            print(date)
            mdir = "/mnt/ams2/meteors/" + date + "/"
            ai_day_file = mdir + station_id + "_" + date + "_AI_SCAN.info"


           # cmd = "python3.6 AI_Scan_Meteors.py " + date
           # print(cmd)
           # os.system(cmd)

            machine_data_file = "/mnt/ams2/datasets/" + station_id + "_ML_DATA.json"
            #human_data_file = "/mnt/ams2/datasets/human_data.json"
            print(machine_data_file)
            if os.path.exists(machine_data_file) is True:
               machine_data = load_json_file(machine_data_file)
            else:
               machine_data = {}

            roi_files,ai_day_data = load_meteors_for_day(date, station_id)
            for roi_file in roi_files:
               try:
                  predict_top3 = predict_image(roi_file, model)
                  predict_class, confidence = predict_top3[0] 
                  predict_class2, confidence2 = predict_top3[1] 
                  predict_class3, confidence3 = predict_top3[2] 
               except: 
                  predict_class = "BAD_IMAGE"
               roi_fn = roi_file.split("/")[-1]
               if roi_fn not in ai_day_data:
                  ai_day_data[roi_fn] = {}
               ai_day_data[roi_fn]['predict_top3'] = predict_top3 

               tdir = data_dir + predict_class + "/"
               roi_fn = roi_file.split("/")[-1]
               new_file = tdir + roi_fn
               if os.path.exists(tdir) is False:
                  os.makedirs(tdir)
                  print("mkdir", tdir)
               cmd = "cp " + roi_file + " " + new_file
               os.system(cmd)
               print(cmd)
               print(roi_file, predict_class)
               machine_data[roi_fn] = predict_class
            save_json_file(machine_data_file, machine_data)
            save_json_file(ai_day_file, ai_day_data)
            print("saved:", machine_data_file)
            print("saved:", ai_day_file)

      cmd = "cd /mnt/ams2/datasets/learning/; tar -cvf " + station_id + "_ML_REPO.tar * ; gzip -f " + station_id + "_ML_REPO.tar"
      print(cmd)
      #os.system(cmd)
      if os.path.exists("/mnt/archive.allsky.tv/" + station_id + "/ML/") is False:
         os.makedirs("/mnt/archive.allsky.tv/" + station_id + "/ML/")
      cmd = "cd /mnt/ams2/datasets/learning/; cp " + station_id + "_ML_REPO.tar.gz /mnt/archive.allsky.tv/" + station_id + "/ML/"
      print(cmd)
      #os.system(cmd)
 


            #roi_files = load_meteors_for_day(date, station_id)
            #for roi_file in roi_files:
            #   print(roi_file)
   elif date == "remake_roi":
      remake_roi(sys.argv[2])


   elif date == "fix_repo":
      fix_repo_images()
   elif date == "repo":
      print("GET ALL REPO METEOR FILES...")
      human_data_file = "/mnt/ams2/datasets/human_data.json"
      label = "meteors"
      machine_data_file = "/mnt/ams2/datasets/" + station_id + "_ML_DATA.json"
      if os.path.exists(human_data_file):
         human_data = load_json_file(human_data_file)
      else:
         human_data = {}
      if os.path.exists(machine_data_file):
         machine_data = load_json_file(machine_data_file)
      else:
         machine_data = {}

      all_repo_meteors = glob.glob("/mnt/ams2/datasets/images/repo/meteors/*")
      model = "./first_try_model.h5"
      label = "meteors"
      roi_files = []
      roi_files_done = []
      rc = 0
      mc = 0
      for rfile in all_repo_meteors:
         roi_file = rfile.split("/")[-1]
         if roi_file not in machine_data :
            print(rc, "NEW ROI FILE THAT HAS NOT BEEN EXAMINED YET:", roi_file)
            roi_files.append(rfile)
            rc += 1
         else:
            print(mc, "CURRENT MACHINE LABEL/SCORE:", roi_file, machine_data[roi_file])
            roi_files_done.append(rfile)
            mc += 1

      print(len(all_repo_meteors), " TOTAL ROI FILES IN REPO")
      print(len(roi_files), " METEOR ROI FILES NEEDING ML PREDICT")
      print(len(roi_files_done), " METEOR ROI FILES ALREADY DONE")
      predict_images(roi_files, model, label )

      print("GET ALL REPO NON METEOR FILES...")
      all_repo_nonmeteors = glob.glob("/mnt/ams2/datasets/images/repo/nonmeteors/*")
      print(len(all_repo_nonmeteors), " METEOR ROI FILES READY TO ANALYZE")
      label = "nonmeteors"
      predict_images(all_repo_nonmeteors, model, label )


      
   else:

      mdir = "/mnt/ams2/meteors/" + date + "/" 
      ai_day_file = mdir + station_id + "_" + date + "_AI_SCAN.info"
      if os.path.exists(ai_day_file):
         ai_day_data = load_json_file(ai_day_file)
      else:
         ai_day_data = {}

      #load_meteors_for_day(date, station_id)
      machine_data_file = "/mnt/ams2/datasets/" + station_id + "_ML_DATA.json"
      #human_data_file = "/mnt/ams2/datasets/human_data.json"
      if os.path.exists(machine_data_file) is True:
         machine_data = load_json_file(machine_data_file)
      else:
         machine_data = {}

      roi_files, ai_day_data = load_meteors_for_day(date, station_id)
      for roi_file in roi_files:
         print(roi_file)
         roi_fn = roi_file.split("/")[-1]
         predict_top3 = predict_image(roi_file, model)
         predict_class, confidence = predict_top3[0] 
         predict_class2, confidence2 = predict_top3[1] 
         predict_class3, confidence3 = predict_top3[2] 


         if roi_fn not in ai_day_data:
            ai_day_data[roi_fn] = {}
         ai_day_data[roi_fn]['predict_top3'] = predict_top3 


         tdir = data_dir + predict_class + "/"
         roi_fn = roi_file.split("/")[-1]
         new_file = tdir + roi_fn
         if os.path.exists(tdir) is False:
            os.makedirs(tdir)
            print("mkdir", tdir)
         cmd = "cp " + roi_file + " " + new_file
         os.system(cmd)
         print(cmd)
         print(roi_file, predict_class)
         machine_data[roi_fn] = predict_class
      save_json_file(machine_data_file, machine_data)
      save_json_file(ai_day_file, ai_day_data)
      print("saved:", machine_data_file)


#data_dir = "/mnt/ams2/datasets/learning/scan_results/" + selected_class + "/"

