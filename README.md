# EirLabSoundAndLights

## Project architecture

├── config
├── files
│   ├── wav
│   └── yaml
├── light
├── sound
├── jack_launcher.sh
└──Player.py

## Configuration you need to do in order to launch the lights without sudo (a must if you want sound + lights) :

**Needs:** to not be connected to the lights while doing this

First, do this:

- `sudo usermod -aG dialout your_username_on_your_laptop`
- `sudo usermod -aG tty your_username_on_your_laptop`
- `sudo usermod -aG plugdev your_username_on_your_laptop`

Now, **restart** your laptop

Then, do the command `lsusb`

Check for the line containing **"Future Technology Devices International"** (or **"FTDI"**). On my laptop this line appears like :

"Bus 003 Device 002: ID **0403**:**6001** Future Technology Devices International, Ltd FT232 Serial (UART) IC"

The 2 values with 4 digits in **bold** are what you need to remember (here **0403** and **6001** for me, but maybe not for you)

Then, do  `sudo nano /etc/udev/rules.d/99-ftdi.rules`

**Add** the line `SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666"`

Replace **"0403"** and **"6001"** by your own values you got earlier

Then **save** and **exit**

Then **execute** this command line `sudo udevadm control --reload-rules`
