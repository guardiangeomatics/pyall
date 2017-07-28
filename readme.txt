created: p.kennedy@fugro.com
created: May 2015

#FSPTY BMS Rev 2015 readme.txt

Please see HTML files in the ./parts folder


#User Guide
The static HTML pages are compiled from files on disc using Python.  By compiling the pages once, we create a static site which does not need a web server to host the pages
You need to have python 2.7 or better to compile the BMS.  Download it from the web
to compile the site, run open a cmd prompt in the BMS folder and enter the following:

C:\Temp\bms\V2\FSPTY-BMS>c:\Python27\ArcGIS10.3\python.exe buildFSPTYBMS.py
Starting to compile the FSPTY BMS...
processing static parts..
scanning management documents
scanning QHSE documents
scanning Operations documents
Adding the closing tags to the page...
Complete.

C:\Temp\bms\V2\FSPTY-BMS>

This will result in a new FSPTY-BMS.HTML file.  Open it in a browser to see your results.

#Adding / Removing new files to an existing folder.
If you wish to add or remove files to the existing folders, just use windows explorer.  Nothing special there.
You can even use sub folder if you prefer, but there is a restriction to 2 levels, ie .\management\classA\mydoc.doc is ok, but do not go any further down.
Once you have updated the folders with the new files, you need to re-compile the BMS as shown above.

#Adding static text to existing BMS
If you wish to add static text to the site, you can find the files in the ./parts folder.  Edit an existing file then re-compile to see your results.

#Adding a new static file to the BMS
1. You can add a new part to the site, but you then need to add it to the compiler.
2. We make a new file "./parts/reception.html" and add some valid HTML to it.
3. We then edit the "buildBMS.py" script and add the following entry
mergeFile("./parts/reception.html")
4. Finally, we need to recompile the BMS, and view in a browser

Thats it!


