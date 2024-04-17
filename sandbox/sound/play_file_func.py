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
import jack
import soundfile as sf
import time
from math import sqrt
#filename = fichier audio
# bufferSize = 20
# clientName = file player



# parser = argparse.ArgumentParser(description=__doc__)
# parser.add_argument('filename', help='audio file to be played back')
# parser.add_argument(
#     '-b', '--buffersize', type=int, default=20,
#     help='number of blocks used for buffering (default: %(default)s)')
# parser.add_argument('-c', '--clientname', default='file player',
#                     help='JACK client name')
# parser.add_argument('-m', '--manual', action='store_true',
#                     help="don't connect to output ports automatically")
# args = parser.parse_args()
# if args.buffersize < 1:
#     parser.error('buffersize must be at least 1')





class AudioPlayer:
    def __init__(self, clientName = "file player", bufferSize=20):
        self.clientName = clientName
        self.bufferSize = bufferSize
        self.manual = False
        self.fileName = None
        self.q = queue.Queue(maxsize=self.bufferSize)
        self.event = threading.Event()
        self.mainThread = None
        self.isRunning = False
        self._rmsValues = {}
        self._samplerate = 0
        self._port = 0
        self._cpt = 0
        self._preRmsSum = {}
        self._maxRmsValue = 0

        try:
            self.client = jack.Client(self.clientName)
            self.blocksize = self.client.blocksize
            self.samplerate = self.client.samplerate
            self.client.set_xrun_callback(self.xrun)
            self.client.set_shutdown_callback(self.shutdown)
            self.client.set_process_callback(self.process)
        #    client.activate()
        except KeyboardInterrupt:
            exit('\nInterrupted by user')
        except (queue.Full):
            # A timeout occured, i.e. there was an error in the callback
            exit(1)
        except Exception as e:
            exit(type(e).__name__ + ': ' + str(e))
            
    def load_file(self, fileName):
        self.mainThread = threading.Thread(target=self._play, args=[fileName])
        
    def start(self):
        self.isRunning = True
        self.mainThread.start()
    
    def get_samplerate_fe(self,sf):
        self._samplerate = sf.samplerate
    

    def _play(self, fileName):

        try:
            self.fileName = fileName
            with sf.SoundFile(self.fileName) as f:
                self.get_samplerate_fe(f)
                NCHANNELS = f.channels
                for ch in range(f.channels):
                    self.client.outports.register(f'out_{ch + 1}')
                block_generator = f.blocks(blocksize=self.blocksize, dtype='float32',
                                        always_2d=True, fill_value=0)
                for _, data in zip(range(self.bufferSize), block_generator):
                    self.q.put_nowait(data)  # Pre-fill queue
        #        with client:
                self.client.activate()
                if True:
                    if not self.manual:
                        target_ports = self.client.get_ports(
                            is_physical=True, is_input=True, is_audio=True)
                        NPORTS = len(target_ports)
        #                if len(client.outports) == 1 and len(target_ports) > 1:
                            # Connect mono file to stereo output
                            #for i in range(20):
                        for i in range(NCHANNELS):
                            self.client.outports[i].connect(target_ports[i%NPORTS])
        #                    client.outports[0].connect(target_ports[1])
        #                else:
        #                    for source, target in zip(client.outports, target_ports):
        #                        source.connect(target)
                    timeout = self.blocksize * self.bufferSize / self.samplerate
                    print("Start Sound !")
                    for data in block_generator:
                        self.q.put(data, timeout=timeout)
                    self.q.put(None, timeout=timeout)  # Signal end of file
                    self.event.wait()  # Wait until playback is finished
            print("Sound finished !")
            self.isRunning = False
        except KeyboardInterrupt:
            self.isRunning = False
            print("error1")
            exit('\nInterrupted by user')
        except (queue.Full):
            print("error2")
            self.isRunning = False
            # A timeout occured, i.e. there was an error in the callback
            exit(1)
        except Exception as e:
            print(type(e).__name__ + ': ' + str(e))
            self.isRunning = False
            exit(1)
        
        
    def print_error(self, *args):
        print(*args, file=sys.stderr)


    def xrun(self, delay):
        self.print_error("An xrun occured, increase JACK's period size?")


    def shutdown(self, status, reason):
        self.print_error('JACK shutdown!')
        self.print_error('status:', status)
        self.print_error('reason:', reason)
        self.event.set()


    def stop_callback(self, msg=''):
        if msg:
            self.print_error(msg)
        for port in self.client.outports:
            port.get_array().fill(0)
        self.event.set()
        raise jack.CallbackExit


    def process(self, frames):
        if frames != self.blocksize:
            self.stop_callback('blocksize must not be changed, I quit!')
        try:
            data = self.q.get_nowait()
        except queue.Empty:
            self.stop_callback('Buffer is empty: increase buffersize?')
        if data is None:
            self.stop_callback()  # Playback is finished
        self._cpt += 1024
        for channel, port in zip(data.T, self.client.outports):
            lgth_channel = len(channel)
            port.get_array()[:] = channel
            channel_value = 0
            for i in range(lgth_channel):
                channel_value += channel[i]**2
            if self._port not in self._preRmsSum.keys():
                self._preRmsSum[self._port] = [channel_value]
            else:
                self._preRmsSum[self._port].append(channel_value)
            if (len(self._preRmsSum[self._port]) * lgth_channel >= self._samplerate):
                self._preRmsSum[self._port].pop(0)
            if (self._cpt >= self._samplerate * 0.25):
                sum = 0
                for i in range(len(self._preRmsSum[self._port])):
                    sum += self._preRmsSum[self._port][i]
                self.set_Rms_Values(self._port, lgth_channel, sum)
                self.set_Max_Rms_Values(self._port)
                #print("1 port n°",self._port," : ",self.get_Rms_Values(self._port))
            self._port += 1
        self._port = 0
        if (self._cpt >= self._samplerate * 0.25): #We want to take rms vlaue every 1/4 second, 
            self._cpt = 0

    def set_Rms_Values(self, port, lgth, sum):
        self._rmsValues[port] = sqrt(sum/(lgth * len(self._preRmsSum[port])))

    def get_Rms_Values(self, port):
        return self._rmsValues.get(port)

    def set_Max_Rms_Values(self,port):
        self._maxRmsValue = self._rmsValues.get(port) if self._rmsValues.get(port)>= self._maxRmsValue else self._maxRmsValue
    
    def get_Max_Rms_Values(self):
        return self._maxRmsValue 

    def normalize_Rms_Value(self, value):
        return value/self._maxRmsValue