#!/usr/bin/python

import sys
import io
from collections import OrderedDict
import datetime
from time import gmtime
import re
import numpy as np
from numpy.fft import fftfreq, fftshift
import numpy.dual as npfast

from . import TNTdtypes


def s(b):
    """Convert a bytes object to a str, decoding with latin1 if necessary"""
    if isinstance(b, str):  # Python 2
        return b
    elif isinstance(b, bytes):  # Python 3
        return b.decode('latin1')
    else:
        return b


def unsqueeze(M, new_ndim=4):
    """Add extra dimensions to a matrix so it has the desired dimensionality"""
    newshape = np.ones((new_ndim,))
    newshape[:M.ndim] = M.shape
    return np.reshape(M, newshape, order='A')


def convert_si(si_num_list):
    """takes a list of strings, si_num_lst, of the form xxx.xxx<si suffix>
    and returns an array of floats xxx.xxxe-6 or similar, depending on the si
    suffix
    """
    # A dict of all the SI prefixes
    prefix = {'y': 1e-24,  # yocto
              'z': 1e-21,  # zepto
              'a': 1e-18,  # atto
              'f': 1e-15,  # femto
              'p': 1e-12,  # pico
              'n': 1e-9,   # nano
              'u': 1e-6,   # micro
              'm': 1e-3,   # mili
              'c': 1e-2,   # centi
              'd': 1e-1,   # deci
              's': 1,      # seconds
              'k': 1e3,    # kilo
              'M': 1e6,    # mega
              'G': 1e9,    # giga
              'T': 1e12,   # tera
              'P': 1e15,   # peta
              'E': 1e18,   # exa
              'Z': 1e21,   # zetta
              'Y': 1e24,   # yotta
              }
    # go through the items in the list and try to float them. If they don't
    # float...
    for index, item in enumerate(si_num_list):
        try:
            si_num_list[index] = float(item)
        except ValueError:
            # check if the last character is a valid prefix
            if item[-1] in prefix:
                # if it is, set that list element to the rest of the item
                # multiplied by the value appropriate to the prefix
                si_num_list[index] = prefix[item[-1]] * float(item[:-1])
            else:
                # raise if it doesn't work out
                raise ValueError("Couldn't convert delay table entires\
                                 to float! Make sure your suffixes\
                                 correspond to real SI units.")
    #return it as an array
    return np.array(si_num_list)


class TNTfile:

    def __init__(self, tntfilename):

        self.tnt_sections = OrderedDict()

        with open(tntfilename, 'rb') as tntfile:

            self.tntmagic = np.fromstring(tntfile.read(TNTdtypes.Magic.itemsize),
                                          TNTdtypes.Magic, count=1)[0]

            if not TNTdtypes.Magic_re.match(self.tntmagic):
                raise ValueError("Invalid magic number (is '%s' really a TNMR file?): %s" % (tntfilename, self.tntmagic))

            ##Read in the section headers
            tnthdrbytes = tntfile.read(TNTdtypes.TLV.itemsize)
            while(TNTdtypes.TLV.itemsize == len(tnthdrbytes)):
                tntTLV = np.fromstring(tnthdrbytes, TNTdtypes.TLV)[0]
                data_length = tntTLV['length']
                hdrdict = {'offset': tntfile.tell(),
                           'length': data_length,
                           'bool': bool(tntTLV['bool'])}
                if data_length <= 4096:
                    hdrdict['data'] = tntfile.read(data_length)
                    assert(len(hdrdict['data']) == data_length)
                else:
                    tntfile.seek(data_length, io.SEEK_CUR)
                self.tnt_sections[s(tntTLV['tag'])] = hdrdict
                tnthdrbytes = tntfile.read(TNTdtypes.TLV.itemsize)
            # Find and parse the delay tables
            self.DELAY = {}
            # This RegExp should match only bytearrays containing
            # things like "deXX:X" or so.
            delay_re = re.compile(b'de[0-9]+:[0-9]')
            # seek well past the data section so we read as little
            # of the file into memory as possible
            tntfile.seek(self.tnt_sections["PSEQ"]["offset"])
            search_region = tntfile.read()
            # Do the search, and iterate over the matches
            for match in delay_re.finditer(search_region):
                # Lets go back and read the section properly. Offset back by
                # four to capture the delay table name length
                offset = (self.tnt_sections["TMG2"]["offset"]
                          + match.start() - 4)
                tntfile.seek(offset)
                # extract the name length, the name, the delay length,
                # and the delay.
                name_len = np.fromfile(tntfile, dtype=np.int32, count=1)[0]
                delay_name = s(tntfile.read(name_len))
                delay_len = np.fromfile(tntfile, dtype=np.int32, count=1)[0]
                delay = s(tntfile.read(delay_len))
                # Now check for delay tables of length one and discard them
                if len(delay) > 1:
                    delay = delay.split()
                    delay = convert_si(delay)
                    self.DELAY[delay_name] = delay

        assert(self.tnt_sections['TMAG']['length'] == TNTdtypes.TMAG.itemsize)
        self.TMAG = np.fromstring(self.tnt_sections['TMAG']['data'],
                                  TNTdtypes.TMAG, count=1)[0]

        assert(self.tnt_sections['DATA']['length'] ==
               self.TMAG['actual_npts'].prod() * 8)
        ## For some reason we can't set offset and shape together
        #DATA = np.memmap(tntfilename,np.dtype('<c8'), mode='r',
        #                 offset=self.tnt_sections['DATA']['offset'],
        #                 shape=self.TMAG['actual_npts'].tolist(),order='F')
        self.DATA = np.memmap(tntfilename, np.dtype('<c8'), mode='c',
                              offset=self.tnt_sections['DATA']['offset'],
                              shape=self.TMAG['actual_npts'].prod())
        self.DATA = np.reshape(self.DATA,
                               self.TMAG['actual_npts'],
                               order='F')

        assert(self.tnt_sections['TMG2']['length'] == TNTdtypes.TMG2.itemsize)
        self.TMG2 = np.fromstring(self.tnt_sections['TMG2']['data'],
                                  TNTdtypes.TMG2, count=1)[0]


#    def writefile(self, outfilename):
#        outfile = open(outfilename, 'wb')
#        outfile.write(self.tntmagic)
#        for tag in self.tnt_sections_order:
#            tlv = np.asarray(self.tnt_sections[tag].items(), dtype=TNTdtypes.TLV)
#

    @property
    def start_time(self):
        """The time when the NMR acquisition was started

        No timezone information is available"""
        time_struct = gmtime(self.TMAG['start_time'])
        return datetime.datetime(*time_struct[:6])

    @property
    def finish_time(self):
        """The time when the NMR acquisition ended

        No timezone information is available"""
        time_struct = gmtime(self.TMAG['finish_time'])
        return datetime.datetime(*time_struct[:6])

    @property
    def date(self):
        """The time when the file was saved

        No timezone information is available"""
        strlen = self.TMAG['date'].index(b'\x00')
        if sys.version_info.major <= 2:
            datestr = str(self.TMAG['date'][:strlen])
        else:
            datestr = str(self.TMAG['date'][:strlen], encoding='ascii')
        return datetime.datetime.strptime(datestr, "%Y/%m/%d %H:%M:%S")

    def __getattr__(self, name):
        """Expose members of the TMAG and TMG2 structures as attributes"""
        if name in self.TMAG.dtype.names:
            return self.TMAG[name]
        elif name in self.TMG2.dtype.names:
            return self.TMG2[name]
        else:
            raise AttributeError("'%s' is not a member of the TMAG or TMG2 structs" % name)

    def LBfft(self, LB=0, zf=0, phase=None, logfile=None, ph1=0,
              DCoffset=None, altDATA=None):
        if altDATA is None:
            DATA = self.DATA
        else:
            DATA = altDATA
        LBdw = -LB * self.dwell[0] * np.pi  # Multiply by pi to match TNMR
        npts = DATA.shape[0]
        npts_ft = npts * (2 ** zf)

        if DCoffset is None:
            # Taking the last eighth of the points seems to give OK (but not
            # perfect) agreement with the TNMR DC offset correction.
            # This hasn't been tested with enough different values of npts
            # to be sure that this is the right formula.
            DCoffset = np.mean(DATA[int(npts / -8):, :, :, :],
                               axis=0, keepdims=True)
            if logfile is not None:
                logfile.write("average DC offset is %g\n" % np.mean(DCoffset))

        lbweight = np.exp(LBdw * np.arange(npts, dtype=float))
        DATAlb = (DATA - DCoffset) * lbweight[:, np.newaxis, np.newaxis, np.newaxis]

        DATAfft = npfast.fft(DATAlb, n=npts_ft, axis=0)
        DATAfft = fftshift(DATAfft, axes=[0])
        DATAfft /= np.sqrt(npts_ft)  # To match TNMR behaviour

        if phase is None:  # Phase automatically
            DATAfft *= np.exp(-1j * np.angle(np.sum(DATAfft)))
        else:
            DATAfft *= np.exp(1j * (phase + ph1 * np.linspace(-0.5, 0.5, npts_ft))
                              )[:, np.newaxis, np.newaxis, np.newaxis]

        return DATAfft

    def freq_Hz(self, altDATA=None):
        """Returns the frequency axis (in Hz) for the NMR spectrum"""
        if altDATA is None:
            npts = self.actual_npts[0]
        else:
            npts = altDATA.shape[0]
        dw = self.dwell[0]
        ref_freq = self.ref_freq

        return -(fftshift(fftfreq(npts, dw)) + ref_freq)

    def freq_ppm(self, altDATA=None):
        """Returns the frequency axis (in ppm) for the NMR spectrum"""
        NMR_freq = self.ob_freq[0]
        return self.freq_Hz(altDATA) / NMR_freq

    def fid_times(self, altDATA=None):
        """Returns the time axis (in s) for the FID"""
        if altDATA is None:
            npts = self.actual_npts[0]
        else:
            npts = altDATA.shape[0]
        dw = self.dwell[0]

        return np.arange(npts) * dw

    def ppm_points(self, max_ppm, min_ppm, altDATA=None):
        """Given a maximum and minimum frequency (in ppm), return the indices
        of the points in the spectrum that correspond to the beginning and
        one-past-the-end of that range."""
        ppm = self.freq_ppm(altDATA)
        npts = len(ppm)

        # Account for the situation in which max or min are out of range
        i_max_ppm = 0
        i_min_ppm = npts

        # N.B. the ppm array goes from high to low
        i_max_ppm = npts - np.searchsorted(ppm[::-1], max_ppm, side='right')
        i_min_ppm = npts - np.searchsorted(ppm[::-1], min_ppm, side='left')
        return (i_max_ppm, i_min_ppm)

    def ppm_points_reverse(self, min_ppm, max_ppm, altDATA=None):
        (i_max_ppm, i_min_ppm) = self.ppm_points(max_ppm, min_ppm, altDATA)
        # Does not work if i_max_ppm is 0, because the it returns -1
        return (i_min_ppm - 1, i_max_ppm - 1)

    def spec_acq_time(self):
        """Returns the total time taken to acquire one spectrum

        i.e. number of scans * (acquisition time + delay between scans)"""
        return self.scans * (self.acq_time + self.last_delay)

    def spec_times(self, nspec=None):
        """Return the time at which the acquisition of each spectrum began"""
        if nspec is None:
            nspec = np.prod(self.actual_npts[1:])
        return np.arange(nspec) * self.spec_acq_time()

    def n_complete_spec(self):
        """The number of spectra where all the scans have been completed

        Sometimes acquisition is stopped in the middle of acquiring a
        spectrum. In this case, not all the scans of the last spectrum have
        been acquired, so the summed intensity will be less. It might be
        desirable to omit the last spectrum in this case."""
        assert (self.actual_npts[2:] == 1).all()  # TODO handle general case
        if self.scans == self.actual_scans:
            num_spectra = self.actual_npts[1]
        else:  # The last scan was not finished, so omit it
            num_spectra = self.actual_npts[1] - 1
        return num_spectra

    def save_gnuplot_matrix(self, mat_file, max_ppm=np.Inf, min_ppm=-np.Inf,
                            altDATA=None, times=None, logfile=None):
        """Save a file suitable for use as a gnuplot 'binary matrix'

        Only the real part is saved, and it is converted to 32 bit float.
        The frequency goes in the first row, and the acquisition time goes in
        the first column.

        See http://gnuplot.sourceforge.net/docs_4.2/node330.html for a
        description of the data format."""
        ppm = self.freq_ppm(altDATA)
        (i_max_ppm, i_min_ppm) = self.ppm_points(max_ppm, min_ppm, altDATA)

        ppm = ppm[i_max_ppm:i_min_ppm]
        if altDATA is None:
            DATAslice = self.DATA[i_max_ppm:i_min_ppm, :]
            nspec = self.n_complete_spec()
        else:
            DATAslice = altDATA[i_max_ppm:i_min_ppm, :]
            nspec = altDATA.shape[1]

        npts = DATAslice.shape[0]

        gpt_matrix = np.memmap(mat_file, dtype='f4', mode='w+',
                               shape=(npts + 1, nspec + 1), order='F')

        gpt_matrix[0, 0] = npts
        gpt_matrix[1:, 0] = ppm

        if times is None:
            times = self.spec_times(nspec)

        for i in range(nspec):
            gpt_matrix[0, i+1] = times[i]
            ## without the 'squeeze', we get some kind of 'output operand
            ## requires a reduction, but reduction is not enabled' error ??
            gpt_matrix[1:, i+1] = DATAslice.real[:, i].squeeze()
            if logfile is not None:
                logfile.write('.')
                logfile.flush()
        if logfile is not None:
            logfile.write('Done\n')
            logfile.flush()

        del(gpt_matrix)  # flush the file to disk

    def dump_params_txt(self, txtfile):
        """Write a text file with the acquisition and processing parameters"""
        if type(txtfile) == str:
            txtfile = open(txtfile, 'w')

        txtfile.write("TMAG struct (acquisition parameters):\n")
        for fieldname in TNTdtypes.TMAG.names:
            if fieldname.startswith('space'):
                continue
            txtfile.write("{0}:\t{1}\n".format(fieldname, s(self.TMAG[fieldname])))

        txtfile.write("\nTMG2 struct (processing parameters):\n")
        for fieldname in TNTdtypes.TMG2.names:
            if fieldname in ['Boolean_space', 'unused', 'space']:
                continue
            txtfile.write("{0}:\t{1}\n".format(fieldname, s(self.TMG2[fieldname])))
