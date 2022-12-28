# ALDL Py

A Python program to communicate with and interpret data from 8192 baud GM ALDL ECMs

## Prerequisites

### Supported Vehicles

ALDL Py will be able to communicate with most, if not all, later model 8192 baud ALDL ECMs. Earlier 160 baud ECMs will not work with this program. Support for 160 baud ECMs should be possible, but are not in the scope of this program at this point.

As for interpreting the data from the ECM, the definitions ALDL Py uses are contained within a datastream definition file. ALDL Py currently only ships with an A217 datastream definition file. If you'd like to create a datastream definition file for your vehicle, included in this repo is an archive of documentation for a wide range of datastreams.

[**More info on creating a datastream definition file is included later on in this README.**](#datastream-definitions)

This program was specifically written for and tested with a 1994 Chevrolet G20 van with the L05 engine (5.7L V8 TBI, VIN=K) and 4L60E transmission. Out of the box, only very similar vehicles that share the same datastream definition file will receive the full utility of ALDL Py.

### Serial Hardware

The ECM communicates via by a single bidirectional serial pin. To connect to a PC or device without serial pins, a basic FT232RL USB to serial board can be had fairly inexpensively. In order to connect to the single serial pin of your ECM, both the TX and RX pins will need to be joined together, and the board set to 5V if applicable.

### Python Packages

ALDL Py relies on the pyserial, bitarray and simple_eval packages. To install these packages, run the following command.

```python
pip install -r requirements.txt
```

## Connecting to the ECM

### Finding Your Serial Pin

#### 12 Pin ALDL Connector Pinout (???? - Mid 1995)

|     |     | Notch | Notch |     |     |
|:---:|:---:|:-----:|:-----:|:---:|:---:|
| F   | E   | D     | C     | B   | A   |
| G   | H   | J     | K     | L   | M   |

From around the (possibly?) early 90's up until OBDII was introduced, the majority of GM vehicles typically use pin M for serial communication at 8192 baud. Nonetheless, it is wise to still check the applicable datastream documentation for your vehicle to verify this.

If your vehicle is older, please check the applicable datastream documentation for your vehicle to find the correct pin to connect to for serial communication. 

Pin A will always be ground.

**Note that some cars (not my G20) require a 10k resistor between pin B and pin A for serial transmission to be enabled.**

[**More info on finding the correct datastream documentation for your vehicle is included later on in this README.**](#finding-your-definition)

#### 5 Pin ALDL Connector Pinout (Early 1980s - ????)

| A   | B   | C   | D   | E   |
|:---:|:---:|:---:|:---:|:---:|

Older vehicles using the 5 pin ALDL connector are currently not in the scope of this program. YMMV when it comes to establishing a serial to this connector. Some documentation for this connector should be included in the datastream documentation file for your vehicle. If your vehicle has a 5 pin connector, it will most likely communicate at 160 baud, which is not supported by this program.

[**More info on finding the correct datastream documentation for your vehicle is included later on in this README.**](#finding-your-definition)

### Connecting Your Serial Hardware to the ECM

Now that you have identified your serial and ground pin, it's time to connect your serial hardware to the ECM. The TX and RX pins on your serial hardware will be joined into a single wire that connects to the serial pin on the ALDL connector. The ground pin on your serial hardware will connect to pin A on the ALDL connector.

**ALDL is uses a 5V serial interface. Make sure your serial hardware is set to communicate at 5V.**

## Usage

```bash
aldlecho.py [-h] [-v] [-l LOG | -p PORT] data_stream [data_stream ...]
```

- `p`/`--port` -- The name of the serial port to use. On Mac, something like `/dev/cu.usbserial*`. On Windows, something like `COM1`. On Linux, something like `/dev/ttyS0` or `/dev/ttyACM0`

- OR

- `-l`/`--log` -- The specified data log directory to read from, rather than live data from the ECM.

- `<data_stream_definition> ...` -- The data stream definition file to use.
  See "Data Streams."

**Optional Arguments**

- -h, --help show this help message and exit

- -v, --version show program's version number and exit

## Datastream Definitions

Included with this program is an A217 definition file (definitions/A217/A217.json) that I wrote for my 1994 G20. Chances are, if your vehicle is not a 1/2 ton or 3/4 ton 1994/95 GM Truck/Van/SUV with the L05 5.7L engine and 4l60E transmission, it need a different definition file. Here are the steps towards creating your own definition file.

Included in this repo is an archive (`ALDL-Documentation.7z`) with most of the files necessary to assemble your own data stream definition file. Every file in this archive is a text file and can be opened in a text editor. As these are old files, for compatibility, some may require that your text editor's encoding is set to [Latin-US (DOS)]([Code page 437 - Wikipedia](https://en.wikipedia.org/wiki/Code_page_437))

### Finding Your Definition

Included in `ALDL-Documentation/` is a file `INDEX-Compatibility.pdf`. Within this file you will find a comprehensive list of datastream IDs and the vehicles that match to them. The datastream index is roughly organized as so.

```
  DATA STREAM A136 -- Datastream ID
       ENGINE USAGE: -- Indicates this datastream is for an ECM
              3.1L TBI   (LG6)   (VIN=D)   91 U VAN -- For a 1991 3.1L (LG6) Van
              3.1L TBI   (LG6)   (VIN=D)   92 U VAN -- For a 1992 3.1L (LG6) Van
              3.1L TBI   (LG6)   (VIN=D)   93 U VAN -- For a 1993 3.1L (LG6) Van
              3.1L TBI   (LG6)   (VIN=D)   94 U VAN -- For a 1994 3.1L (LG6) Van
              3.1L TBI   (LG6)   (VIN=D)   95 U VAN -- For a 1995 3.1L (LG6) Van
```

With your datastream ID in hand, check for a corresponding `AXXX.DS` file in `ALDL-Documentation/`. That is your datastream documentation file. 

### Opening the Definition Documentation

With the datastream documentation file open in a text editor, you'll find two things of note near the top of the file. First is the ALDL serial data pin. Keep this pin in mind for when you are attempting to connect your serial hardware to the ALDL connector on the vehicle. Second, is the baud rate. You will want to confirm that it is indeed 8192 baud. As previously stated this program will only work with 8192 baud ECMs and not 160 baud.

### Creating Your Own Datastream Definition File

This section has yet to be created. In the meantime, take a look at `datastreams/A217/A217.json` as a sort of example/template. The final datastream definition file format has yet to be finalized. Once that gets out the the way, I will begin work on documenting the process of creating a definition file.

## License

See `LICENSE.txt` for more information.

## Notes

This project is a fork of aldl_echo Copyright © 2014 Dominick C. Pastore

[GitHub - dominickpastore/aldl_echo: A simple python program to echo data parsed from an ALDL stream](https://github.com/dominickpastore/aldl_echo)
