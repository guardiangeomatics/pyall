# created p.kennedy@fugro.com
# created: May 2015
# Based on twitter bootstrap
# 
import os
import sys
import re
import urllib.parse
import urllib.request
import time
import datetime

# specify a list of folder names which will be skipped in the scanning process.  The list can be as long as you like.


def whatsnew(outputFileName, searchFolder, ignoreFolders):
	print("scanning folders and sub folders and build all links...")
	dirs = os.listdir( searchFolder )
	files = []

	for folder in dirs:
		if os.path.isdir(folder):
			for dirname, dirnames, filenames in os.walk ( folder + "/"):
				if (len(filenames) > 0):
					if any(x in dirname for x in ignoreFolders):
						print("Skipping ignored folder: " + folder)
						print (filenames)
					else:
						for filename in filenames:
							f = os.path.join(dirname, filename)
							t = os.path.getmtime(os.path.join(dirname, filename))
							file = [f, t, filename]
							files.append(file)
			sortedFiles = sorted(files, key=lambda x: x[1], reverse=True)

	s = ""
	#open the table	
	#s += "<div class=\"col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main\">\n"
	#s += "	<h2 id=\"new" + "\">Whats new</h2>\n"
	#s += "</div>\n"	

	s += "<div class=\"col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main\">\n"
	s += "  <h3 id=\"" + "new" + "\">" + "Whats new?  Here is a short list of the newest 10 documents in your portal" + "</h3>\n"

	s += "  <table class=\"table\">\n"
	s += "    <tbody>\n"	
	s += "    <tr> <th>FileName</th> <th>Date</th> <th>Status</th> </tr>\n"

	newlistSize = 10
	for f in sortedFiles[:newlistSize]:
		#add a link to the filename
		s += "      <tr>\n"
		s += "        <td><a href=" + "\"" + urllib.parse.quote(f[0]) + "\">" + patchurlText(f[2]) + "</a></td>\n" 
		
		#add the file timestamp
		s += "        <td>" + time.strftime('%d/%m/%Y', time.gmtime(f[1])) + "</td>\n" 	

		# mtime is the number of seconds since epoch			
		fileTimeStamp = datetime.datetime.fromtimestamp(f[1])
		
		age = pretty_date(fileTimeStamp)
		s += "        <td>" + age + "</td>\n"

	#close the table
	s += "    </tbody>\n"	
	s += "  </table>\n"	
	s += "</div>\n"	

	fout = open(outputFileName, "a")
	fout.write(s)
	fout.close()

	return

def patchurlText(url):
	url = url.replace('&', '&amp;')
	return url
def patchurl(url):
	url = url.replace(' ', '')
	#url = url.replace('.', '')
	url = url.replace('(', '')
	url = url.replace(')', '')
	return url

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "released just now"
        if second_diff < 60:
            return "released {0:1.0f}".format(second_diff) + " seconds ago"
        if second_diff < 120:
            return "released a minute ago"
        if second_diff < 3600:
            return "released {0:1.0f}".format(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "released an hour ago"
        if second_diff < 86400:
            return "released {0:1.0f}".format(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "released Yesterday"
    if day_diff < 7:
        return "released {0:1.0f}".format(day_diff) + " days ago"
    if day_diff < 31:
        return "released {0:1.0f}".format(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return "released {0:1.0f}".format(day_diff / 30) + " months ago"
    return "released {0:1.0f}".format(day_diff / 365) + " years ago"
	
def main():
	ignoreFolders = ['_parts', 'images', '_trash', 'bootstrap', '_scripts', '__pychache__', 'aspnet_client']

	print("Starting to compile Whats New...")

	whatsnew(  "c:/temp/whatsnew.txt", "H:/FSPTY-BMS", ignoreFolders)

	
if __name__ == "__main__":
    main()