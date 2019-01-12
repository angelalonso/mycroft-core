# What is this?

Server that receives audio streaming and saves it into a file.

# Requirements
- Install python3, pip3 and ATLAS
E.g. on Ubuntu (or a RaspberryPi):  
apt-get install python3 python3-pip libatlas-base-dev
- pip3 install -r requirements --user


# Testing steps: a Brain Storm!
- OK - The server is up 
- OK - The server can read init of streaming
- OK - The server can read end of streaming
- OK - Anything coming after the init of streaming is saved into a file
- OK - When the read of streaming is detected, the server confirms
- OK - The streaming comes from a microphone and not the read of a file
- After the streaming is ended, the saved file is put to good use
- The server responds to a healthcheck call with OK
- In case of a disconnection in the middle of the transfer, the server asks for retransmission 3 times, then discards

# Thanks:
- Wikimedia Commons for the Image used for testing:
https://upload.wikimedia.org/wikipedia/commons/6/66/Two_Great_Flamingos.jpg
