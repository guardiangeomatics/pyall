#created p.kennedy@fugro.com
#created: May 2015
#Based on twitter bootstrap

import os
import time
import sys
import datetime
import urllib.parse
import urllib.request

#make a listing of filenames into a nice HTML table
def makeListing( folder):
	s = ""
	#open the table	
	s += "<div class=\"col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main\">\n"
	s += "	<h2 id=\"" + folder + "\">" + folder + "</h2>\n"
	s += "</div>\n"	
	
	# if a html file exists in the parts folder, we merge it here.  
	# This could be intro information on the purpose of the section in the BMS
	introFile = os.path.join("./_parts", folder + ".html")
	print ("Searching for parts in: " + introFile)
	if os.path.exists (introFile):
		print("merging intro section: " + introFile)
		fin = open(introFile, "r")
		document = fin.read()
		fin.close()
		s += document
		
	for dirname, dirnames, filenames in os.walk("./" + folder + "/"):
		if (len(filenames) > 0):
			s += "<div class=\"col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main\">\n"
			s += "  <h3 id=\"" + patchurl(os.path.basename(dirname)) + "\">" + patchurlText(os.path.basename(dirname)) + "</h3>\n"

			# if a html file exists in the parts folder, we merge it here.  
			# This could be intro information on the purpose of the section in the BMS
			introFile = os.path.join("./_parts", os.path.basename(dirname) + ".html")
			print ("Searching for parts in: " + introFile)
			if os.path.exists (introFile):
				print("merging intro section: " + introFile)
				fin = open(introFile, "r")
				document = fin.read()
				fin.close()
				s += document

			s += "  <table class=\"table\">\n"
			s += "    <tbody>\n"	
			s += "    <tr> <th>FileName</th> <th>Date</th> <th>Status</th> </tr>\n"


		for filename in filenames:
			#add a link to the filename
			s += "      <tr>\n"
			s += "        <td><a href=" + "\"" + urllib.parse.quote(os.path.join(dirname, filename)) + "\">" + patchurlText(filename) + "</a></td>\n" 
			
			#add the file timestamp
			s += "        <td>" + time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(os.path.join(dirname, filename)))) + "</td>\n" 	

			# mtime is the number of seconds since epoch			
			fileTimeStamp = datetime.datetime.fromtimestamp(os.path.getmtime(	os.path.join(dirname, filename)))
			
			age = pretty_date(fileTimeStamp)
			s += "        <td>" + age + "</td>\n"
			
			
			
			now = datetime.datetime.today()
			timediff = now - fileTimeStamp
			#add the New icon if less than 1 month old (seconds*minutes*hours*days*months
			oldFiles = 60 * 60 * 24 * 30 * 6
#			if timediff.total_seconds() < oldFiles:
#				s += "        <td>" + "<img src=\"images/new.png\" height=\"24\" alt=\"new\" >(New)" + "</td>\n"
#			else:
#				s += "        <td>" + "<img src=\"images/tick.png\" height=\"24\" alt=\"tick\" >" + "</td>\n"
			s += "      </tr>\n"

		if (len(filenames) > 0):
			#close the table
			s += "    </tbody>\n"	
			s += "  </table>\n"	
			s += "</div>\n"	
	return s

def patchurlText(url):
		url = url.replace('&', '&amp;')
		return url
def patchurl(url):
		url = url.replace(' ', '')
		#url = url.replace('.', '')
		url = url.replace('(', '')
		url = url.replace(')', '')
		return url

#build the navbar crop down menu from the folder layout and add the links
def makeListing2DropDownMenu( folder):
	s = ""
	#add menu item	
	s += "					<li class=\"dropdown\">\n"
	s += "						<a href=\"#\" data-toggle=\"dropdown\" class=\"dropdown-toggle\">" + patchurl(folder) + "<b class=\"caret\"></b></a>\n"
	s += "						<ul class=\"dropdown-menu\">\n"
			
	# add sub menu
	for dirname, dirnames, filenames in os.walk("./" + folder + "/"):
		if (len(filenames) > 0):
			s += "							<li> <a href=\"#" + patchurl(os.path.basename(dirname))+ "\">" + patchurlText(os.path.basename(dirname)) + "</a> </li>\n"	
	
	s += "						</ul>\n"
	s += "					</li>\n"
	return s
	
def makeListing2SideBarMenu( folder):
	s = ""
	#add menu item	
	s += "						<li> <a href=\"#" + patchurl(folder) + "\"><B>" + patchurlText(folder) + "</B></a>	</li>\n"
	s += "						<ul>\n"
			
	# add sub menu
	for dirname, dirnames, filenames in os.walk("./" + folder + "/"):
		if (len(filenames) > 0):
			s += "							<li> <a href=\"#" + patchurl(os.path.basename(dirname)) + "\">" + patchurlText(os.path.basename(dirname)) + "</a> </li>\n"
	
	s += "						</ul><!--close the submenu list-->\n"
	# s += "					</li><!--do bugger all-->\n"
	return s

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

if __name__ == '__main__':
    # test1.py executed as script
    # do something
	s = makeListing(sys.argv[1])
	print(s)