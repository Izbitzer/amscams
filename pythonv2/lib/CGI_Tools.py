import sys

# CGI redirect
def redirect_to(redirectURL, page_type="proper"):
   print( '<html  style="width:100vw; height:100vh; background:#061329">')
   print( '  <head>')
   print( '    <meta http-equiv="refresh" content="0;url='+redirectURL+'" />' )
   print( '    <title>You are going to be redirected</title><link rel="stylesheet" href="./dist/css/main.css"/>')
   print( '  </head>') 
   print( '  <body style="width:100vw; height:100vh; background:#061329">')
   print( '  <div id="overlay" class="animated"><div class="row h-100 text-center"><div class="col-sm-12 my-auto"><div class="card card-block" style="background:transparent"><iframe style="border:0;margin: 0 auto;" src="./dist/img/anim_logo.svg" width="140" height="90"></iframe><h4>Please wait while we redirect you to the '+page_type+' page...</h4></div></div></div></div>')
   print( '  </body>')
   print( '</html>')
   sys.exit(0)