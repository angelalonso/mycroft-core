#!/usr/bin/env python3

# Thanks to
# https://gist.github.com/rambabusaravanan/a0811f8c9bff440f06ca04d06abdd363#file-client-py-L4 
# https://stackoverflow.com/questions/35344649/reading-input-sound-signal-using-python
import os
import socket
import pyaudio
import wave
import speech_recognition as sr

from threading import Thread, Event
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
import sys
from mycroft.stt import STTFactory
from mycroft.configuration import ConfigurationManager
from mycroft.util.log import LOG

## Copied from Forslund
ws = None
config = ConfigurationManager.get()
                                  
         
def connect():
  ws.run_forever()
             
         
def read_wave_file(wave_file_path):
  '''      
  reads the wave file at provided path and return the expected
  Audio format   
  '''      
  # use the audio file as the audio source
  r = sr.Recognizer()           
  with sr.AudioFile(wave_file_path) as source:
    audio = r.record(source)  
  return audio   
## End of Copied from Forslund


HOST = '0.0.0.0'
PORT = 8045
# TODO: use the tmp folder, avoid hardcoded home folder
FILENAME = '/home/pi/mycroft-core/mycroft/stt_service/received.wav'
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
# TODO: do we need two channels?
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5


def service_up():
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((HOST, PORT))
  s.listen(1)

  frames = []
  p = pyaudio.PyAudio()
  
  while True:
    conn, addr = s.accept()
    print('Incoming client transfer accepted ', addr)
    if os.path.exists(FILENAME):
      os.remove(FILENAME)
    while True:
      try:
        data_in = conn.recv(CHUNK_SIZE)
        if not data_in: 
          print('Transfer ended')
          transmission_end(conn, p, frames)
          frames = []
          break
        frames.append(data_in)
      except (socket.error):
        print('Client connection closed', addr)
        break

  transmission_end(conn, p, frames)

def transmission_end(conn, p, frames):
  conn.close()
  wf = wave.open(FILENAME, 'wb')
  wf.setnchannels(CHANNELS)
  wf.setsampwidth(p.get_sample_size(FORMAT))
  wf.setframerate(RATE)
  wf.writeframes(b''.join(frames))
  wf.close()
  frames = []
  ## Copied from Forslund
  global ws
  global config
  ws = WebsocketClient()
  config = ConfigurationManager.get()
  ConfigurationManager.init(ws)     
  event_thread = Thread(target=connect)
  event_thread.setDaemon(True)      
  event_thread.start() 
  config = config.get("wav_client", {"path": FILENAME})
  try:  
    file_consumer = FileConsumer(file_location=config["path"], emitter=ws)
    file_consumer.start()         
    file_consumer.stop()          
    file_consumer.join()          
  except KeyboardInterrupt:         
    LOG.exception("Manual Key interruption")
    file_consumer.stop()          
    file_consumer.join()          
    sys.exit()       
  ## End of Copied from Forslund


## Copied from Forslund
class FileConsumer(Thread):
  def __init__(self, file_location=FILENAME, emitter=None):
    super(FileConsumer, self).__init__()
    self.path = file_location
    self.stop_event = Event()
    self.stt = None
    self.emitter = emitter

  def run(self):
    LOG.info("Creating STT interface")
    self.stt = STTFactory.create()
    LOG.debug("New wav file found")
    audio = read_wave_file(self.path)
    text = self.stt.execute(audio).lower().strip()
    LOG.info("Speech To Text: " + text)
    self.emitter.emit(
      Message("recognizer_loop:utterance", 
             {"utterances": [text]},
             {"source": "wav_client"}))
    os.remove(self.path)

  def stop(self):
    self.stop_event.set()

## End of Copied from Forslund


if __name__ == '__main__':
  service_up()
