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
        with self.assertRaises(AssertionError):
            zero = TNTfile("/dev/zero")


class TestFourierTransform(unittest.TestCase):
    
    """Test that the Fourier Transform is done correctly
    
    Makes sure that the reference frequency is taken into account properly
    """
    
    def test_ref1(self):
        time_domain = TNTfile("testdata/LiCl_ref1.tnt")
        freq_domain = TNTfile("testdata/LiCl_ref1-ftp.tnt")
        
        lb = freq_domain.TMG2['linebrd'][0, 0]
        ph0 = freq_domain.TMG2['cumm_0_phase'][0, 0]
        
        my_ft = time_domain.LBfft(lb, 1, phase=np.deg2rad(ph0))
        
        assert_allclose(freq_domain.DATA, my_ft)


if __name__ == '__main__':
    unittest.main()