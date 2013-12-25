"""Determine whether arrays work as well as individual inputs."""

from numpy import array
from ..constants import T0
from ..planets import earth, mars
from ..timescales import JulianDate, julian_date

dates = array([
    julian_date(1969, 7, 20, 20. + 18. / 60.),
    T0,
    julian_date(2012, 12, 21),
    julian_date(2027, 8, 2, 10. + 7. / 60. + 50. / 3600.),
    ])

deltas = array([39.707, 63.8285, 66.8779, 72.])

class Manifold(object):
    def __init__(self, vec, seq):
        self.vec = vec
        self.seq = seq

    def step(self, f):
        self.vec = f(self.vec)
        self.seq = [f(value) for value in self.seq]

    def check(self, name):
        for vslice, value in zip(self.vec, self.seq):
            assert vslice == value

def planetary_position(ut1, delta_t):
    jd = JulianDate(ut1=ut1, delta_t=delta_t)

    yield jd.ut1
    yield jd.tt
    yield jd.tdb

    observer = earth(jd)

    yield observer.position
    yield observer.velocity
    yield observer.jd.ut1
    yield observer.jd.tt
    yield observer.jd.tdb

    astrometric = observer.observe(mars)

    yield astrometric.position
    yield astrometric.velocity

    ra, dec, distance = astrometric.radec()

    yield ra.hours()
    yield dec.degrees()
    yield distance

def test_planetary_position():
    vector_results = list(planetary_position(dates, deltas))

    length = len(dates)
    for vector_value in vector_results:
        assert vector_value.shape[-1] == length

    for i, (date, delta) in enumerate(zip(dates, deltas)):
        scalar_results = list(planetary_position(date, delta))
        for vector_value, scalar_value in zip(vector_results, scalar_results):
            assert (vector_value.T[i] == scalar_value).all()