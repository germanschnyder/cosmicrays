import os.path

from common.instruments import ACS, WFC3, STIS, WFPC2, NICMOS

test_images = {
    ACS.NAME: os.path.join(os.path.dirname(__file__), 'images/ACS/j6mf16lhq_%s.fits' % ACS.DATA_FILE_EXT[0]),
    WFC3.NAME: os.path.join(os.path.dirname(__file__), 'images/WFC3/iaa901jxq_%s.fits' % WFC3.DATA_FILE_EXT[0]),
    STIS.NAME: os.path.join(os.path.dirname(__file__), 'images/STIS/o3sj01ozq_%s.fits' % STIS.DATA_FILE_EXT[0]),
    WFPC2.NAME: os.path.join(os.path.dirname(__file__), 'images/WFPC2/u21u0201t_%s.fits' % WFPC2.DATA_FILE_EXT[0]),
    NICMOS.NAME: os.path.join(os.path.dirname(__file__), 'images/NICMOS/n3t102d3q_%s.fits' % NICMOS.DATA_FILE_EXT[0])
}

stats_images = {
    WFC3.NAME: os.path.join(os.path.dirname(__file__), 'images/WFC3/iaa901jxq_%s.fits' % WFC3.DATA_FILE_EXT[0]),
}
