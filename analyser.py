import os
import sys
import wave
import mutagen
import ffmpy


def load_music( music ):
    try:
        os.remove('temp.wav')
    except:
        pass
    ff = ffmpy.FFmpeg( inputs={music: None}, outputs={'temp.wav' : None})
    ff.run()
    wf = wave.open('temp.wav', 'rb')
    return wf

def analyse_bpm():
    try:
        os.remove('temp.txt')
    except:
        pass
    os.system('vamp-simple-host /usr/lib/vamp/vamp-aubio.so:aubiotempo temp.wav 1 -o temp.txt')
    bpm_file = open('temp.txt', 'r' )
    print( bpm_file )
    counter = [0,0]
    for line in bpm_file:
        counter[0] += float(line.split(" ")[2])
        counter[1] += 1

    return ( counter[0] / counter[1] )

def create_report( path ):
    report = open( 'report.txt', 'a' )
    m = load_music( path )
    tag = mutagen.File( path )
    bpm = analyse_bpm()
    for each in tag:
        print( each, "   :    ",  tag[each])
    #O código abaixo é feio:
    try:
        t1 = str( tag["TIT2"] )
    except:
        t1 = "-"
    try:
        t2 = str( tag["TPE1"] )
    except:
        t2 = "-"
    try:
        t3 = str( tag["TPE2"] )
    except:
        t3 = "-"
    try:
        t4 = str( tag["TALB"] )
    except:
        t4 = "-"
    try:
        t5 = str( tag["TCON"] )
    except:
        t5 = "-"
    try:
        t6 = str( tag["TDOR"] )
    except:
        t6 = "-"

    meta = path + " : " + t1 + " : " + t2 + " : " + t3 + " : " + t4 + " : " + t5 + " : " + t6 + " : " + str( bpm ) + "\n"
    report.write( meta )
    report.close()
    m.close()

def create_list( arq ):
    flist = open( arq )
    path = ""
    for line in flist:
        if( line.find("./") >= 0 ):
            path = line[2:-2]
            print( path )
        else:
            if( line != "\n" ):
                music = line[:-1]
                print( music )
                fullpath = "/home/guru/Music/" + path + "/" + music
                try:
                    create_report( fullpath )
                except:
                    pass

create_list( sys.argv[1] )
#create_report( sys.argv[1] )
