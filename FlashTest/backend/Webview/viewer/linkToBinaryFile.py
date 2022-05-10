#!/usr/bin/env python
import os,sys
import cgi, tempfile
sys.path.insert(0,"../lib")
import validate

# -------------- form data ---------------- #
form = cgi.FieldStorage()
targetFile = form.getvalue("target_file")

print("Content-type: text/html\n")
print("<html>")
print("<head>")

if targetFile:
  validate.validatePath(targetFile)
  if os.path.isfile(targetFile):
    tmpDir = tempfile.mkdtemp(dir="../tmp")
    linkDest = os.path.normpath(os.path.join("../tmp", tmpDir, os.path.basename(targetFile)))
    os.symlink(targetFile, linkDest)
    print("<meta http-equiv=\"refresh\" content=\"0; url=%s\">" % linkDest)
    print("</head>")
  else:
    print("<title>Flash Center for Computational Science</title>")
    print("</head>")
    print("<body>")
    print("%s does not exist or is not a file" % targetFile)
    print("</body>")

else:
  print("<title>Flash Center for Computational Science</title>")
  print("<style>")
  print("body {font-family: Courier, Times, Helvetica, Geneva, Arial, sans-serif;")
  print("font-size: 12px;}")
  print("</style>")
  print("</head>")
  print("<body>")
  print("no target file specified.")
  print("</body>")

print("</html>")
