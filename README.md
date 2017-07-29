# DocumentDelivery
A simple python script to build an all-in-one index.html page of all files in subfolders and expose as a simple web page

To serve the project documentation using IIS on your regular windows PC follow these instructions.  This sounds like a lot, but it only takes a minute...
1. From the start menu, goto control panel and open "programs and features"
2. On the left side, select 'Turn Windows features on or off"
3. Enable the checkbox "Internet Information Services\Web Management Tools\IIS Management Console"
4. Enable the checkbox "Internet Information Services\World Wide Web Services\ Common HTTP Features\Default Document"
5. Enable the checkbox "Internet Information Services\World Wide Web Services\ Common HTTP Features\Static Content"
6. From the start menu, type IIS to open the IIS Manager tool
7. Expand the connection tree on the left side of the application and open the \Sites.  Click on the 'Default Web Site'
8. On the right hand side of the tool, click the 'Edit Site\Basic Settings'
9. Edit the physical path to wherever your index.html page resides on your computer (by default inetpub\wwwroot will be the folder)
10.Open a web browser such as chrome and type in 'localghost'  you should see your document portal!
11. From any other computer, just enter the IP address of the computer you are using to host the portal, eg 192.168.1.12


