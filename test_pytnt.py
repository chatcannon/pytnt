# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 20:22:29 2013

@author: chris

Test script for the pytnt project
"""

import unittest

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
        

if __name__ == '__main__':
    unittest.main()