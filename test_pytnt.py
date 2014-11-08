# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:22:29 2013

@author: chris

Test script for the pytnt project
"""

import unittest
import datetime

import numpy as np
from numpy.testing import assert_allclose
from numpy.testing import assert_array_almost_equal

from .processTNT import TNTfile


class TestLoadFile(unittest.TestCase):

    """Tests that pytnt can load files"""

    def test_load_time_domain(self):
        ref1 = TNTfile("testdata/LiCl_ref1.tnt")

        real, imag, usec = np.loadtxt("testdata/LiCl_ref1.txt",
                                      skiprows=3, unpack=True)

        assert_array_almost_equal(ref1.DATA.real.squeeze(), real, decimal=3)
        assert_array_almost_equal(ref1.DATA.imag.squeeze(), imag, decimal=3)
        assert_array_almost_equal(np.arange(ref1.npts[0]) * ref1.dwell[0] * 1e6,
                                  usec, decimal=3)

    def test_load_freq_domain(self):
        ref1 = TNTfile("testdata/LiCl_ref1_ftp.tnt")

        real, imag, hz = np.loadtxt("testdata/LiCl_ref1_ftp.txt",
                                    skiprows=3, unpack=True)

        assert_array_almost_equal(ref1.DATA.real.squeeze(), real, decimal=3)
        assert_array_almost_equal(ref1.DATA.imag.squeeze(), imag, decimal=3)
        assert_array_almost_equal(ref1.freq_Hz(), hz, decimal=3)

    def test_load_fails(self):
        with self.assertRaises(ValueError):
            zero = TNTfile("/dev/zero")

    def test_times(self):
        ref1 = TNTfile("testdata/LiCl_ref1.tnt")

        self.assertGreater(ref1.finish_time, ref1.start_time)
        self.assertEqual(ref1.finish_time - ref1.start_time,
                         datetime.timedelta(seconds=int(ref1.elapsed_time)))
        ## This should be true but isn't
#        self.assertAlmostEqual(ref1.elapsed_time,
#                               ref1.spec_times()[-1] + ref1.spec_acq_time(),
#                               places=0)
        self.assertGreaterEqual(ref1.date, ref1.finish_time)


class TestRefFreq(unittest.TestCase):

    """Tests that the offset and reference frequencies are treated correctly"""

    def test_ref0ppm(self):
        tnt = TNTfile("testdata/7LiCl_ref0ppmS.tnt")

        real, imag, hz = np.loadtxt("testdata/7LiCl_ref0ppmS.txt",
                                    skiprows=3, unpack=True)

        assert_array_almost_equal(tnt.freq_Hz(), hz, decimal=3)

    def test_ref40ppm(self):
        tnt = TNTfile("testdata/7LiCl_ref40ppmS.tnt")

        real, imag, hz = np.loadtxt("testdata/7LiCl_ref40ppmS.txt",
                                    skiprows=3, unpack=True)

        assert_array_almost_equal(tnt.freq_Hz(), hz, decimal=3)

    def test_2118_ref0ppm(self):
        tnt = TNTfile("testdata/7LiCl_2118_ref0ppmS.tnt")

        real, imag, hz = np.loadtxt("testdata/7LiCl_2118_ref0ppmS.txt",
                                    skiprows=3, unpack=True)

        assert_array_almost_equal(tnt.freq_Hz(), hz, decimal=3)

    def test_2118_ref40ppm(self):
        tnt = TNTfile("testdata/7LiCl_2118_ref40ppmS.tnt")

        real, imag, hz = np.loadtxt("testdata/7LiCl_2118_ref40ppmS.txt",
                                    skiprows=3, unpack=True)

        assert_array_almost_equal(tnt.freq_Hz(), hz, decimal=3)

    def test_ppm_points(self):
        tnt = TNTfile("testdata/7LiCl_2118_ref40ppmS.tnt")

        max_ppm = 50
        min_ppm = -35.2
        ppm = tnt.freq_ppm()
        imax, imin = tnt.ppm_points(max_ppm, min_ppm)
        self.assertLess(imax, imin)
        assert np.all(ppm[:imax] > max_ppm)
        assert np.all(ppm[imax:] <= max_ppm)
        assert np.all(ppm[:imin] >= min_ppm)
        assert np.all(ppm[imin:] < min_ppm)

    def test_ppm_points_reverse(self):
        tnt = TNTfile("testdata/7LiCl_ref0ppmS.tnt")

        max_ppm = 5
        min_ppm = -35.2
        reverse_ppm = tnt.freq_ppm()
        imin, imax = tnt.ppm_points_reverse(min_ppm, max_ppm)
        self.assertGreater(imin, imax)
        assert np.all(reverse_ppm[:imin:-1] < min_ppm)
        assert np.all(reverse_ppm[imin::-1] >= min_ppm)
        assert np.all(reverse_ppm[:imax:-1] <= max_ppm)
        assert np.all(reverse_ppm[imax::-1] > max_ppm)


class TestFourierTransform(unittest.TestCase):

    """Test that the Fourier Transform is done correctly

    Makes sure that the reference frequency is taken into account properly
    """

    def test_ref1(self):
        time_domain = TNTfile("testdata/LiCl_ref1.tnt")
        freq_domain = TNTfile("testdata/LiCl_ref1_ftp.tnt")

        lb = freq_domain.linebrd[0]
        ph0 = freq_domain.cumm_0_phase[0]
        ph1 = freq_domain.cumm_1_phase[0]

        my_ft = time_domain.LBfft(lb, 1, phase=np.deg2rad(ph0),
                                  ph1 = np.deg2rad(ph1))

        # Define the absolute tolerance relative to the noise level
        tolerance = np.median(abs(freq_domain.DATA)) / 20
        assert_allclose(my_ft, freq_domain.DATA, atol=tolerance, rtol=1e-5)

    def test_ref2(self):
        time_domain = TNTfile("testdata/LiCl_ref2.tnt")
        freq_domain = TNTfile("testdata/LiCl_ref2_ftp.tnt")

        lb = freq_domain.linebrd[0]
        ph0 = freq_domain.cumm_0_phase[0]
        ph1 = freq_domain.cumm_1_phase[0]

        my_ft = time_domain.LBfft(lb, 1, phase=np.deg2rad(ph0),
                                  ph1 = np.deg2rad(ph1))

        # Define the absolute tolerance relative to the noise level
        tolerance = np.median(abs(freq_domain.DATA)) / 2
        assert_allclose(my_ft, freq_domain.DATA, atol=tolerance, rtol=1e-5)

    def test_ref3(self):
        time_domain = TNTfile("testdata/LiCl_ref3.tnt")
        freq_domain = TNTfile("testdata/LiCl_ref3_ftp.tnt")

        lb = freq_domain.linebrd[0]
        ph0 = freq_domain.cumm_0_phase[0]
        ph1 = freq_domain.cumm_1_phase[0]

        my_ft = time_domain.LBfft(lb, 1, phase=np.deg2rad(ph0),
                                  ph1 = np.deg2rad(ph1))

        # Define the absolute tolerance relative to the noise level
        tolerance = np.median(abs(freq_domain.DATA)) / 4
        assert_allclose(my_ft, freq_domain.DATA, atol=tolerance, rtol=1e-5)

    def test_ref4(self):
        time_domain = TNTfile("testdata/LiCl_ref4.tnt")
        freq_domain = TNTfile("testdata/LiCl_ref4_ftp.tnt")

        lb = freq_domain.linebrd[0]
        ph0 = freq_domain.cumm_0_phase[0]
        ph1 = freq_domain.cumm_1_phase[0]

        my_ft = time_domain.LBfft(lb, 1, phase=np.deg2rad(ph0),
                                  ph1 = np.deg2rad(ph1))

        # Define the absolute tolerance relative to the noise level
        tolerance = np.median(abs(freq_domain.DATA)) / 4
        assert_allclose(my_ft, freq_domain.DATA, atol=tolerance, rtol=1e-5)

    def test_2118_ref40ppm(self):
        time_domain = TNTfile("testdata/7LiCl_2118_ref40ppm.tnt")
        freq_domain = TNTfile("testdata/7LiCl_2118_ref40ppmS.tnt")

        lb = freq_domain.linebrd[0]
        ph0 = freq_domain.cumm_0_phase[0]
        ph1 = freq_domain.cumm_1_phase[0]

        my_ft = time_domain.LBfft(lb, 3, phase=np.deg2rad(ph0),
                                  ph1 = np.deg2rad(ph1))

        # Define the absolute tolerance relative to the noise level
        tolerance = np.median(abs(freq_domain.DATA)) / 20
        assert_allclose(my_ft, freq_domain.DATA, atol=tolerance, rtol=1e-5)


class TestDelayTables(unittest.TestCase):
    
    def test_nut2d(self):
        nut2d = TNTfile("testdata/nut2d.tnt")
        assert_allclose(nut2d.DELAY['de7:2'], np.arange(1.0, 9.0))


if __name__ == '__main__':
    unittest.main()