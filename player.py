import pyaudio
import readchar
import random
import os
import ffmpy
import wave
import sys

def translate( report = "report.txt" ):
    rep = open( report, "r" )
    mdic = []
    for line in rep:
        path, name, artist, album_artist, album, genre, year, bpm = line.split(" : ")
        mdic.extend( [{"path" : path, "name" : name, "artist" : artist, "album_artist" : album_artist, "album" : album, "genres" : genre, "year" : year, "bpm": float( bpm ), "rate" : 70 }] )
    return mdic

def load_music( music ):
    os.remove('temp.wav')
    ff = ffmpy.FFmpeg( inputs={music: None}, outputs={'temp.wav' : None})
    ff.run()
    wf = wave.open('temp.wav', 'rb')
    return wf

def create_stream( p, wf ):
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)
    return stream

def callback(in_data, frame_count, time_info, status):
    data = curr_msc_stream.readframes(frame_count)
    return (data, pyaudio.paContinue)

def fitness( msc, wdic ):
    total = 0
    sv = 5 #peso inicial #35 normal

    try:
        total += wdic[ msc["artist"] ]
    except:
        wdic.update( { msc["artist"] : sv } )
        total += wdic[ msc["artist"] ]

    try:
        total += wdic[ msc["album_artist"] ]
    except:
        wdic.update( { msc["album_artist"] : sv } )
        total += wdic[ msc["album_artist"] ]

    try:
        total += wdic[ msc["album"] ]
    except:
        wdic.update( { msc["album"] : sv } )
        total += wdic[ msc["album"] ]

    try:
        total += wdic[ msc["year"] ]
    except:
        wdic.update( { msc["year"] : sv } )
        total += wdic[ msc["year"] ]

    try:
        total += abs( 100 - abs( wdic[ "bpm" ] - msc["bpm"] ) )
    except:
        wdic["bpm"] = msc["bpm"]
        total += wdic["bpm"]

    genres = msc["genres"].split(", ")
    for genre in genres:
        try:
            total += (1/len(genres)) * wdic[ genre ]
        except:
            wdic.update( { genre : sv } )
            total += (1/len(genres)) * wdic[ genre ]

    return total


def update_fitness( msc, wdic, percent ):
    p1 = 0.35 #peso memória  #.65 normal
    p2 = 1 - p1 #peso musica
    wdic[ msc["artist"] ] = p1 * wdic[ msc["artist"] ] + ( p2 * 100  * percent )
    wdic[ msc["album_artist"] ] = p1 * wdic[ msc["album_artist"] ] + ( p2 * 100  * percent )
    wdic[ msc["album"] ] = p1 * wdic[ msc["album"] ] + ( p2 * 100  * percent )
    wdic[ msc["year"] ] = p1 * wdic[ msc["year"] ] + ( p2 * 100  * percent )

    wdic[ "bpm" ] = p1 * (1 - percent) * wdic[ "bpm" ] + p2 * percent * msc["bpm"]

    for genre in msc["genres"].split(", "):
        wdic[ genre ] = p1 * wdic[ genre ] + ( p2 * 100  * percent )

def update_frame( frame, db, wdic ):
    if( len(frame) <= 0 ):
        winsize = int( 0.10 * (len(db) - 1))
        for i in range(0, winsize):
            r = random.randrange( 0, len( db ) )
            frame.extend( [ db[ r ] ] )
            db.remove( db[ r ] )

    for msc in frame:
        msc["rate"] = fitness( msc, wdic )
        #print( msc["name"], " || ", msc["artist"], " || ", msc["rate"], "\n" )

def reproduction( frame, db ):
    p1 = None
    p2 = None
    rate1 = 0
    rate2 = 0
    for msc in frame:
        if( msc["rate"] > rate1 ):
            rate1 = msc["rate"]
            p1 = msc
        else:
            if( msc["rate"] > rate2 ):
                rate2 = msc["rate"]
                p2 = msc
    #fuck
    child = {}

    r = random.randrange(0, 100)
    if( r <= 50 ):
        child[ "artist"] = p1["artist"]
    if( r > 50 ):
        child[ "artist"] = p2["artist"]

    r = random.randrange(0, 100)
    if( r <= 50 ):
        child[ "album_artist"] = p1["album_artist"]
    if( r > 50 ):
        child[ "album_artist"] = p2["album_artist"]

    r = random.randrange(0, 100)
    if( r <= 50 ):
        child[ "album"] = p1["album"]
    if( r > 50 ):
        child[ "album"] = p2["album"]

    r = random.randrange(0, 100)
    if( r <= 50 ):
        child[ "year"] = p1["year"]
    if( r > 50 ):
        child[ "year"] = p2["year"]

    #30%/30% e 30% de ser a media do bpm dos pais
    r = random.randrange(0, 100)
    child[ "bpm" ] = ( p1["bpm"] + p2["bpm"] ) / 2
    if( r <= 30 ):
        child[ "bpm"] = p1["bpm"]
    if( r >= 70 ):
        child[ "bpm"] = p2["bpm"]

    #40% de chance de herdar os generos
    child["genres"] = ""
    for genre in p1["genres"].split(", "):
        r = random.randrange(0, 100)
        if( r <= 40 ):
            child[ "genres"] = child["genres"] + genre + ", "

    for genre in p2["genres"].split(", "):
        r = random.randrange(0, 100)
        if( r <= 40 ):
            child[ "genres"] = child["genres"] + genre + ", "

    child[ "genres" ] = child["genres"][:-2]

    cand = []
    #escolhendo candidatos: Como um cruzamento pode gerar muita coisa inválida, procuro a musica mais parecida com o que seria o filho
    for each in db:
        if( each["artist"] == child["artist"] or each["album_artist"] == child["album_artist"] or each["album"] == child["album"]  ):
            cand.extend( [ each ] )

    best = [ 1, 0 ]
    for each in cand:
        value = 0
        if( each["year"] == child["year"] ):
             value += 100
        for cgenre in child["genres"].split(", "):
            for genre in each["genres"].split(", "):
                if( cgenre == genre ):
                    value += 30
        value += abs( 100 - abs( child["bpm"] - each["bpm"] ))
        if( value > best[1] ):
            best[0] = each

    try:
        db.remove( best[0] )
        frame.extend( [ best[0] ] )
        return 1
    except:
        print( "ERRO: Não foi possivel criar um filho \n")
        return 0

def mutation( frame, db, count ):
    mut = frame[ random.randrange( 0, len( frame ) - 1 ) ]
    for each in db:
        if( each["artist"] == mut["artist"] or each["album_artist"] == mut["album_artist"] or each["album"] == mut["album"]  ):
            frame.extend( [ each ] )
            db.remove( each )
            count -= 1
        if( count == 0 ):
            return 1
    return 0

def randkill( frame, db, e ):
    for i in range( 0,  e ):
        r = random.randrange( 0, len( frame ) - 1 )
        db.extend( [ frame[ r ] ] )
        frame.remove( frame[ r ] )

def bestfit( frame, db, e ):
    for i in range( 0, e ):
        lr = 999
        lesser = None
        for msc in frame:
            if( msc["rate"] < lr ):
                lesser = msc
        if( lesser ):
            db.extend( [ lesser ] )
            frame.remove( lesser )

def evolve( frame, db, repcount, mutcount ):
    #reproduz
    i = 0
    e = 0
    while( i < repcount ):
        e += reproduction( frame, db )
        i += 1

    #muta
    i = 0
    while( i < mutcount ):
        e += 2 * mutation( frame, db, 2 )
        i += 1

    #fight
    update_frame( frame, db, wdic )
    #kill

    print( len( frame ), repcount + (mutcount * 2 ), e, "\n" )

    #randkill( frame, db, e )
    bestfit( frame, db, e )

    print( len( frame ), repcount + (mutcount * 2 ), e, "\n" )

    #salute!



def chose_next( frame, db, wdic ):
    global curr_msc, curr_msc_stream

    try:
        update_fitness( curr_msc, wdic, ( curr_msc_stream.tell() / curr_msc_stream.getnframes() )  )
        update_frame( frame, db, wdic )
        evolve( frame, db, int( 0.2 * len( frame ) ), int( 0.3 * len( frame ) ) )
        update_frame( frame, db, wdic )
    except:
        update_frame( frame, db, wdic )

    rate = 0;
    for msc in frame:
        if( msc["rate"] > rate ):
            rate = msc["rate"]
            curr_msc = msc


    frame.remove( curr_msc )
    return load_music( curr_msc["path"] )


p = pyaudio.PyAudio()
mdic = translate()
wdic = {}
frame = []
played = []
curr_msc = {}
curr_msc_stream = chose_next( frame, mdic, wdic )
print( curr_msc )
stream = create_stream( p, curr_msc_stream )

stream.start_stream()
print( "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
print( "Song: ", curr_msc["name"], " | Artist: ", curr_msc["artist"],  " | Rate: ", curr_msc["rate"], "\nAlbum: ", curr_msc["album"], " | Genres: ", curr_msc["genres"], "\n")
print("Frame Lenght: ", len( frame ), "  | Database Lenght: ", len( mdic ), " | Played so far: ", len( played ), " \n" )


playing = 1
paused = 0
lock = 0
while( playing ):
    try:
        if( not lock ):
            key = readchar.readkey()

        if( key == 'p' ):
            if( paused ):
                paused = 0
                stream.start_stream()
            else:
                paused = 1
                stream.stop_stream()

        if( key == 'n' or ( not stream.is_active() and not paused ) ):
            stream.stop_stream()
            played.extend( [ curr_msc ] )
            curr_msc_stream = chose_next( frame, mdic, wdic )
            stream.close()
            stream = create_stream( p, curr_msc_stream )
            stream.start_stream()
            print( "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
            print( "Song: ", curr_msc["name"], " | Artist: ", curr_msc["artist"],  " | Rate: ", curr_msc["rate"], "\nAlbum: ", curr_msc["album"], " | Genres: ", curr_msc["genres"], "\n")
            print("Frame Lenght: ", len( frame ), "  | Database Lenght: ", len( mdic ), " | Played so far: ", len( played ), " \n" )

        if( key == "s" ):
            print( "Song: ", curr_msc["name"], " | Artist: ", curr_msc["artist"],  " | Rate: ", curr_msc["rate"], "\nAlbum: ", curr_msc["album"], " | Genres: ", curr_msc["genres"], "\n")
            print("Frame Lenght: ", len( frame ), "  | Database Lenght: ", len( mdic ), " | Played so far: ", len( played ), " \n" )
            print(100 * ( curr_msc_stream.tell() / curr_msc_stream.getnframes() ), "%\n")

        if( key == "f" ):
            for each in frame:
                print( each["name"], " || ", each["artist"], " || ", each["rate"], "\n" )


        if( key == 'l' ):
            print("keyboard locked, ctrl+c to unlock it.")
            key = 'z'
            lock = 1

        if( key == 'q' ):
            playing = 0

    except KeyboardInterrupt:
        print("keyboard unlocked.")
        lock = 0


#clean up
stream.close()
curr_msc_stream.close()
p.terminate()
