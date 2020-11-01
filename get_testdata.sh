#!/bin/sh

# SPDX-License-Identifier: GPL-3.0-or-later

## Test data are posted on FigShare, listed in this article
# http://figshare.com/articles/pytnt_test_data/1228508

mkdir -p testdata
cd testdata

/usr/bin/wget --no-clobber --input-file=- <<END_FILELIST
http://files.figshare.com/1778519/LiCl_ref2.txt
http://files.figshare.com/1778520/7LiCl_ref0ppmS.tnt
http://files.figshare.com/1778521/7LiCl_2118_ref0ppm.tnt
http://files.figshare.com/1778522/7LiCl_2118_ref40ppmS.tnt
http://files.figshare.com/1778523/LiCl_ref4.tnt
http://files.figshare.com/1778524/LiCl_ref2_ftp.tnt
http://files.figshare.com/1778525/LiCl_ref3.tnt
http://files.figshare.com/1778526/7LiCl_ref40ppm.txt
http://files.figshare.com/1778527/LiCl_ref3_ftp.txt
http://files.figshare.com/1778528/LiCl_ref2.tnt
http://files.figshare.com/1778529/LiCl_ref4.txt
http://files.figshare.com/1778530/LiCl_ref2_ftp.txt
http://files.figshare.com/1778531/LiCl_ref3.txt
http://files.figshare.com/1778542/7LiCl_2118_ref0ppmS.txt
http://files.figshare.com/1778543/7LiCl_ref0ppm.txt
http://files.figshare.com/1778544/7LiCl_ref40ppmS.txt
http://files.figshare.com/1778545/LiCl_ref4_ftp.tnt
http://files.figshare.com/1778546/7LiCl_2118_ref40ppm.txt
http://files.figshare.com/1778547/LiCl_ref1.txt
http://files.figshare.com/1778548/7LiCl_2118_ref0ppmS.tnt
http://files.figshare.com/1778549/7LiCl_ref0ppm.tnt
http://files.figshare.com/1778550/LiCl_ref1_ftp.txt
http://files.figshare.com/1778551/nut2d.tnt
http://files.figshare.com/1778552/notuneAS_083.750_085.505MHz_2d.tnt
http://files.figshare.com/1784815/7LiCl_ref40ppmS.tnt
http://files.figshare.com/1784816/LiCl_ref1.tnt
http://files.figshare.com/1784817/7LiCl_ref0ppmS.txt
http://files.figshare.com/1784818/LiCl_ref3_ftp.tnt
http://files.figshare.com/1784819/7LiCl_2118_ref40ppmS.txt
http://files.figshare.com/1784820/7LiCl_2118_ref40ppm.tnt
http://files.figshare.com/1784822/LiCl_ref1_ftp.tnt
END_FILELIST
