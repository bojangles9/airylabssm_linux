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
- If found it goes into capture mode writing a csv into the folder specificed at the top (running as root as need privilegs to read from com port)
- Streams data into the CSV until the SSM is disconnected
- CSV is then copied to a predefined location using SCP, and deleted locally. If it isn't sucessfully copied remotely the file stays there
- Continues monitoring to see if SSM is plugged back and will establish a new capture file and re-run from scratch

