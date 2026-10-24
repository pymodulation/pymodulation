#
# test_qam.py
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

import pytest
import numpy as np

from qam import QAM, _QAM_DEFAULT_OVERSAMPLING_FACTOR

@pytest.mark.parametrize('order', [4, 16, 64, 256, 1024])
@pytest.mark.parametrize('sps', [1, 7, 100])
def test_round_trip_and_timing(order, sps):
    qam = QAM(order, 1200)
    data = list(range(256))
    samples, fs, duration = qam.modulate(data, sps)
    bits, nrz = qam.demodulate(samples, fs)
    expected = qam._int_list_to_bit_list(data)
    bps = int(np.log2(order))
    expected += [0] * ((-len(expected)) % bps)
    assert bits == expected
    assert nrz == [2 * bit - 1 for bit in expected]
    assert samples.dtype == np.complex64
    assert fs == pytest.approx(sps * 1200 / bps)
    assert duration == pytest.approx(len(expected) / 1200)
    assert duration == pytest.approx(len(samples) / fs)

def test_gray_constellation_and_unit_energy():
    qam = QAM(16, 1000)
    # Both axes, in increasing amplitude order, have labels 00, 01, 11, 10.
    data = [0x00, 0x40, 0xC0, 0x80]
    samples, _, _ = qam.modulate(data, 1)
    np.testing.assert_allclose(samples[::2].real, np.array([-3, -1, 1, 3]) / np.sqrt(10))
    samples, _, _ = qam.modulate(list(range(256)), 1)
    assert np.mean(abs(samples) ** 2) == pytest.approx(1)

def test_iq_and_carrier():
    qam = QAM(16, 1000)
    data = [0xAB, 0xCD]
    samples, fs, dur = qam.modulate(data, 10)
    i, q, iq_fs, iq_dur = qam.get_iq(data, 10)
    np.testing.assert_array_equal(i + 1j * q, samples)
    signal, t, carrier_fs, carrier_dur = qam.modulate_time_domain(data, 10)
    phase = 2 * np.pi * 250 * t
    np.testing.assert_allclose(signal, i * np.cos(phase) - q * np.sin(phase))
    np.testing.assert_allclose(t, np.arange(len(samples)) / fs)
    assert (iq_fs, iq_dur) == (fs, dur) == (carrier_fs, carrier_dur)

def test_noise_and_order_change():
    qam = QAM(4, 1200)
    qam.set_order(64)
    assert qam.get_order() == 64
    samples, fs, _ = qam.modulate(list(range(256)), 8)
    rng = np.random.default_rng(42)
    noise = 0.01 * (rng.normal(size=len(samples)) + 1j * rng.normal(size=len(samples)))
    assert qam.demodulate(samples + noise, fs) == qam.demodulate(samples, fs)

@pytest.mark.parametrize('order', [0, 1, 2, 8, 32, -4, 16.0, True])
def test_invalid_order(order):
    with pytest.raises(ValueError):
        QAM(order, 1000)

@pytest.mark.parametrize('baud', [0, -1, float('nan'), float('inf'), True])
def test_invalid_baud(baud):
    with pytest.raises(ValueError):
        QAM(16, baud)

@pytest.mark.parametrize('sps', [0, -1, 1.5, True])
def test_invalid_sps(sps):
    with pytest.raises(ValueError):
        QAM(16, 1000).modulate([0], sps)

@pytest.mark.parametrize('data', [[-1], [256], [1.5], [True]])
def test_invalid_bytes(data):
    with pytest.raises(ValueError):
        QAM(16, 1000).modulate(data)

@pytest.mark.parametrize('samples,fs', [([1j], 0), ([1j], 375), ([1j], 500),
                                       ([[1j]], 250), ([np.nan], 250)])
def test_invalid_demodulation(samples, fs):
    with pytest.raises(ValueError):
        QAM(16, 1000).demodulate(samples, fs)

def test_empty_data_and_defaults():
    qam = QAM(16, 1000)
    samples, fs, dur = qam.modulate([])
    assert samples.size == 0
    assert fs == _QAM_DEFAULT_OVERSAMPLING_FACTOR * 250
    assert dur == 0
    assert qam.demodulate(samples, fs) == ([], [])

def test_package_export():
    from pymodulation import QAM as exported
    assert exported(16, 1000).get_order() == 16
