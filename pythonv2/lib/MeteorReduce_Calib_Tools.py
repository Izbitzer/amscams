import math
import glob
import re
import sys

from datetime import datetime,timedelta
from lib.MeteorReduce_Tools import name_analyser, get_datetime_from_analysedname
from lib.VIDEO_VARS import HD_W, HD_H
from lib.REDUCE_VARS import *

# TO DELETE 
from lib.UtilLib import convert_filename_to_date_cam, bound_cnt, check_running,date_to_jd, angularSeparation , calc_dist, better_parse_file_date



# Convert Y, M, d into JD Date
def date_to_jd(year,month,day):
    """
    Convert a date to Julian Day.
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet',
        4th ed., Duffet-Smith and Zwart, 2011.
    Parameters
    ----------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.
    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.
    day : float
        Day, may contain fractional part.
    Returns
    -------
    jd : float
        Julian Day
    Examples
    --------
    Convert 6 a.m., February 17, 1985 to Julian Day
    >>> date_to_jd(1985,2,17.25)
    2446113.75
    """
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month

    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if ((year < 1582) or
        (year == 1582 and month < 10) or
        (year == 1582 and month == 10 and day < 15)):
        # before start of Gregorian calendar
        B = 0
    else:
        # after start of Gregorian calendar
        A = math.trunc(yearp / 100.)
        B = 2 - A + math.trunc(A / 4.)

    if yearp < 0:
        C = math.trunc((365.25 * yearp) - 0.75)
    else:
        C = math.trunc(365.25 * yearp)

    D = math.trunc(30.6001 * (monthp + 1))

    jd = B + C + D + day + 1720994.5

    return jd




# TEST
def XYtoRADec(img_x,img_y,analysed_name,json_file):

   #def XYtoRADec(img_x,img_y,cal_file,cal_params,json_conf):
   #hd_datetime, hd_cam, hd_date, hd_y, hd_m, hd_d, hd_h, hd_M, hd_s = convert_filename_to_date_cam(cal_file)
   hd_datetime, hd_cam, hd_date, hd_y, hd_m, hd_d, hd_h, hd_M, hd_s = convert_filename_to_date_cam(analysed_name['name'])
   
   print('Year    ' +  str(hd_y) +"<br>")
   print('Mpnth   ' +  str(hd_m)+"<br>")
   print('Day     ' +  str(hd_d)+"<br>")
   print('Hour    ' +  str(hd_h)+"<br>")
   print('Minute     ' +  str(hd_M)+"<br>") 


  

   
   F_scale = 3600/float(json_file['scale_px'])
   #F_scale = 24

   total_min = (int(hd_h) * 60) + int(hd_M)
   day_frac = total_min / 1440 
   hd_d = int(hd_d) + day_frac
   jd = date_to_jd(int(hd_y),int(hd_m),float(hd_d))

   lat = float(json_conf['site']['device_lat'])
   lon = float(json_conf['site']['device_lng'])

   # Calculate the reference hour angle
   T = (jd - 2451545.0)/36525.0
   Ho = (280.46061837 + 360.98564736629*(jd - 2451545.0) + 0.000387933*T**2 \
      - (T**3)/38710000.0)%360

   x_poly_fwd = json_file['calib']['poly']['x_fwd']
   y_poly_fwd = json_file['calib']['poly']['y_fwd']
   
   dec_d = float(json_file['calib']['device']['center']['dec']) 
   RA_d  = float(json_file['calib']['device']['center']['ra']) 

   dec_d = dec_d + (x_poly_fwd[13] * 100)
   dec_d = dec_d + (y_poly_fwd[13] * 100)

   RA_d = RA_d + (x_poly_fwd[14] * 100)
   RA_d = RA_d + (y_poly_fwd[14] * 100)

   pos_angle_ref = float(json_file['calib']['device']['angle']) + (1000*x_poly_fwd[12]) + (1000*y_poly_fwd[12])

   # Convert declination to radians
   dec_rad = math.radians(dec_d)

   # Precalculate some parameters
   sl = math.sin(math.radians(lat))
   cl = math.cos(math.radians(lat))
 
   x_det = img_x - int(HD_W)/2
   y_det = img_y - int(HD_H)/2

   dx = (x_poly_fwd[0]
      + x_poly_fwd[1]*x_det
      + x_poly_fwd[2]*y_det
      + x_poly_fwd[3]*x_det**2
      + x_poly_fwd[4]*x_det*y_det
      + x_poly_fwd[5]*y_det**2
      + x_poly_fwd[6]*x_det**3
      + x_poly_fwd[7]*x_det**2*y_det
      + x_poly_fwd[8]*x_det*y_det**2
      + x_poly_fwd[9]*y_det**3
      + x_poly_fwd[10]*x_det*math.sqrt(x_det**2 + y_det**2)
      + x_poly_fwd[11]*y_det*math.sqrt(x_det**2 + y_det**2))

   # Add the distortion correction
   x_pix = x_det + dx 

   #print("ORIG X:", img_x)
   #print("X DET:", x_det)
   #print("DX :", dx)
   #print("NEWX :", x_pix)

   dy = (y_poly_fwd[0]
      + y_poly_fwd[1]*x_det
      + y_poly_fwd[2]*y_det
      + y_poly_fwd[3]*x_det**2
      + y_poly_fwd[4]*x_det*y_det
      + y_poly_fwd[5]*y_det**2
      + y_poly_fwd[6]*x_det**3
      + y_poly_fwd[7]*x_det**2*y_det
      + y_poly_fwd[8]*x_det*y_det**2
      + y_poly_fwd[9]*y_det**3
      + y_poly_fwd[10]*y_det*math.sqrt(x_det**2 + y_det**2)
      + y_poly_fwd[11]*x_det*math.sqrt(x_det**2 + y_det**2))

   # Add the distortion correction
   y_pix = y_det + dy 

   x_pix = x_pix / F_scale
   y_pix = y_pix / F_scale

   ### Convert gnomonic X, Y to alt, az ###

   # Caulucate the needed parameters
   radius = math.radians(math.sqrt(x_pix**2 + y_pix**2))
   theta = math.radians((90 - pos_angle_ref + math.degrees(math.atan2(y_pix, x_pix)))%360)

   sin_t = math.sin(dec_rad)*math.cos(radius) + math.cos(dec_rad)*math.sin(radius)*math.cos(theta)
   Dec0det = math.atan2(sin_t, math.sqrt(1 - sin_t**2))

   sin_t = math.sin(theta)*math.sin(radius)/math.cos(Dec0det)
   cos_t = (math.cos(radius) - math.sin(Dec0det)*math.sin(dec_rad))/(math.cos(Dec0det)*math.cos(dec_rad))
   RA0det = (RA_d - math.degrees(math.atan2(sin_t, cos_t)))%360

   h = math.radians(Ho + lon - RA0det)
   sh = math.sin(h)
   sd = math.sin(Dec0det)
   ch = math.cos(h)
   cd = math.cos(Dec0det)

   x = -ch*cd*sl + sd*cl
   y = -sh*cd
   z = ch*cd*cl + sd*sl

   r = math.sqrt(x**2 + y**2)

   # Calculate azimuth and altitude
   azimuth = math.degrees(math.atan2(y, x))%360
   altitude = math.degrees(math.atan2(z, r))



   ### Convert alt, az to RA, Dec ###

   # Never allow the altitude to be exactly 90 deg due to numerical issues
   if altitude == 90:
      altitude = 89.9999

   # Convert altitude and azimuth to radians
   az_rad = math.radians(azimuth)
   alt_rad = math.radians(altitude)

   saz = math.sin(az_rad)
   salt = math.sin(alt_rad)
   caz = math.cos(az_rad)
   calt = math.cos(alt_rad)

   x = -saz*calt
   y = -caz*sl*calt + salt*cl
   HA = math.degrees(math.atan2(x, y))

   # Calculate the hour angle
   T = (jd - 2451545.0)/36525.0
   hour_angle = (280.46061837 + 360.98564736629*(jd - 2451545.0) + 0.000387933*T**2 - T**3/38710000.0)%360

   RA = (hour_angle + lon - HA)%360
   dec = math.degrees(math.asin(sl*salt + cl*calt*caz))

   ### ###
 

   return(x_pix+img_x,y_pix+img_y,RA,dec,azimuth,altitude)

# Return Ra/Dec based on X,Y for a given frame
def XYtoRADec___(x,y,analysed_name,json_file):
 
   # Get Data from analysed_name
   hd_y = analysed_name['year']
   hd_m = analysed_name['month']
   hd_d = analysed_name['day']
   hd_h = analysed_name['hour']
   hd_M = analysed_name['min']
    
   # Get Calib params
   F_scale     = 3600 /float(json_file['calib']['device']['scale_px'])
   x_poly_fwd  = json_file['calib']['device']['poly']['x_fwd']
   y_poly_fwd  = json_file['calib']['device']['poly']['y_fwd']
   lat         = float(json_file['calib']['device']['lat'])
   lon         = float(json_file['calib']['device']['lng'])
   dec_d       = float(json_file['calib']['device']['center']['dec']) 
   RA_d        = float(json_file['calib']['device']['center']['ra']) 
   angle       = float(json_file['calib']['device']['angle']) 


   #print('Year' +  str(hd_y) +"<br>")
   #print('Mpnth' +  str(hd_m)+"<br>")
   #print('Day' +  str(hd_d)+"<br>")
   #print('Hour' +  str(hd_h)+"<br>")
   #print('Minute' +  str(hd_M)+"<br>") 
   #print('F_scale' +  str(F_scale) +"<br>")
   #print('lat' +  str(lat)+"<br>")
   #print('lon' +  str(lon)+"<br>")
   #print('dec_d' +  str(dec_d)+"<br>")
   #print('RA_d' +  str(RA_d)+"<br>")
   #print('angle' +  str(angle)+"<br>")

   print(json_file)
   


   total_min = (int(hd_h) * 60) + int(hd_M)
   day_frac = total_min / 1440 
   hd_d = int(hd_d) + day_frac
   jd = date_to_jd(int(hd_y),int(hd_m),float(hd_d))

   # Calculate the reference hour angle
   T = (jd - 2451545.0)/36525.0
   Ho = (280.46061837 + 360.98564736629*(jd - 2451545.0) + 0.000387933*T**2 - (T**3)/38710000.0)%360

   dec_d = dec_d + (x_poly_fwd[13] * 100)
   dec_d = dec_d + (y_poly_fwd[13] * 100)

   RA_d = RA_d + (x_poly_fwd[14] * 100)
   RA_d = RA_d + (y_poly_fwd[14] * 100)

   pos_angle_ref = angle + (1000*x_poly_fwd[12]) + (1000*y_poly_fwd[12])

   # Convert declination to radians
   dec_rad = math.radians(dec_d)

   # Precalculate some parameters
   sl = math.sin(math.radians(lat))
   cl = math.cos(math.radians(lat))
   
   # HERE we only work with HD
   x_det = x - HD_W/2
   y_det = y - HD_H/2

   dx = (x_poly_fwd[0]
      + x_poly_fwd[1]*x_det
      + x_poly_fwd[2]*y_det
      + x_poly_fwd[3]*x_det**2
      + x_poly_fwd[4]*x_det*y_det
      + x_poly_fwd[5]*y_det**2
      + x_poly_fwd[6]*x_det**3
      + x_poly_fwd[7]*x_det**2*y_det
      + x_poly_fwd[8]*x_det*y_det**2
      + x_poly_fwd[9]*y_det**3
      + x_poly_fwd[10]*x_det*math.sqrt(x_det**2 + y_det**2)
      + x_poly_fwd[11]*y_det*math.sqrt(x_det**2 + y_det**2))

   # Add the distortion correction
   x_pix = x_det + dx  

   dy = (y_poly_fwd[0]
      + y_poly_fwd[1]*x_det
      + y_poly_fwd[2]*y_det
      + y_poly_fwd[3]*x_det**2
      + y_poly_fwd[4]*x_det*y_det
      + y_poly_fwd[5]*y_det**2
      + y_poly_fwd[6]*x_det**3
      + y_poly_fwd[7]*x_det**2*y_det
      + y_poly_fwd[8]*x_det*y_det**2
      + y_poly_fwd[9]*y_det**3
      + y_poly_fwd[10]*y_det*math.sqrt(x_det**2 + y_det**2)
      + y_poly_fwd[11]*x_det*math.sqrt(x_det**2 + y_det**2))

   # Add the distortion correction
   y_pix = y_det + dy 

   x_pix = x_pix / F_scale
   y_pix = y_pix / F_scale

   ### Convert gnomonic X, Y to alt, az ###

   # Caculate the needed parameters
   radius = math.radians(math.sqrt(x_pix**2 + y_pix**2))
   theta = math.radians((90 - pos_angle_ref + math.degrees(math.atan2(y_pix, x_pix)))%360)

   sin_t = math.sin(dec_rad)*math.cos(radius) + math.cos(dec_rad)*math.sin(radius)*math.cos(theta)
   Dec0det = math.atan2(sin_t, math.sqrt(1 - sin_t**2))

   sin_t = math.sin(theta)*math.sin(radius)/math.cos(Dec0det)
   cos_t = (math.cos(radius) - math.sin(Dec0det)*math.sin(dec_rad))/(math.cos(Dec0det)*math.cos(dec_rad))
   RA0det = (RA_d - math.degrees(math.atan2(sin_t, cos_t)))%360

   h = math.radians(Ho + lon - RA0det)
   sh = math.sin(h)
   sd = math.sin(Dec0det)
   ch = math.cos(h)
   cd = math.cos(Dec0det)

   x = -ch*cd*sl + sd*cl
   y = -sh*cd
   z = ch*cd*cl + sd*sl

   r = math.sqrt(x**2 + y**2)

   # Calculate azimuth and altitude
   azimuth = math.degrees(math.atan2(y, x))%360
   altitude = math.degrees(math.atan2(z, r))

   ### Convert alt, az to RA, Dec ###

   # Never allow the altitude to be exactly 90 deg due to numerical issues
   if altitude == 90:
      altitude = 89.9999

   # Convert altitude and azimuth to radians
   az_rad = math.radians(azimuth)
   alt_rad = math.radians(altitude)

   saz = math.sin(az_rad)
   salt = math.sin(alt_rad)
   caz = math.cos(az_rad)
   calt = math.cos(alt_rad)

   x = -saz*calt
   y = -caz*sl*calt + salt*cl
   HA = math.degrees(math.atan2(x, y))

   # Calculate the hour angle
   T = (jd - 2451545.0)/36525.0
   hour_angle = (280.46061837 + 360.98564736629*(jd - 2451545.0) + 0.000387933*T**2 - T**3/38710000.0)%360

   RA = (hour_angle + lon - HA)%360
   dec = math.degrees(math.asin(sl*salt + cl*calt*caz))

   ### ###
   return(x_pix+x,y_pix+y,RA,dec,azimuth,altitude)


# Find closest Calibration Parameters based on Cam ID and capture date 
def find_matching_cal_files(cam_id, capture_date):
   matches = []
   all_directories = glob.glob(CALIB_PATH + "*"+cam_id+"*")
   
   for directory in all_directories:
      # Do we have a "-stacked-calparams.json" file in this directory?
      st_cal_json = glob.glob(directory+"/*-stacked-calparams.json")
      if(len(st_cal_json)!=0):
         matches.append(st_cal_json[0])
      else:
         cal_json = glob.glob(directory+"/*-calparams.json")
         if(len(cal_json)!=0):
            matches.append(cal_json[0])

   # We sort the files by date
   td_sorted_matches = []

   for match in matches:
      # We analysed the name (with without -stacked-calparams or -calparams)
      # _X is added to match the regex defined in REDUCE_VARS and used by the name_analyser
      if match.endswith('-stacked-calparams.json'):
         match_t = re.sub('\-stacked-calparams.json$', '', match) + "_X.json"
      elif match.endswith('-calparams.json'):
         match_t = re.sub('\-calparams.json$', '', match) + "_X.json"

      analysed_name = name_analyser(match_t)   

      # Build the date
      t_datetime = get_datetime_from_analysedname(analysed_name)
      tdiff = abs((capture_date-t_datetime).total_seconds())

      # We dont add the seconds or milliseconds here as we shouldn't have 2 calib files within the same minute 
      td_sorted_matches.append((match,datetime.strftime(t_datetime, '%Y-%m-%d %H:%M'),tdiff))

   # We return the sorted list of calib file
   return sorted(td_sorted_matches, key=lambda x: x[2], reverse=False)
 

# Find a calibration file based on a calib date as presented in the JSON
# ex: 2019_08_03_07_48_45_000
# and a cam_id
def find_calib_file(calib_dt_string,cam_id):
   # Get the corresponding file name 
   find_calib_json = glob.glob(CALIB_PATH + calib_dt_string + "*"+cam_id+"*"+"/"+"*-stacked-calparams.json")
   
   if(len(find_calib_json)==0):
      find_calib_json = glob.glob(CALIB_PATH + calib_dt_string + "*"+cam_id+"*"+"/"+"*-calparams.json")

   #print("GLOB " + CALIB_PATH + calib_dt_string + "*"+cam_id+"*"+"/"+"*-calparams.json")
   
   if(len(find_calib_json)==0):
      return "ERROR: Calibration File not found"
   else:
      return find_calib_json[0]