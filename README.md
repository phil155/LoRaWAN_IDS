# LoRaWAN IDS 

This project is an integration of an Intrusion Detection System with an artificial intelligent algorithm KNN. The goal is to use Suricata IDS and convert it into an Anomaly IDS. In other words, use python programming with KNN to correctly classify the behavior of the devices in IoT LoRaWAN protocol.
This was implemented and tested in a Linux machine with version Ubuntu 18.04.05 LTS.

## Principles:
 - Integration of artificial algorithm with Suricata;
 - Detecting the normal behavior and intrusions in IoT devices;
 - Not having access to the payload of the packets.

## Use the LoRaWAN IDS:

You need to install:
- Suricata. I recommend the steps inside the documentation: 
  - https://suricata.readthedocs.io/en/suricata-5.0.4/install.html
  
- CrateDB. I recommend the steps inside the documentation: 
  - https://crate.io/docs/crate/howtos/en/latest/deployment/linux/ubuntu.html
  
- Python3. I recommend this site:
  - https://phoenixnap.com/kb/how-to-install-python-3-ubuntu


After that, you need to copy the files from GitHub to your machine:

	                              Github 	-> to your machine
	/etc/suricata/suricata.yaml 		-> /etc/suricata/suricata.yaml
	/etc/suricata/rules/local.rules 	-> /etc/suricata/rules/local.rules
	/etc/suricata/lua-output/local.lua 	-> /etc/suricata/lua-output/local.lua

Subsequently, you have to create a folder to Python scripts and Lua libraries and copy the files, for example:

	Github 	-> to your machine
	/py/ 	-> ~/IDS/py/
	/lua 	-> ~/IDS/lua/

You have to make sure that the variable `dir` inside of `local.lua` is pointing to the right dir of python scripts.

Right now you are ready to launch the Suricata, you need to execute the next command in directory ~/IDS/lua/.

    sudo suricata -c suricata.yaml -i ens33

(The option `-i ens33` inform to Suricata the interface to analyse the packets)
