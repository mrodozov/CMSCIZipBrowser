#!/usr/bin/env python

import zipfile
import os
import time
import datetime

def removeDirSlash(path= None):
    if path[-1:] is '/':
        path = path[:-1]
    return path


def checkForZipsInPath(full_path= None):

    # remove the slash if the path is given with it
    full_path = removeDirSlash(full_path)
    list_of_dirs = full_path.split('/')
    path_to_zip = ''

    for i in list_of_dirs:
        path_to_zip += i
        #print path_to_zip
        if os.path.isfile( path_to_zip +'.zip'):
            break
        else:
            path_to_zip += '/'

    if path_to_zip[-1:] is '/':
        path_to_zip = None

    return os.path.join(path_to_zip)


def browseFileInZip(zipObj=None, path_in_zip=None):

    path_in_zip = removeDirSlash(path_in_zip)
    result = None

    if isfileinzip(zipObj, path_in_zip):
        result = zipObj.read(path_in_zip)

    if isdirinzip(zipObj, path_in_zip):
        files_in_dir = [i for i in zipObj.namelist() if path_in_zip+'/' in i and path_in_zip+'/' != i]

        if len(files_in_dir) == 0:
            #it's empty folder
            result = '--empty folder--'
        else:
            #print '---------fies in folder----------'
            items_to_show = []
            result = []
            for i in files_in_dir:
                an_item = i.split(path_in_zip+'/', 1)[1].split('/', 1)[0]
                if an_item not in items_to_show:
                    items_to_show.append(an_item)
                    if isdirinzip(zipObj, path_in_zip+'/'+an_item):
                        an_item += '/'
                    info = zipObj.getinfo(path_in_zip+'/'+an_item)
                    item_size = info.file_size
                    item_mtime = time.strftime('%Y-%m-%d %H:%M:%S', (info.date_time + (0, 0, 0)))
                    item_description = info.comment

                    result.append({'name':an_item,'link':path_in_zip+'/'+an_item,'size':str(item_size),
                                   'modified':item_mtime, 'description':item_description})

    return result


def formatResult(result = None):

    if not result:
        # not existing
        print 'file not found'
    elif not isinstance(result, list):
        #empty dir or file
        print result
    else:
        # non empty folder
        #print result

        markup="""
       <table>
       <tr>
            <th>Filename</th>
            <th>Size</th>
           <th>Date</th>
           <th>Comment<th>
       </tr>"""
        for i in result:
            markup += """
           <tr>
              <td><a href="%s">%s</a></td>
               <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>""" % (i['link'],i['name'],i['size'],i['modified'],i['description'])
        markup += '</table>'
        print markup


def isfileinzip(zipObj=None, path_in_zip=None):

    path_in_zip = removeDirSlash(path_in_zip)
    list_of_items = zipObj.namelist()
    isfile = False
    #print  path_in_zip
    if path_in_zip in list_of_items:
        isfile = True
    return isfile


def isdirinzip(zipObj=None, path_in_zip=None):

    path_in_zip = removeDirSlash(path_in_zip)
    list_of_items = zipObj.namelist()
    isdir = False
    #print  path_in_zip
    if path_in_zip+'/' in list_of_items:
        isdir = True
    return isdir


def browsePath(path=None):

    result = None

    if os.path.isfile(path):
        with open(path) as file_to_read:
            result = file_to_read.read()
        if os.stat(path).st_size == 0:
            result = ' '
    elif os.path.isdir(path):
        if not os.listdir(path):
            result = '--empty folder--'
        else:
            result = []
            for i in os.listdir(path):

                file_stat = os.stat(os.path.join(path, i))

                item_size = file_stat.st_size
                item_mtime = datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                item_description = ''

                result.append({'name':i,'link': os.path.join(path,i),'size':str(item_size),
                               'modified':item_mtime, 'description':item_description})

    return result


if __name__ == "__main__":
    print "Content-Type: text/html\n"


    if 'REQUEST_URI' in os.environ:
        uri = os.environ['REQUEST_URI']
        print uri

    requested_path = 'blabla'
    requested_path =  'zipfold/delme'
                      #'134.806_RunMuonEG2015C+RunMuonEG2015C+HLTDR2_25ns+RECODR2_25nsreHLT_HIPM+HARVESTDR2/'
                      #'step1_RunMuonEG2015C+RunMuonEG2015C+HLTDR2_25ns+RECODR2_25nsreHLT_HIPM+HARVESTDR2.log'

    result = None
    if os.path.exists(requested_path):
        result = browsePath(requested_path)
    else:
        zip_found_in_path = checkForZipsInPath(requested_path)
        if zip_found_in_path:
            zip_name = zip_found_in_path+'.zip'
            path_in_zip = requested_path.split(zip_found_in_path)[1][1:]
            #print zip_found_in_path, zip_name, path_in_zip
            zipObj = zipfile.ZipFile(zip_name,'r')
            # add the full path to the link
            result = browseFileInZip(zipObj, path_in_zip)
            if isinstance(result, list):
                for i in result:
                    i['link'] = zip_found_in_path+'/'+i['link']
            zipObj.close()

    formatResult(result)

