import os
from django.core.management.base import BaseCommand
from time import time
import re
# used the example of /django_trunk/django/core/management/commands/dumpdata.py

class Command(BaseCommand):
    def handle(self, *app_labels, **options):
        os.system("rm -rf temp")
        os.system("rm cm/media/client/js/comentclient-min.js")
        os.system("mkdir temp")
        os.system("find cm/media/client/js -name \"*.js\" > clientfiles")
            
        f = open("clientfiles")
        try:
            for fname in f:
                fullfilename = fname.replace('\n','')
                filename = fullfilename
                
                ind = filename.rfind("/")
                if ind > -1 :
                    filename = filename[ind+1:]
                    
                ind = filename.rfind(".")
                if ind > -1 :
                    filename = filename[:ind]
                   
                destfile = "temp/" + filename + "-min.js"
                os.system("java -jar cm/lib/yuicompressor-2.2.4/build/yuicompressor-2.2.4.jar --preserve-semi " + fullfilename + ">" + destfile)
                
        finally:
            f.close()
        
        os.system("cat temp/ns_cst-min.js temp/CookieHandler-min.js temp/User-min.js temp/CommentAttachMgr-min.js temp/ServerExchange-min.js temp/AttachController-min.js temp/DiscussionItem-min.js temp/FilterMgr-min.js temp/Language-min.js temp/util-min.js temp/LayoutMgr-min.js temp/MenuMgr-min.js temp/TextMgr-min.js temp/PrintMgr-min.js temp/ExportMgr-min.js temp/So_Computation-min.js temp/SelectionMgr-min.js temp/CommentAttach-min.js temp/coment-client-min.js > cm/media/client/js/comentclient-min.js")
        os.system("rm -rf temp")
        os.system("rm clientfiles")
        
        # change reference to js to add datetimestamp int(time())
        # to prevent browser caching
        timestamp = int(time())
        FILE = 'cm/templates/layout/client_js_libs.html'
        
        print ""
        print "setting timestamp %d in %s, commit the file" %(timestamp,FILE)
        
        input = open(FILE).read()
        p = re.compile('comentclient-min.js\?(\d*)"')
        new_input = p.sub('comentclient-min.js?%d"' % timestamp,input)
        ff = open(FILE,'w')
        ff.write(new_input)
        ff.close()
        

        