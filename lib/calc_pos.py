from astropy.time import Time
import math
import numpy
from astropy.utils.iers import iers


def lst(JD, EastLong):
    # --------------------------------------------------------------------
    # lst function         Local Sidereal Time, (mean or apparent),
    #                    for vector of JD's and a given East Longitude.
    # input  : - Vector of JD, in UT1 time scale.
    #          - East Longitude in radians.
    #          - Sidereal Time Type, deprecated
    #            'm' - Mean (default).
    #            'a' - apparent.
    # output : - vector of LST in fraction of day.
    #    By  Eran O. Ofek           August 1999
    # --------------------------------------------------------------------
    # RAD = 57.29577951308232;

    # convert JD to integer day + fraction of day
    TJD = math.floor(JD - 0.5) + 0.5;
    DayFrac = JD - TJD;

    T = (TJD - 2451545.0) / 36525.0;

    GMST0UT = 24110.54841 + 8640184.812866 * T + 0.093104 * T * T - 6.2e-6 * T * T * T;

    # convert to fraction of day in range [0 1)
    GMST0UT = GMST0UT / 86400.0;

    GMST0UT = GMST0UT - math.floor(GMST0UT);
    LST = GMST0UT + 1.0027379093 * DayFrac + EastLong / (2 * math.pi);
    LST = LST - math.floor(LST)
    # print("LST: " + str(LST))

    # switch STType
    # case {'m'}
    #    # do nothing
    # case {'a'}
    #    # calculate nutation
    #    NutMat = nutation(JD);
    #    Obl    = obliquity(JD);
    #    EquationOfEquinox = (RAD.*3600).*NutMat(:,1).*cos(Obl)./15;
    #    LST = LST + EquationOfEquinox./86400;
    # otherwise
    #    error('Unknown sidereal time type');
    #
    return LST


def ecef2geodetic(x, y, z, semia, ecc) -> object:
    # ECEF2GEODETIC Convert geocentric (ECEF) to geodetic coordinates
    #
    #   [PHI, LAMBDA, H] = ECEF2GEODETIC(X, Y, Z, ELLIPSOID) converts point
    #   locations in geocentric Cartesian coordinates, stored in the
    #   coordinate arrays X, Y, Z, to geodetic coordinates PHI (geodetic
    #   latitude in radians), LAMBDA (longitude in radians), and H (height
    #   above the ellipsoid). The geodetic coordinates refer to the
    #   reference ellipsoid specified by ELLIPSOID (a row vector with the
    #   form [semimajor axis, eccentricity]). X, Y, and Z must use the same
    #   units as the semimajor axis;  H will also be expressed in these
    #   units.  X, Y, and Z must have the same shape; PHI, LAMBDA, and H
    #   will have this shape also.
    #
    #   For a definition of the geocentric system, also known as
    #   Earth-Centered, Earth-Fixed (ECEF), see the help for GEODETIC2ECEF.
    #
    #   See also ECEF2LV, GEODETIC2ECEF, GEOCENTRIC2GEODETICLAT, LV2ECEF.

    # Copyright 2005-2009 The MathWorks, Inc.
    # $Revision: 1.1.6.4 $  $Date: 2009/04/15 23:34:43 $

    # Reference
    # ---------
    # Paul R. Wolf and Bon A. Dewitt, "Elements of Photogrammetry with
    # Applications in GIS," 3rd Ed., McGraw-Hill, 2000 (Appendix F-3).

    # Implementation Notes from Rob Comer
    # -----------------------------------
    # The implementation below follows Wolf and DeWitt quite literally,
    # with a few important exceptions required to ensure good numerical
    # behavior:
    #
    # 1) I used ATAN2 rather than ATAN in the formulas for beta and phi.  This
    #    avoids division by zero (or a very small number) for points on (or
    #    near) the Z-axis.
    #
    # 2) Likewise, I used ATAN2 instead of ATAN when computing beta from phi
    #    (conversion from geodetic to parametric latitude), ensuring
    #    stability even for points at very high latitudes.
    #
    # 3) Finally, I avoided dividing by cos(phi) -- also problematic at high
    #    latitudes -- in the calculation of h, the height above the ellipsoid.
    #    Wold and Dewitt give
    #
    #                   h = sqrt(X^2 + Y^2)/cos(phi) - N.
    #
    #    The trick is to notice an alternative formula that involves division
    #    by sin(phi) instead of cos(phi), then take a linear combination of the
    #    two formulas weighted by cos(phi)^2 and sin(phi)^2, respectively. This
    #    eliminates all divisions and, because of the identity cos(phi)^2 +
    #    sin(phi)^2 = 1 and the fact that both formulas give the same h, the
    #    linear combination is also equal to h.
    #
    #    To obtain the alternative formula, we simply rearrange
    #
    #                   Z = [N(1 - e^2) + h]sin(phi)
    #    into
    #                   h = Z/sin(phi) - N(1 - e^2).
    #
    #    The linear combination is thus
    #
    #        h = (sqrt(X^2 + Y^2)/cos(phi) - N) cos^2(phi)
    #            + (Z/sin(phi) - N(1 - e^2))sin^2(phi)
    #
    #    which simplifies to
    #
    #      h = sqrt(X^2 + Y^2)cos(phi) + Zsin(phi) - N(1 - e^2sin^2(phi)).
    #
    #    From here it's not hard to verify that along the Z-axis we have
    #    h = Z - b and in the equatorial plane we have h = sqrt(X^2 + Y^2) - a.

    # Ellipsoid constants
    a = 6378.137;  # Semimajor axis of WGS84 in KM
    fe = 0.0818191908426214864480385813294560648500919342041015625;  # First Eccentricity of WGS84
    e2 = fe ** 2;  # Square of first eccentricity
    ep2 = e2 / (1 - e2);  # Square of second eccentricity
    f = 1 - math.sqrt(1 - e2);  # Flattening
    b = a * (1 - f);  # Semiminor axis

    # Longitude
    lam = math.atan2(y, x);

    # Distance from Z-axis
    rho = math.hypot(x, y);

    # Bowring's formula for initial parametric (beta) and geodetic (phi) latitudes
    beta = math.atan2(z, (1 - f) * rho);
    phi = math.atan2(z + b * ep2 * math.sin(beta) ** 3, rho - a * e2 * math.cos(beta) ** 3);

    # Fixed-point iteration with Bowring's formula
    # (typically converges within two or three iterations)
    betaNew = math.atan2((1 - f) * math.sin(phi), math.cos(phi));
    # print("BETA: " + str(beta))
    # print("BETA_NEW: " + str(betaNew))
    # print(math.isclose(beta, betaNew))
    count = 0;
    while not math.isclose(beta, betaNew) and count < 5:
        beta = betaNew;
        phi = math.atan2(z + b * ep2 * math.sin(beta) ** 3, rho - a * e2 * math.cos(beta) ** 3);
        betaNew = math.atan2((1 - f) * math.sin(phi), math.cos(phi));
        count = count + 1;
        # print(count)

    # Calculate ellipsoidal height from the final value for latitude
    sinphi = math.sin(phi);
    N = a / math.sqrt(1 - e2 * sinphi ** 2);
    h = rho * math.cos(phi) + (z + e2 * N * sinphi) * sinphi - N;

    return phi, lam, h


def calc_pos(img) -> object:
    # The X,Y,Z coordinates are in the geocentric J2000.0 inertial coordinate
    # system. This is a right-handed coordinate system centered in the Earth,
    # with the X axis pointing towards the vernal equinox for the year 2000,
    # the Z-axis pointing towards the north celestial pole for the year 2000,
    # and the Y axis orthogonal to both.

    # tok=['TDATEOBS','TTIMEOBS','TEXPTIME','POSTNSTX','POSTNSTY','POSTNSTZ']

    # hdulist_spt = fits.open(sptFilePath)


    POSTNSTX = img.postnstx  # hdulist_spt[0].header["POSTNSTX"]
    POSTNSTY = img.postnsty  # hdulist_spt[0].header["POSTNSTY"]
    POSTNSTZ = img.postnstz  # hdulist_spt[0].header["POSTNSTZ"]

    DATEOBS = img.observation_date
    TIMEOBS = img.observation_start_time
    # EXPTIME = hdulist_raw[0].header["EXPTIME"]

    # print("POSTNSTX: " + str(POSTNSTX))
    # print("POSTNSTY: " + str(POSTNSTY))
    # print("POSTNSTZ: " + str(POSTNSTZ))
    # print("DATEOBS: " + str(DATEOBS))
    # print("TIMEOBS: " + str(TIMEOBS))
    # print("EXPTIME: " + str(EXPTIME))

    DISTANCE = math.sqrt(POSTNSTX ** 2 + POSTNSTY ** 2 + POSTNSTZ ** 2)
    # print("DISTANCE: " + str(DISTANCE))
    LATITUDE = math.degrees(math.atan(POSTNSTZ / DISTANCE))
    # print("LATITUDE: " + str(LATITUDE))
    RA = math.fmod(math.degrees(math.atan2(POSTNSTY, POSTNSTX)), 360)
    # print("RA: " + str(RA))

    print('About to parse dates...')

    jd = Time(DATEOBS + ' ' + TIMEOBS, scale='utc')
    # print("JulianDate: " + str(jd.jd))

    print('... parsing is done')
    print('Auto download is %s' % str(iers.conf.auto_download))

    # sidereal = jd.sidereal_time('mean', 0)

    print('sideral done')

    # Estoy seguro que puedo usar el sidereal para no tener que implementar lst,
    # pero no se que transformación me esta faltando para pasar de arco sidereal al numero que usan para las operaciones
    # print("sidereal: " + str(sidereal))
    localST = lst(jd.jd, 0)
    # print("localST: " + str(localST))
    GSMT = localST * 2 * math.pi

    print('gsmt done')

    # print("GSMT: " + str(GSMT))
    # print("GSMT.hour: " + str(GSMT.hour))

    ROT = numpy.matrix([[math.cos(GSMT), math.sin(GSMT), 0],
                        [-math.sin(GSMT), math.cos(GSMT), 0], [0, 0, 1]])

    # print("ROT: " + str(ROT))

    POS = numpy.matrix([[POSTNSTX], [POSTNSTY], [POSTNSTZ]])

    # print(POS)

    POSR = ROT.dot(POS)

    # print(POSR)


    print('posr done')

    semia = 6378.137;  # Earth semimajor axis - ellipsoid WGS84
    finv = 298.257223563;  # Inverse of flattening - ellipsoid WGS84
    f = 1 / finv;
    ecc = math.sqrt(2 * f - f ** 2);  # eccentricity

    # print("ECC: " + str(ecc))

    PHI, LAMBDA, HEIGHT = ecef2geodetic(POSR[0, 0], POSR[1, 0], POSR[2, 0], semia, ecc)


    print('geodetic done')

    LONGITUDE = math.degrees(LAMBDA);
    LATITUDE = math.degrees(PHI);

    # print(LONGITUDE)
    # print(LATITUDE)

    return LONGITUDE, LATITUDE, HEIGHT
