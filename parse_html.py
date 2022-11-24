import re 
import os


path_to_junit = "test-output.xml"

os.system(f"junit2html {path_to_junit} temp.html")

f = open("temp.html", "r")

html_content = f.read()

m=re.match('.*<body>\n(.*)\n</body>.*', html_content , flags=re.S)

body_contnet = m.group(1)
f.close()

# f = open("demofile2.txt", "w")
# f.write(m.group(1))
# f.close()

os.remove("temp.html")

print(body_contnet)
