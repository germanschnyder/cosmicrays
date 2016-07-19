from astropy.io import fits
import calc_pos

prefixFilename = 'C:/Users/Fabricio/Desktop/images/ic74c9gmq'

LONGITUDE, LATITUDE, HEIGHT = calc_pos.calc_pos(prefixFilename)

print(LONGITUDE)
print(LATITUDE)
print(HEIGHT)

