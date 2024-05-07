#!/usr/bin/env python3

# some commands lines:

# playing a audio file with mplayer
# eirlab@eirlab:~/Downloads$ mplayer -loop 0 -ao jack Daft\ Punk\ -\ Around\ the\ World\ \(1997\).mp3 
#
# using this script:
# 
# eirlab@eirlab:~/Documents/EirlabSoundAndLights/sandbox/sound$ python3 ./play_file.py  10tracks_studio/dreamworks_10_tracks.wav 
#
#


"""Play a sound file.

This only reads a certain number of blocks at a time into memory,
therefore it can handle very long files and also files with many
channels.

NumPy and the soundfile module (http://PySoundFile.rtfd.io/) must be
installed for this to work.

"""
import argparse
import yaml 
try:
    import queue  # Python 3.x
except ImportError:
    import Queue as queue  # Python 2.x
import sys
import threading

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('filename', help='audio file to be played back')
parser.add_argument('number_x', type=float, help='x coordinates')
parser.add_argument('number_y', type=float, help='y coordinates')
parser.add_argument(
    '-b', '--buffersize', type=int, default=20,
    help='number of blocks used for buffering (default: %(default)s)')
parser.add_argument('-c', '--clientname', default='file player',
                    help='JACK client name')
parser.add_argument('-m', '--manual', action='store_true',
                    help="don't connect to output ports automatically")
args = parser.parse_args()
if args.buffersize < 1:
    parser.error('buffersize must be at least 1')

q = queue.Queue(maxsize=args.buffersize)
event = threading.Event()


def print_error(*args):
    print(*args, file=sys.stderr)


def xrun(delay):
    print_error("An xrun occured, increase JACK's period size?")


def shutdown(status, reason):
    print_error('JACK shutdown!')
    print_error('status:', status)
    print_error('reason:', reason)
    event.set()


def stop_callback(msg=''):
    if msg:
        print_error(msg)
    for port in client.outports:
        port.get_array().fill(0)
    event.set()
    raise jack.CallbackExit


def speaker():
    with open('speaker.yml', 'r') as stream:
        try:
            d = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
        
    speakers = []
    speakers_data = d[0]["speakers"]
    for speakerId, speaker in enumerate(speakers_data):
        if speakerId != speaker["id"]:
            ValueError(f"Exepected id {speakerId}, got { speaker['id'] }")
        speakers.append([speaker["coordinates"][0]["x"], speaker["coordinates"][0]["y"], speaker["coordinates"][0]["z"]])
    return speakers

# look for the specification of the process function into jack API (jack.Client.set_process_callback)
def process(frames):
    if frames != blocksize:
        stop_callback('blocksize must not be changed, I quit!')
    try:
        data = q.get_nowait()
    except queue.Empty:
        stop_callback('Buffer is empty: increase buffersize?')
    if data is None:
        stop_callback()  # Playback is finished
    
    target_volumes = []
    # getting volume for each speaker
    for coordinates in speaker(): 
        x = abs(args.number_x - coordinates[0]) 
        y = abs(args.number_y - coordinates[1])
        distance = (x**2 + y**2)**0.5 # distance between the speaker and the sound source
        if (distance > 9):             # radius is set to 9
            target_volumes.append(0.0)
        else:
            target_volumes.append(1.0 - distance/9)
    for i in range(10):
        client.outports[i].get_array()[:] = data.T[0] * target_volumes[i]

try:
    
    import jack
    import soundfile as sf
    import time

    client = jack.Client(args.clientname)
    blocksize = client.blocksize
    samplerate = client.samplerate
    client.set_xrun_callback(xrun)
    client.set_shutdown_callback(shutdown)
    client.set_process_callback(process)
#    client.activate()

    

    with sf.SoundFile(args.filename) as f:
        NCHANNELS = f.channels
        print(NCHANNELS)
        for ch in range(10): # create output port in jack for our client
            client.outports.register(f'out_{ch + 1}')

        # Read bloack of  audio data from file (argument of the script) 
        block_generator = f.blocks(blocksize=blocksize, dtype='float32',
                                   always_2d=True, fill_value=0)
        # put the first blocks into the queue q
        for _, data in zip(range(args.buffersize), block_generator):
            q.put_nowait(data)  # Pre-fill queue
        
            
#        with client:
        
        client.activate() # this activate our jack client
        if True:
            if not args.manual:
                target_ports = client.get_ports( # this is supposed to give us speakers ports lines
                    is_physical=True, is_input=True, is_audio=True)
                print(target_ports)
                
                NPORTS=len(target_ports)

                for port in range(10): # connection between OUR ports to speakers
                    client.outports[port].connect(target_ports[port])
                 
            timeout = blocksize * args.buffersize / samplerate
            # put remaining input audio blocks into q
            for data in block_generator:
                q.put(data, timeout=timeout)
            q.put(None, timeout=timeout)  # Signal end of file
            event.wait()  # Wait until playback is finished
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except (queue.Full):
    # A timeout occured, i.e. there was an error in the callback
    parser.exit(1)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
