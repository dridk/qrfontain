# qrfontain
Transferring data through a sequence of QR codes using a fountain code.

This tool enables file transfers by generating multiple QR codes using 
the [Luby Transform Code](https://en.wikipedia.org/wiki/Luby_transform_code) thanks to [anrosent/Lt-code](https://github.com/anrosent/LT-code).
This fountain code allows the receiver to scan the QR codes in any order while minimizing the amount of data required 
to retrieve the complete file.

![](qrfontain.gif)


## Installation 

```
git clone git@github.com:dridk/qrfontain
cd qrfontain 
python -m virtualenv venv 
pip install -e . 

```


## Usage

### From python 

Create a fontain of QR code from a file:

```python

import qrfontain 
qrfontain.create_video("big.txt", "big.webm")

```




