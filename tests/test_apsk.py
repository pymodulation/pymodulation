#
# test_apsk.py
# 
# Copyright The PyModulation Contributors.
# 
# This file is part of PyModulation library.
# 
# PyModulation library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PyModulation library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with PyModulation library. If not, see <http://www.gnu.org/licenses/>.
# 
#

import numpy as np
import pytest

from pymodulation import APSK

@pytest.mark.parametrize('order,populations', [(16, [4, 12]), (32, [4, 12, 16])])
def test_constellation_geometry_and_labels(order, populations):
    modem = APSK(1200, order=order)
    points = modem._constellation()
    assert len(np.unique(points)) == order
    assert np.mean(abs(points) ** 2) == pytest.approx(1)
    radii, counts = np.unique(np.round(abs(points), 10), return_counts=True)
    assert counts.tolist() == populations
    np.testing.assert_allclose(radii / radii[0], np.arange(1, len(radii) + 1))
    bps = order.bit_length() - 1
    expected = [int(bit) for label in range(order) for bit in f'{label:0{bps}b}']
    assert modem.demodulate(points, 1200 / bps) == expected

@pytest.mark.parametrize('order', [16, 32])
@pytest.mark.parametrize('L', [1, 6, 100])
def test_round_trip_with_noise_and_timing(order, L):
    modem = APSK(1200, order=order)
    data = list(range(256))
    samples, fs, duration = modem.modulate(data, L)
    expected = modem._int_list_to_bit_list(data)
    bps = order.bit_length() - 1
    expected += [0] * (-len(expected) % bps)
    assert samples.dtype == np.complex64
    assert fs == pytest.approx(L * 1200 / bps)
    assert duration == pytest.approx(len(expected) / 1200)
    rng = np.random.default_rng(42)
    noise = 0.01 * (rng.normal(size=len(samples)) + 1j * rng.normal(size=len(samples)))
    assert modem.demodulate(samples + noise, fs) == expected
    baseband, indices = modem.modulate_time_domain(data, L)
    np.testing.assert_allclose(samples, baseband)
    np.testing.assert_array_equal(indices, np.arange(len(samples)))

@pytest.mark.parametrize('order', [16, 32])
def test_empty_input(order):
    modem = APSK(1200, order=order)
    samples, fs, duration = modem.modulate([])
    assert samples.size == 0
    assert duration == 0
    assert modem.demodulate(samples, fs) == []

@pytest.mark.parametrize('order', [4, 8, 64, 16.0, True])
def test_invalid_order(order):
    with pytest.raises(ValueError):
        APSK(1200, order=order)

@pytest.mark.parametrize('baud', [0, -1, np.inf, np.nan, True, '1200'])
def test_invalid_baud(baud):
    with pytest.raises(ValueError):
        APSK(baud)

@pytest.mark.parametrize('L', [0, -1, 1.5, True])
def test_invalid_oversampling(L):
    with pytest.raises(ValueError):
        APSK(1200).modulate([0], L)

@pytest.mark.parametrize('data', [[-1], [256], [1.5], [True]])
def test_invalid_bytes(data):
    with pytest.raises(ValueError):
        APSK(1200).modulate(data)

@pytest.mark.parametrize('fs', [0, -1, np.inf, np.nan, True, 450])
def test_invalid_sample_rate(fs):
    with pytest.raises(ValueError):
        APSK(1200).demodulate(np.ones(10), fs)

@pytest.mark.parametrize('samples', [np.ones(9), np.ones((2, 5)), [np.nan] * 10])
def test_invalid_waveform(samples):
    with pytest.raises(ValueError):
        APSK(1200).demodulate(samples, 3000)
