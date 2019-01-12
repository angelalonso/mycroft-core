#!/usr/bin/env python3

# Thanks to
# https://gist.github.com/rambabusaravanan/a0811f8c9bff440f06ca04d06abdd363#file-client-py-L4 
# https://stackoverflow.com/questions/35344649/reading-input-sound-signal-using-python
import os
import socket
import time

import numpy as np
import scipy.io.wavfile
import math

from random import randint

import pyaudio
import wave

import speech_recognition as sr

from threading import Thread, Lock, Event
from mycroft.messagebus.client.ws import WebsocketClient
from mycroft.messagebus.message import Message
import sys
from os.path import exists
from mycroft.stt import STTFactory
from mycroft.configuration import ConfigurationManager
from mycroft.util.log import LOG
from os import remove


HOST = '0.0.0.0'
PORT = 8045
# TODO: use the tmp folder, avoid hardcoded home folder
FILENAME = '/home/pi/mycroft-core/mycroft/mycroft_stt_server/received.wav'
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
# TODO: do we need two channels?
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5


def server_up():
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


if __name__ == '__main__':
  server_up()
