*******
co-ment
*******

Technical presentation
======================
co-ment is distributed as a django application.

License
=======
GNU AFFERO GENERAL PUBLIC LICENSE
http://www.gnu.org/licenses/agpl.html


Dependencies
============

Environment
-------------
- Postgresql 8.3
- Python 2.5
- Django 1.0


Python libs used (*NOT* shipped with the distribution)
----------------
- django	http://www.djangoproject.com/	BSD License
- python magic	permissive BSD style license
- Beautiful soup	http://www.crummy.com/software/BeautifulSoup/	PSF license
- python-chardet	http://chardet.feedparser.org/	LGPL 
- python-feedparser	http://feedparser.org/ "Permissive" custom licence
- python-imaging	http://www.pythonware.com/products/pil/ http://www.pythonware.com/products/pil/license.htm
- python-openid


Installation (development install)
============
1. Install python2.5 and all required python libraries
	(ubuntu intrepid+ users : 'apt-get install python-imaging python-psycopg2 python-beautifulsoup python-uno python-feedparser python-chardet python-magic')
2. Install django version 1.0+ 
	(ubuntu intrepid+ users : 'apt-get install python-django)
3  Install openoffice (headless mode) [used for document conversion]
	((ubuntu intrepid+ users : 'apt-get install sun-java6-jre openoffice.org openoffice.org-headless xvfb)
4. Install/configure Postgresql database server
5. Create a database (with UTF8 encoding) and a read/write access to it.
   The database account accessing the database MUST have administrative privileges when running the 'syncdb command' (step 8)
   (The reason for that is that Postgresql requires such privileges to create the C-based stored procedure that we use for full text indexing)
6. Install co-ment
   - cd into co-ment directory (next to the README.txt that you are currently reading)
   - copy settings_local_sample.py to settings_local.py (this file will contain your personal settings)  
   - edit settings_local.py to suit your settings (search for 'your_settings' occurences)
7. Create the database structure (and test your database connection)
   - `python manage.py syncdb`
9. Launch development server
   - `python manage.py runserver`
10. Acces your co-ment instance by pointing your browser to http://127.0.0.1:8000/

Installation (production environnement)
=============
If you'd like to install co-ment on a production environnement, check out django installation guide at http://www.djangoproject.com/documentation/modpython/

Openoffice
==========
co-ment uses openoffice to convert documents from ODT, MS Word, etc. to html.
On a development setup, you should make sure no openoffice process is left and launch
`soffice -headless "-accept=socket,port=2002;urp;"` to start openoffice in background mode.

co-ment uses (shipped with the distribution)
============

Javascript libs
---------------
- Yahoo UI	http://developer.yahoo.com/yui/	BSD License
- JQuery	http://jquery.com/	MIT
- Ext	http://extjs.com/	LGPL3

Icons 
-----
- Icons derived from Tango Icon Set	http://tango.freedesktop.org/Tango_Desktop_Project	CC Attr Share-Alike

FAQ
====
Q: I get 'import error' when starting the server (step #9)
R: Make sure you installed all required python dependencies (see README.txt)

Q: I am using microsoft windows and the initial loading message never disappears
R: Try disabling your antivirus if you are using one  

Supported browsers
==================
co-ment has been tested with these browsers : 
FF 3.0.5            OK
IE 7                OK
opera 9.63          OK
safari 3.2.1        OK
epiphany 2.24.1     OK
IE 6                OK (although we've heard some users experienced never ending loading message making it impossible to access comment interface)
konqueror 4.1.3     KO
                      
Contact
=======
If you have trouble to install co-ment, don't hesitate to contact us at http://www.co-ment.net/contact/

