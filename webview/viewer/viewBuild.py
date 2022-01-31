#!/usr/bin/env python
import os
import cgi,sys
sys.path.insert(0, "../lib")
import validate

# -------------- form data ---------------- #
form = cgi.FieldStorage()

targetDir = form.getvalue("target_dir")

validate.validatePath(targetDir)

print("Content-type: text/html\n")
print("<html>")
print("<head>")
print("<title>Flash Center for Computational Science</title>")
print(open("style.css","r").read())
print("</head>")

print("<frameset cols=\"40%,*\">")
print("  <frame src=\"leftFrame.py?target_dir=%s\" name=\"leftframe\">" % targetDir)
print("  <frame src=\"viewTextFile.py\" name=\"rightframe\">")
print("</frameset>")
print("</html>")
