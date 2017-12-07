#!/usr/bin/env python
# --coding:utf-8--
# date:20171024
# author:wuling
# emai:ling.wu@myhealthgene.com

'''
this model setted  to download, extract and update pubchem data automatically
'''
import os
import sys
import threading
reload(sys)
sys.path.append('..')
sys.setdefaultencoding = ('utf-8')
from share.share_v1 import *
from pubchem_v1 import *

version = '1.0'

today = datetime.now().strftime('%y-%m-%d-%H-%M-%S')

model_name = os.path.split(os.path.abspath(__file__))[1]

# buid directory to store raw an extracted data
pubchem_load = os.path.join(dataload,'pubchem')

pubchem_raw = os.path.join(dataraw,'pubchem')

pubchem_store =  os.path.join(datastore,'pubchem')

def downloadPartData():

    haveDownFiles =[ name.split('_213')[0].strip() + '.sdf.gz' for name in os.listdir(pubchem_raw) if name.startswith('Compound')]
   
    ftp =connectFTP()

    allfiles = ftp.nlst()

    noDownFiles = [name for name in allfiles if name not in haveDownFiles]
    print len(noDownFiles)

    bufsize=1024 
    # create a tmp dir to store download data
    tmp_pubchem_one = os.path.join(dataraw,'tmp_pubchem_one')
    createDir(tmp_pubchem_one)

    # tmp_pubchem_muli = os.path.join(dataraw,'tmp_pubchem_muli')
    # createDir(tmp_pubchem_muli)

    # method 1 download one by one
    # start1 = time.clock()
    num = 0
    n = 0

    while  num <  len(noDownFiles):
        try:
            for name in noDownFiles[num:]:
    # for name in noDownFiles[ : :-1]:

                mt = ftp.sendcmd('MDTM {}'.format(name)).replace(' ','-',1)

                save_file_name = '{}_{}_{}.sdf.gz'.format(name.split('.',1)[0].strip(),mt,today)

                save_file_path =os.path.join(tmp_pubchem_one,save_file_name)

                file_handle=open(save_file_path,'wb')

                ftp.retrbinary('RETR /pubchem/Compound/CURRENT-Full/SDF/{}'.format(name) ,file_handle.write ,bufsize) 

                ftp.set_debuglevel(0)
                
                num += 1
                n += 1
                print num,name

        except Exception,e:
            print e
            print '!!!'*100
            ftp = connectFTP()
        ftp.quit()

    # end1 = time.clock()
# 
    # print 'end1-start1',end1-start1
    # method 1 download one by one
    # start2 = time.clock()
    # jobs = list()
    # for name in noDownFiles[:3]:
    #     t = threading.Thread(target=down,args=(ftp,name,tmp_pubchem_muli,1024,))
    #     jobs.append(t)

    # for t in jobs:
    #     t.setDaemon(True)
    #     t.start()

    # t.join()
    # end2 = time.clock()
    # print 'end2-start2',end2-start2

def down(ftp,name,save_dir,bufsize):

        # ftp = connectFTP()

        mt = ftp.sendcmd('MDTM {}'.format(name)).replace(' ','-',1)

        save_file_path =os.path.join(save_dir,'{}_{}_{}.sdf.gz'.format(name.split('.',1)[0].strip(),mt,today))

        file_handle=open(save_file_path,'wb')

        ftp.retrbinary('RETR /pubchem/Compound/CURRENT-Full/SDF/{}'.format(name) ,file_handle.write ,bufsize) 

        ftp.set_debuglevel(0)


def dedup():

    alls = list()
    dup = list()

    for filename in os.listdir(pubchem_raw):
        name = filename.rsplit('_',1)[0].strip()

        if name not in alls:
            alls.append(name)
        else:
            dup.append(name)


    print len(alls)
    print len(dup)

    dupdic = dict()
    for filename in os.listdir(pubchem_raw):
        name = filename.rsplit('_',1)[0].strip()

        if name in dup:
            if name not in dupdic:
                dupdic[name] = list()
            dupdic[name].append(filename)

    for key,val in dupdic.items():
        mt0 = val[0].split('_213-')[1].strip().split('_',1)[0].strip()
        mt1 = val[1].split('_213-')[1].strip().split('_',1)[0].strip()

        if int(mt1) > int(mt0):
            oldfile = val[0]
        elif int(mt1) == int(mt0):
            date0 = int(val[0].rsplit('_',1)[1].strip().split('.sdf.gz')[0].strip().replace('-',''))
            date1 = int(val[0].rsplit('_',1)[1].strip().split('.sdf.gz')[0].strip().replace('-',''))

            if date1 >= date0:
                oldfile = val[0]
            else:
                oldfile = val[1]
        else:
                oldfile = val[1]


        rmpath = os.path.join(pubchem_raw,oldfile)
        command = 'rm {}'.format(rmpath)
        os.popen(command)

def rename():

    for filename in os.listdir(pubchem_raw):

        oldfilepath = os.path.join(pubchem_raw,filename)

        newname = filename.replace('-','')

        newfilepath = os.path.join(pubchem_raw,newname)

        command = 'mv {} {} '.format(oldfilepath,newfilepath)

        os.rename(oldfilepath,newfilepath)


def updatelog():

    pubchem_log = json.load(open(os.path.join(pubchem_load,'pubchem.log')))

    tmp_pubchem_one = os.path.join(dataraw,'tmp_pubchem_one')

    for filename in os.listdir(tmp_pubchem_one):
        if filename.strip().startswith('R'):
            continue
        name = filename.split('_213')[0].strip() + '.sdf.gz'
        mt = '213 ' +  filename.split('_213-',1)[1].strip().split('_',1)[0].strip()
        date = filename.split('.sdf.gz')[0].strip().rsplit('_',1)[1].strip()
        
        pubchem_log[name][-1][0] = mt
        pubchem_log[name][-1][1] = date

    with open(os.path.join(pubchem_load,'pubchem.log'),'w') as wf:

        json.dump(pubchem_log,wf,indent=2)

def testInsert():
        conn = MongoClient('localhost',27017)
        db = conn.PubChem 
        col = db.PubChem_171103

        errorInsertFile  = json.load(open(os.path.join(pubchem_load,'errorInsert.json')))

        for filename in errorInsertFile:

            # rawfile = os.path.join(pubchem_raw,filename.replace('.json','.sdf.gz'))
            
            # store_file_path = standarData(rawfile,pubchem_store)

            print filename
            try:
                filepath = os.path.join(pubchem_store,filename)
                docs  = json.load(open(filepath))

                col.insert_many(docs)
                print filename,'done'
            except Exception,e:
                print e
                print '-'*50
                
if __name__ == '__main__':

    # dedup()
    # errorStandardFile = open('./errorStandardFile')
    # needdownfiles = list()
    # testInsert()