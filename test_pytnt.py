# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:22:29 2013

@author: chris

Test script for the pytnt project
"""

import unittest

import numpy as np
from numpy.testing import assert_allclose

from processTNT import TNTfile


class TestLoadFile(unittest.TestCase):
    
    """Tests that pytnt can load files"""
    
    def test_load_time_domain(self):
        ref1 = TNTfile("testdata/LiCl_ref1.tnt")
    
    def test_load_freq_domain(self):
        ref1 = TNTfile("testdata/LiCl_ref1-ftp.tnt")
        
    def test_load_fails(self):
        with self.assertRaises(ValueError):
            zero = TNTfile("/dev/zero")


class TestFourierTransform(unittest.TestCase):
    
    """Test that the Fourier Transform is done correctly
    
    Makes sure that the reference frequency is taken into account properly
    """
    
    def test_ref1(self):
        time_domain = TNTfile("testdata/LiCl_ref1.tnt")
        freq_domain = TNTfile("testdata/LiCl_ref1-ftp.tnt")
        
        lb = freq_domain.linebrd[0]
        ph0 = freq_domain.cumm_0_phase[0]
        ph1 = freq_domain.cumm_1_phase[0]
        
        my_ft = time_domain.LBfft(lb * np.pi, 1, phase=np.deg2rad(ph0),
                                  ph1 = np.deg2rad(ph1)) / 128
        
        # Define the absolute tolerance relative to the noise level
        tolerance = np.median(abs(freq_domain.DATA)) / 20
        assert_allclose(my_ft, freq_domain.DATA, atol=tolerance, rtol=1e-5)
    
    def test_ref2(self):
        time_domain = TNTfile("testdata/LiCl_ref2.tnt")
        freq_domain = TNTfile("testdata/LiCl_ref2-ftp.tnt")
        
        lb = freq_domain.linebrd[0]
        ph0 = freq_domain.cumm_0_phase[0]
        ph1 = freq_domain.cumm_1_phase[0]
        
        my_ft = time_domain.LBfft(lb * np.pi, 1, phase=np.deg2rad(ph0),
                                  ph1 = np.deg2rad(ph1)) / 128
        
        # Define the absolute tolerance relative to the noise level
        tolerance = np.median(abs(freq_domain.DATA)) / 20
        assert_allclose(my_ft, freq_domain.DATA, atol=tolerance, rtol=1e-5)
    
    def test_ref3(self):
        time_domain = TNTfile("testdata/LiCl_ref3.tnt")
        freq_domain = TNTfile("testdata/LiCl_ref3-ftp.tnt")
        
        lb = freq_domain.linebrd[0]
        ph0 = freq_domain.cumm_0_phase[0]
        ph1 = freq_domain.cumm_1_phase[0]
        
        my_ft = time_domain.LBfft(lb * np.pi, 1, phase=np.deg2rad(ph0),
                                  ph1 = np.deg2rad(ph1)) / 128
        
        # Define the absolute tolerance relative to the noise level
        tolerance = np.median(abs(freq_domain.DATA)) / 20
        assert_allclose(my_ft, freq_domain.DATA, atol=tolerance, rtol=1e-5)
    
    def test_ref4(self):
        time_domain = TNTfile("testdata/LiCl_ref4.tnt")
        freq_domain = TNTfile("testdata/LiCl_ref4-ftp.tnt")
        
        lb = freq_domain.linebrd[0]
        ph0 = freq_domain.cumm_0_phase[0]
        ph1 = freq_domain.cumm_1_phase[0]
        
        my_ft = time_domain.LBfft(lb * np.pi, 1, phase=np.deg2rad(ph0),
                                  ph1 = np.deg2rad(ph1)) / 128
        
        # Define the absolute tolerance relative to the noise level
        tolerance = np.median(abs(freq_domain.DATA)) / 20
        assert_allclose(my_ft, freq_domain.DATA, atol=tolerance, rtol=1e-5)


if __name__ == '__main__':
    unittest.main()