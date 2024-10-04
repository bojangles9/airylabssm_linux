# airylabssm_linux
A small tool to let you read the values coming from your AIrylabs SSM via rasperry pi or similar


I run this as service so that it starts automatically when the Pi boots up. 

If you'd like a venv
```
cd /root/airylabssm/
python3.11 -m venv venv
source venv/bin/activate
pip install pyserial
```

#Installation

sudo nano /etc/systemd/system/ssm_service.service
```
[Unit]
Description=SSM Serial Monitor
After=serial-getty@ttyUSB0.service

[Service]
ExecStart=/root/airylabssm/venv/bin/python3 /root/airylabssm/b.py
Restart=always
User=root
WorkingDirectory=/root/airylabssm/

[Install]
WantedBy=multi-user.target
```

General flow of the application:

- Waits to see if the SSM is plugged in and looks for it at /dev/ttyUSB0
- If found it goes into capture mode writing a csv into the folder specified at the top (in initial testing root was needed to read the COM port, but turns out not needed, so can run as regular user)
- Streams data into the CSV until the SSM is disconnected
- CSV is then copied to a predefined location using SCP, and deleted locally. If it isn't successfully copied remotely the file stays there
- Continues monitoring to see if SSM is plugged back and will establish a new capture file and re-run from the beginning


Took some inspiration from this pluging which allowed me to reverse the JAR file and view the connection values and regex which allowed me to parse the data.
http://www.joachim-stehle.de/sssm_eng.html

