# pytnt

<!---
SPDX-FileCopyrightText: 2013 Christopher Kerr

SPDX-License-Identifier: GPL-3.0-or-later
-->

Simple Python module for accessing .tnt NMR data files produced by TecMag's TNMR software.

## Usage

```python
>>> from pytnt import TNTfile

>>> tnt = TNTfile('my-data-file.tnt')

## The raw NMR FID data
>>> fid_data = tnt.DATA

>>> fid_data.dtype
dtype('complex64')
>>> fid_data.shape
(16384, 1, 1, 1)

## The Fourier-transformed spectrum data
>>> spec_data = tnt.freq_ppm()

>>> spec_data.dtype
dtype('float64')
>>> spec_data.shape
(16384,)

## Some metadata
>>> tnt.date
datetime.datetime(2012, 11, 29, 15, 32, 3)
>>> tnt.magnet_field  # in Tesla
2.11
```
