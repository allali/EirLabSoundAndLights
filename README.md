# EirLabSoundAndLights



## Configuration :



### Light and sound configuration :

- Install **qjackctl** with the command `sudo apt-get install qjackctl`
- Install **Tkinter** with the command `apt install python3-tk`
- Install all the **dependencies** with the command `pip install -r <requirements.txt>`



### Configuration you need to do in order to launch the lights without sudo (a must if you want sound + lights) :

**Needs:** to not be connected to the lights while doing this

First, do this:

- `sudo usermod -aG dialout your_username_on_your_laptop`
- `sudo usermod -aG tty your_username_on_your_laptop`
- `sudo usermod -aG plugdev your_username_on_your_laptop`
- `Create file '/etc/modprobe.d/scarlett.conf' and write 'options snd_usb_audio device_setup=1' in it`

Now, **restart** your laptop

**Plug** your USB/DMX module
Then, do the command `lsusb`

Check for the line containing **"Future Technology Devices International"** (or **"FTDI"**). On my laptop this line appears like :

"Bus 003 Device 002: ID **0403**:**6001** Future Technology Devices International, Ltd FT232 Serial (UART) IC"

The 2 values with 4 digits in **bold** are what you need to remember (here **0403** and **6001** for me, but maybe not for you)

Then, do  `sudo nano /etc/udev/rules.d/99-ftdi.rules`

**Add** the line `SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666"`

Replace **"0403"** and **"6001"** by your own values you got earlier

Then **save** and **exit**

Then **unplug** your USB to DMX module

Then **execute** this command line `sudo udevadm control --reload-rules`

Finally, you can **replug** your USB to DMX module.


## Demo launch :


### Sound part :

Move to the `client` folder, then **run** the command `./jack_launcher.sh start`


### Light part :

Move to the `client` folder, then **run** the command `python3 Player.py`

The list of possible **arguments** for this command :

- **--dynamic**: Using the dynamic light manager
- **-s** or **--soundFile**: Path to audio file that will be played
- **-y** or **--yaml**: Path to one or more yaml files to be played
- **-i** or **--interface**: Visual interface used, default Tkinter. Use `FT232R` to use the DMX lights. 
- **--merge**: Type of merge used if multiple YAML files are provided and if the lights handler is static. Fusion can be done in three ways to specify: MAX (default), MIN, MEAN.
- **--loop**: Repeat playback
- **-b** or **--buffersize**: Number of blocks used for buffering
- **-c** or **--clientname**: JACK client name
- **-m** or **--manual**: Manual connection to output ports



### Reset when finished :

Move to the `client` folder, then **run** the command `./jack_launcher.sh stop`
