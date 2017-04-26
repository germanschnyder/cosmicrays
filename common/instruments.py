class Instrument:
    NAME = ''
    DATA_FILE_EXT = []
    POS_FILE_EXT = ''
    WIDTH = 0
    HEIGHT = 0


class ACS(Instrument):
    NAME = 'ACS'
    DATA_FILE_EXT = ['flt']
    POS_FILE_EXT = 'spt'
    WIDTH = 2048
    HEIGHT = 4096


class COS(Instrument):
    NAME = 'COS'
    DATA_FILE_EXT = ['flt_a', 'flt_b']
    POS_FILE_EXT = 'spt'
    WIDTH = 16384
    HEIGHT = 1024


class FGS(Instrument):
    NAME = 'FGS'
    DATA_FILE_EXT = ['a1f', 'a2f', 'a3f']
    POS_FILE_EXT = 'dmf'
    WIDTH = 100878
    HEIGHT = 7


class NICMOS(Instrument):
    NAME = 'NICMOS'
    DATA_FILE_EXT = ['raw', 'mos']
    POS_FILE_EXT = 'spt'
    WIDTH = 256
    HEIGHT = 256


class STIS(Instrument):
    NAME = 'STIS'
    DATA_FILE_EXT = ['flt']
    POS_FILE_EXT = 'spt'
    WIDTH = 1024
    HEIGHT = 1024


class WFC3(Instrument):
    NAME = 'WFC3'
    DATA_FILE_EXT = ['flt']
    POS_FILE_EXT = 'spt'
    WIDTH = 2051
    HEIGHT = 4096


class WFPC2(Instrument):
    NAME = 'WFPC2'
    DATA_FILE_EXT = ['c0m']
    POS_FILE_EXT = 'shm'
    WIDTH = 800
    HEIGHT = 800


class InstrumentUtils:

    @staticmethod
    def instrument_from_name(name):
        if ACS.NAME == name:
            return ACS

        if COS.NAME == name:
            return COS

        if FGS.NAME == name:
            return FGS

        if NICMOS.NAME == name:
            return NICMOS

        if STIS.NAME == name:
            return STIS

        if WFC3.NAME == name:
            return WFC3

        if WFPC2.NAME == name:
            return WFPC2
