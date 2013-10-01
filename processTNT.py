#!/usr/bin/python

import io
from collections import OrderedDict

import numpy as np
from numpy.fft import fftfreq, fftshift
import numpy.dual as npfast

import TNTdtypes


def s(a):
    if isinstance(a, (bytes, np.bytes_)):
        if not isinstance(a, str):  # Python 3
            a = a.decode('latin1')
    return a


class TNTfile:

    def __init__(self, tntfilename):
        
        self.tnt_sections = OrderedDict()

        tntfile = open(tntfilename, 'rb')

        self.tntmagic = np.fromstring(tntfile.read(TNTdtypes.Magic.itemsize),
                                 TNTdtypes.Magic, count=1)[0]

        assert(TNTdtypes.Magic_re.match(s(self.tntmagic)))

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

        tntfile.close()

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

    def LBfft(self, LB, zf, phase=None, logfile=None):
        LBdw = -LB * self.TMAG['dwell'][0]
        npts = self.DATA.shape[0]
        npts_ft = npts * (2 ** zf)

        DCoffset = np.mean(self.DATA[int(npts * 0.75):, :], axis=0, keepdims=True)
        if logfile is not None:
            logfile.write("average DC offset is {0}\n".format(np.mean(DCoffset)))
        
        lbweight = np.exp(LBdw * np.arange(npts, dtype=float))
        DATAlb = (self.DATA - DCoffset) * lbweight[:, np.newaxis, np.newaxis, np.newaxis]

        DATAfft = npfast.fft(DATAlb, n=npts_ft, axis=0)
        DATAfft = fftshift(DATAfft, axes=[0])

        if phase is None: # Phase automatically
            DATAfft = DATAfft * np.exp(-1j * np.angle(np.sum(DATAfft)))
        else:
            DATAfft = DATAfft * np.exp(1j * phase)

        return DATAfft

    def freq_Hz(self, altDATA=None):
        if altDATA is None:
            npts = self.TMAG['actual_npts'][0]
        else:
            npts = altDATA.shape[0]
        dw = self.TMAG['dwell'][0]
        ref_freq = self.TMAG['ref_freq']
        # TODO: find out whether we should add or subtract ref_freq
        #    All my files have a value that is too small to tell the difference
        return fftshift(fftfreq(npts, dw)) + ref_freq

    def freq_ppm(self, altDATA=None):
        NMR_freq = self.TMAG['ob_freq'][0]
        return self.freq_Hz(altDATA) / NMR_freq
        
    def fid_times(self, altDATA=None):
        if altDATA is None:
            npts = self.TMAG['actual_npts'][0]
        else:
            npts = altDATA.shape[0]
        dw = self.TMAG['dwell'][0]
        
        return np.arange(npts) * dw

    def ppm_points(self, max_ppm, min_ppm, altDATA=None):
        ppm = self.freq_ppm(altDATA)
        npts = len(ppm)

        ## Account for the situation in which max or min are out of range
        i_max_ppm = 0
        i_min_ppm = npts

        for i in range(npts):
            if ppm[i] <= max_ppm:
                i_max_ppm = i
                break
        for i in range(i_max_ppm, npts):
            if ppm[i] < min_ppm:
                i_min_ppm = i
                break
        return (i_max_ppm, i_min_ppm)

    def ppm_points_reverse(self, min_ppm, max_ppm, altDATA=None):
        (i_max_ppm, i_min_ppm) = self.ppm_points(max_ppm, min_ppm, altDATA)
        return (i_min_ppm - 1, i_max_ppm - 1)

    def spec_acq_time(self):
        return self.TMAG['scans'] * (self.TMAG['acq_time'] +
                                     self.TMAG['last_delay'])

    def spec_times(self, nspec=None):
        if nspec is None:
            nspec = np.prod(self.TMAG['actual_npts'][1:])
        return np.arange(nspec) * self.spec_acq_time()

    def n_complete_spec(self):
        if self.TMAG['scans'] == self.TMAG['actual_scans']:
            num_spectra = self.TMAG['actual_npts'][1]
        else:  # The last scan was not finished, so omit it
            num_spectra = self.TMAG['actual_npts'][1] - 1
        return num_spectra

    def save_gnuplot_matrix(self, mat_file, max_ppm=float("+Inf"),
                            min_ppm=float("-Inf"), altDATA=None, 
                            times=None, logfile=None):
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
            ## without the 'squeeze', we get some kind of 'output operand requires a reduction, but reduction is not enabled' error ??
            gpt_matrix[1:, i+1] = DATAslice.real[:, i].squeeze()
            if logfile is not None:
                logfile.write('.')
                logfile.flush()
        if logfile is not None:
            logfile.write('Done\n')
            logfile.flush()

        del(gpt_matrix) # flush the file to disk

    def dump_params_txt(self, txtfile):
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