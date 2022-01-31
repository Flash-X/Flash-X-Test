#!/usr/bin/env python
import os,sys
import cgi
sys.path.insert(0,"../lib")
import validate

# -------------- form data ---------------- #
form = cgi.FieldStorage()

targetFile  = form.getvalue("target_file")
soughtBuild = form.getvalue("sought_build")

	



print("Content-type: text/html\n")
print("\n") # DEV Why the hell does uncommenting above line cause
           # "page unavailable" error at my dad's house but just
           # a newline by itself (or anything except the correct 
           # header followed by a newline) allows it to work?!
print("<html>")
print("<head>")
print("<title>Flash Center for Computational Science</title>")
print("<style type=\"text/css\">")
print("body {font-family: Courier, Times, Helvetica, Geneva, Arial, sans-serif;")
print("font-size: 12px;}")
print("</style>")
print("<script src=\"findText.js\"></script>")
print("</head>")
if soughtBuild:
  print("<body onLoad=\"javascript: findText('%s')\">" % soughtBuild)
else:
  print("<body>")
print("<pre>")
if targetFile:
  
  try:

  	validate.validatePath(targetFile)
    	text = open(targetFile,"r").read()
  except Exception as e:
    print("Error opening file<br>")
    print(e)
  else:
    print(text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;"))
print("</pre>")
print("</body>")
print("</html>")
