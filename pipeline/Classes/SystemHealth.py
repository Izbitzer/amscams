import subprocess
from datetime import datetime
import os
import glob
from lib.PipeUtil import cfe, load_json_file, save_json_file, get_file_info

class SystemHealth():
   def __init__(self):
      self.json_conf = load_json_file("../conf/as6.json")
      self.station_id = self.json_conf['site']['ams_id']
      self.cloud_dir = "/mnt/archive.allsky.tv/" + self.station_id + "/" 
      self.data_dirs = {}
      self.data_dirs["/mnt/ams2/HD"] = {}
      self.data_dirs["/mnt/ams2/HD"]['max_size'] = 400
      self.data_dirs["/mnt/ams2/SD/proc2"] = {}
      self.data_dirs["/mnt/ams2/SD/proc2"]['max_size'] = 350
      print("Check for zombies...")
      self.python_procs = self.kill_python_zombies()

   def kill_python_zombies(self):
      cmd = "ps -eo pid,cmd,user,etime |grep python3 | grep ams | grep -v grep > p3procs.txt" 
      os.system(cmd)
      running_procs = []
      fp = open("p3procs.txt", "r")
      for line in fp:
         el = line.split(" ")
         time = el[-1]
         running_procs.append((el[0],el[1],el[2],el[3],el[4],el[5],el[-1]))
         if "-" in time:
            print("PROCESS RUNNING FOR DAYS! KILL IT!")
            cmd = "kill -9 " + el[0]
            print(cmd)
            os.system(cmd)

         else:
            hhh = time.split(":") 
            print("Process running", hhh[0], "hours", line)
            if int(hhh[0]) >= 4:
               cmd = "kill -9 " + el[0]
               print(cmd)
               os.system(cmd)
      return(running_procs)

   def make_report(self):
      print("SYSTEM HEALTH REPORT")
      print("Ping cams...")
      pings = self.ping_cams()
      print("PINGS:", pings)
      print("Run df...")
      df_data, mounts = self.run_df()
      print("DF DATA:", df_data)
      print("MOUNTS:", mounts)
      system_health_report = {}
      system_health_report['last_update'] = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") 
      system_health_report['uptime'] = subprocess.check_output("uptime", shell=True).decode("utf-8")

      system_health_report['pings'] = pings 
      system_health_report['df_data'] = df_data
      system_health_report['mounts'] = mounts
      system_health_report['python_procs'] = self.python_procs
      #self.check_quotas()
      system_health_report['data_dirs'] = {}
      for dd in self.data_dirs:
         print("Data Dir:", dd, self.data_dirs[dd])
         system_health_report['data_dirs'][dd] = self.data_dirs[dd]
      # pending files
      command = "find /mnt/ams2/SD/ -type f -maxdepth 1 -name '*.mp4' | wc -l"
      print("SD FILES:", command)
      process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      stdout, stderr = process.communicate()

      if process.returncode == 0:
         self.pending_SD_files = int(stdout.strip())
         print(f"File count: {self.pending_SD_files}")
      else:
         print(f"Error: {stderr}")
         self.pending_SD_files = 0

      # pending day files
      command = "find /mnt/ams2/SD/proc2/daytime/ -type f -maxdepth 1 -name '*.mp4' | wc -l"
      print("DAY FILES:", command)
      process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
      stdout, stderr = process.communicate()

      if process.returncode == 0:
         self.pending_SD_day_files = int(stdout.strip())
         print(f"File count: {self.pending_SD_day_files}")
      else:
         print(f"Error: {stderr}")
         self.pending_SD_day_files = 0

      if self.pending_SD_day_files >= 10000:
         print("We have major backlog and should delete some files!")
         cmd = """find /mnt/ams2/SD/proc2/daytime/ -type f -maxdepth 1 -name "*.mp4" -print0 | xargs -0 rm -f"""
         print(cmd)
         os.system(cmd)


        #find . -type f -name "*" |wc -l
        #find . -type f -name "2023_09*" -print0 | xargs -0 rm -f


      system_health_report['pending_files'] = self.pending_SD_files
      system_health_report['pending_day_files'] = self.pending_SD_day_files
      print("Get latest file from cloud.")
      latest_files = glob.glob("/mnt/archive.allsky.tv/" + self.station_id + "/LATEST/*.jpg")
      if len(latest_files) > 0:
         info = get_file_info(latest_files[0])
         print("INFO:", latest_files[0])
         fsize, self.last_latest_file = get_file_info(latest_files[0])
         system_health_report['latest_file_age'] = self.last_latest_file
      else:
         self.last_latest_file = None
      print("Last latest file age:", self.last_latest_file)
      save_json_file("../conf/" + self.station_id + "_system_health.json", system_health_report)
      cmd = "cp ../conf/" + self.station_id + "_system_health.json " + self.cloud_dir 
      print(cmd)
      os.system(cmd)

      print("../conf/" + self.station_id + "_system_health.json")
   
      

   def ping_cams(self):
      pings = {}
      for key in self.json_conf['cameras']:
         cmd = "ping -i 0.2 -c 1 " + self.json_conf['cameras'][key]['ip']
         #cmd = "nmap -sP --max-retries=1 --host-timeout=1500ms " + self.json_conf['cameras'][key]['ip']
         print(cmd)
         try:
            response = subprocess.check_output(cmd, shell=True).decode("utf-8")
         except:
            response = "down"
         print("RESP:", response)
         if "bytes from" in response :
            pings[key] = "UP"
         else:
            pings[key] = "DOWN"
      return(pings)

   def check_quotas(self):
      for tdir in self.data_dirs:
         output = self.do_du(tdir) 
         if output is not None:
            used = output[0]
            used = used.replace("G", "")
            used = used.replace("M", "")
            used = used.replace("K", "")
            self.data_dirs[tdir]['used_size'] = int(float(used))
            quota_perc = self.data_dirs[tdir]['used_size'] / self.data_dirs[tdir]['max_size']
            over_quota = 1 - quota_perc
            if over_quota < 0:
               print("OVER QUOTA:", tdir, quota_perc, abs(over_quota))
               self.purge_dir(tdir, over_quota)
               os.system("cd /home/ams/amscams/pythonv2; ./doDay.py cd")

   def purge_dir(self, tdir, over_quota):
      if "HD" in tdir:
         all_files = []
         temp = glob.glob(tdir + "/*.mp4")
         for tfile in temp:
            if "trim" not in tfile:
               all_files.append(tfile)
         #print("ALL HD FILES:", len(all_files))
         delete_count = int(len(all_files) * abs(over_quota))
         #print("DELETE ", (abs(over_quota*100)), "% of HD FILES FROM ", tdir, delete_count," files")
         for hd_file in sorted(all_files)[0:delete_count]:
            #print("Delete this file:", hd_file)
            os.system("rm " + hd_file)
          

            


   def do_du(self,tdir):
      cmd = "du -h " + tdir
      #print(cmd)
      output = subprocess.check_output(cmd, shell=True).decode("utf-8")
      lines = output.split("\n")
      match = None
      for line in lines:
         el = line.split("\t")
         if len(el) > 1:
            if el[1] == tdir:
               match = el

      return(match)

   def run_df(self):
      df_data = []
      mounts = {}
      if True:
         cmd = "df -h "
         output = subprocess.check_output(cmd, shell=True).decode("utf-8")
         #   Filesystem                 Size  Used Avail Use% Mounted on

         for line in output.split("\n"):
            #line = line.replace("  ", " ")
            temp = " ".join(line.split())
            disk_data = temp.split(" ")
            if len(disk_data) > 5:
               file_system = disk_data[0]
               size = disk_data[1]
               used  = disk_data[2]
               avail = disk_data[3]
               used_perc = disk_data[4]
               mount = disk_data[5]
               #print(mount, used_perc)
               if mount == "/" or mount == "/mnt/ams2" or mount == "/mnt/archive.allsky.tv" or mount == "/home":
                  df_data.append((file_system, size, used, avail, used_perc, mount))
                  used_perc = used_perc.replace(" ", "")
                  mounts[mount] = int(used_perc.replace("%", ""))
      #else:
      #   print("Failed du")

      return(df_data, mounts)
