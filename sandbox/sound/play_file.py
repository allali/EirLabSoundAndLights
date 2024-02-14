#!/usr/bin/env python3

"""Play a sound file.

This only reads a certain number of blocks at a time into memory,
therefore it can handle very long files and also files with many
channels.

NumPy and the soundfile module (http://PySoundFile.rtfd.io/) must be
installed for this to work.

"""
import argparse
try:
    import queue  # Python 3.x
except ImportError:
    import Queue as queue  # Python 2.x
import sys
import threading
import numpy as np
from math import *

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('filename', help='audio file to be played back')
parser.add_argument(
    '-b', '--buffersize', type=int, default=20,
    help='number of blocks used for buffering (default: %(default)s)')
parser.add_argument('-c', '--clientname', default='file player',
                    help='JACK client name')
parser.add_argument('-m', '--manual', action='store_true',
                    help="don't connect to output ports automatically")
parser.add_argument('-l', '--loop', action='store_true')
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

def absolute(x):
    if (x < 0):
        return -x
    return x

rms = {}
rms_values = {}
def process(frames):

    if frames != blocksize:
        stop_callback('blocksize must not be changed, I quit!')
    try:
        data = q.get_nowait()
    except queue.Empty:
        stop_callback('Buffer is empty: increase buffersize?')
    if data is None:
        stop_callback()  # Playback is finished
    k = 0
    for channel, port in zip(data.T, client.outports):
        port.get_array()[:] = channel
        channel_value = 0
        for i in range(len(channel)):
            channel_value += channel[i]
        if k not in rms.keys():
            rms[k] = channel
            rms_values[k] = channel_value
        else:
            rms[k] = np.concatenate((rms[k],channel))
            rms_values[k] += channel_value
        if (len(rms[k]) >= 44100):
            print(sqrt(rms_values[k]**2/44100))
            for i in range(len(channel)):
                channel_value -= rms_values[k]
                rms[k] = np.delete(rms[k], 0)
        k += 1




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
    def playsound():
        with sf.SoundFile(args.filename) as f:
            NCHANNELS = f.channels
            for ch in range(f.channels):
                client.outports.register(f'out_{ch + 1}')
            block_generator = f.blocks(blocksize=blocksize, dtype='float32',
                                    always_2d=True, fill_value=0)
            for _, data in zip(range(args.buffersize), block_generator):
                q.put_nowait(data)  # Pre-fill queue
    #        with client:
            client.activate()
            if True:
                if not args.manual:
                    target_ports = client.get_ports(
                        is_physical=True, is_input=True, is_audio=True)
                    NPORTS=len(target_ports)
    #                if len(client.outports) == 1 and len(target_ports) > 1:
                        # Connect mono file to stereo output
                        #for i in range(20):
                    for i in range(NCHANNELS):
                        client.outports[i].connect(target_ports[i%NPORTS])
    #                    client.outports[0].connect(target_ports[1])
    #                else:
    #                    for source, target in zip(client.outports, target_ports):
    #                        source.connect(target)
                timeout = blocksize * args.buffersize / samplerate
                for data in block_generator:
                    q.put(data, timeout=timeout)
                q.put(None, timeout=timeout)  # Signal end of file
                event.wait()  # Wait until playback is finished

    if(args.loop):
        while(1):
            playsound()
    else:
        playsound()
except KeyboardInterrupt:
    parser.exit('\nInterrupted by user')
except (queue.Full):
    # A timeout occured, i.e. there was an error in the callback
    parser.exit(1)
except Exception as e:
    parser.exit(type(e).__name__ + ': ' + str(e))
