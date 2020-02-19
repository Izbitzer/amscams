#!/usr/bin/python3

import os
import cgi 
import json
import datetime

JSON_CONFIG = '/home/ams/amscams/conf/as6.json'

print('Content-Type: text/html; charset=utf-8')

def api_controller(form):
   api_function = form.getvalue('function')

   if(api_function=='login'):
      login(form)


# LOGIN
def login(form):

   user = form.getvalue('user')
   password = form.getvalue('pwd')

   test_log = False

   if(user is not None and password is not None):
      json_file = open('JSON_CONFIG')
      json_str = json_file.read()
      json_data = json.loads(json_str)
       
      try:
         if(json_data['site']['ams_id']==user and json_data['site']['pwd']==pwd):
            test_log = True
      except Exception:
         test_log = False
   

   if(test_log is True):
      cookie_date, tok = create_token() 

      # Keep the token on this side too as a cookie
      create_cookie(cookie_date,tok)

      return json.dumps({'tok':create_token()})
   else
      return json.dumps({'error':'You are not authorized'})


   return test_log

# CREATE TEMPORARY TOKEN
def create_token():
   expiration = datetime.datetime.now() + datetime.timedelta(days=0.5)
   return expiration.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),expiration.strftime("%d%b%Y%H%M%S_4llsk") 

# CREATE COOKIE
def create_cookie(_date,_cook):
    
    print("Content-type:text/html\r\n")
    #print("Set-Cookie:User = "+user+";\r\n") 
    print("Set-Cookie:Expires = "+_date+";\r\n") 
    print("Set-Cookie:Path = /;\n") 

# MAIN
form = cgi.FieldStorage()
api_controller(form)
