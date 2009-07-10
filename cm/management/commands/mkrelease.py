# -*- coding: utf-8 -*-
import os
from django.core.management.base import BaseCommand

# ugly packaging utility

class Command(BaseCommand):
    def handle(self, *app_labels, **options):
        version = '0.99'
        release(version)

app_to_package = ['cm' , 'tagging']
def release(version):
    
        os.system("rm -rf build")
        os.system("mkdir build")        
        os.system("mkdir build/co-ment")
        for app_pack in app_to_package: 
            os.system('rsync -ka --exclude "*.pyc" --exclude ".svn" --exclude ".*" %s build/co-ment' %app_pack)
                    
        os.system("cp build/co-ment/cm/examples/* build/co-ment/")
        os.system("cp build/co-ment/cm/examples/* build/co-ment/")
        os.system("mv build/co-ment/cm/README.txt build/co-ment/README.txt")
        os.system("cd build && tar cfz co-ment-%s.tgz co-ment" %version)

