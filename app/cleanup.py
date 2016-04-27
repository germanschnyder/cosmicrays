from . import cosmics


def load(filepath) -> object:
    return cosmics.fromfits(filepath, hdu=0, verbose=False)

