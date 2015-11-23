Prediction Market - University of Sydney Conversazione 2015 Demo
================================================================

This program demonstrates the concepts behind the *Prediction Market*,
including server based data storage and prediction.

For more information visit <http://www.ee.usyd.edu.au/cel/farzad/Conversazione2015>.

## Installation

### For server:

Install R and Python (preferably version 3).

In R, Install package dependencies:

> install.package(c("forecast", "devtools", "RJSONIO", "xts"))
> devtools::install_github("fnoorian/diskmemoiser@development")

Install Python dependencies using pip:

> pip3 install werkzeug rpy2 

You can find MS Windows wheels for these packages from
<http://www.lfd.uci.edu/~gohlke/pythonlibs>.

### For client:

Install Python dependencies.

Install PyQt4:
On Linux, probably it is already in your software repository, e.g., on Debian,

> sudo apt-get install python-qt4

On Windows, get the binaries from <http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4>
and install it.

Install other libraries using pip:

> pip3 install requests json-rpc numpy pandas pyqt4 matplotlib

## Running the demo

Change the IP addresses in r_rpc_server.py, and main.py if required.

On the server side, run the JSON-RPC server:

> python3 r_rpc_server.py

On the client side, run the GUI:

> python3 main.py

## Interface and GUI

The top and bottom panel offer static information about the market.

The middle panel contains the demo.
The left most listbox contains name of datasets within the server.
The next listbox contatins name of algorithms on the server.

Selecting a dataset starts a demo.
In the demo, each algorithm is tested on the data

## Technical information

The server is implemented using Python WerkZeug, and only passes
the received HTTP request body to an R function, `do.rpc`, as a 
string through rpy2 package, and sends its returned string value 
back as the HTTP response.

The R function `do.rpc` acts as JSON-RPC dispatcher.

On the client side, a Python script request observed and future data,
iterating through different techniques and datasets.

## License
Copyright (c) 2015 Farzad Noorian <farzad.noorian@gmail.com>.

All files in this project are licensed under the Apache License, Version 2.0 
(the "License"); you may not use these files except in compliance with 
the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR 
CONDITIONS OF ANY KIND, either express or implied. See the License for the 
specific language governing permissions and limitations under the License.

### License Notice
Notice that the dependencies, including PyQt and R, are licensed under GPL, 
hence the full application as a whole shall be licensed under GPL v3.0.

