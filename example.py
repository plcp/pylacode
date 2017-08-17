# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import witness as wit
import witness.boil


def build_weather_labels():
    w = wit.refine.label(name='weather', size=6)
    w.add(label='warm', value=[True, False])
    w.add(label='cold', value=[False, True], where=slice(0, 2))
    w.add(label='temp', where=slice(0, 2))

    w.add(label='rainy')
    w.add(label='cloudly')
    w.add(label='windy')

    w.add(label='!thunder', value=False)
    w.add(label='thunder', value=[True, None, True], where=slice(3, 6))

    w.add(label='rainstorm', where=slice(1, 4))
    w.add(label='thunderstorm', where=slice(2, 6))
    return wit.table.translation(w)


weather_labels = build_weather_labels()

if __name__ == '__main__':
    o = wit.oracle.new(wit.backends.naive)
    o.add_labels(weather_labels)

    o.submit('cold')
    assert 'cold' in o.query('cold')

    o.submit('rainy')
    assert 'rainy' in o.query('rainstorm')
    assert 'rainstorm' not in o.query('rainstorm')

    o.submit('cloudly')
    assert 'rainstorm' in o.query('rainstorm')
    assert 'thunderstorm' not in o.query('rainstorm')
    assert 'thunderstorm' not in o.query('thunderstorm')

    o.submit('windy')
    assert 'thunderstorm' not in o.query('rainstorm')
    assert 'thunderstorm' in o.query('thunderstorm')
