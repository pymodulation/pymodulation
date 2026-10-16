#
# test_lora.py
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

from lora import LoRa, _LORA_DEFAULT_OVERSAMPLING_FACTOR

@pytest.mark.parametrize('sf', range(7, 13))
@pytest.mark.parametrize('L', [1, 3])
def test_roundtrip(sf, L):
    data = list(range(256))
    modem = LoRa(125000, sf)
    samples, fs, duration = modem.modulate(data, L)
    expected = modem._int_list_to_bit_list(data)
    expected += [0] * (-len(expected) % sf)
    # A separate receiver must recover the data without transmitter state.
    assert LoRa(125000, sf).demodulate(samples, fs) == expected
    assert samples.dtype == np.complex64
    np.testing.assert_allclose(np.abs(samples), 1, atol=1e-7)
    assert fs == 125000 * L
    assert duration == pytest.approx(len(samples) / fs)

def test_known_zero_chirp():
    modem = LoRa(125000, 8)
    samples, _, _ = modem.modulate([0], 2)
    t = np.arange(512) / 2
    np.testing.assert_allclose(samples, np.exp(1j * np.pi * (t*t / 256 - t)), atol=1e-7)

def test_noise_and_phase_rotation():
    modem = LoRa(125000, 8)
    data = list(range(32))
    samples, fs, _ = modem.modulate(data, 2)
    rng = np.random.default_rng(42)
    noise = rng.normal(0, .1, len(samples)) + 1j * rng.normal(0, .1, len(samples))
    assert modem.demodulate(samples * np.exp(1j * .7) + noise, fs) == modem._int_list_to_bit_list(data)

def test_setters_update_timing():
    modem = LoRa(125000, 7)
    modem.set_bandwidth(250000)
    modem.set_spreading_factor(8)
    samples, fs, duration = modem.modulate([255], 1)
    assert duration == pytest.approx(256 / 250000)
    assert modem.get_baudrate() == pytest.approx(8 * 250000 / 256)
    assert modem.demodulate(samples, fs) == [1] * 8

def test_empty_and_default():
    modem = LoRa(125000, 8)
    samples, fs, duration = modem.modulate([])
    assert samples.size == 0
    assert duration == 0
    assert modem.demodulate(samples, fs) == []
    assert len(modem.modulate([0])[0]) == 256 * _LORA_DEFAULT_OVERSAMPLING_FACTOR

@pytest.mark.parametrize('requested_rate', [1000, 0, -1, np.nan, 7 * 125000 / 128])
def test_set_baudrate_rejected_without_changing_modulation(requested_rate):
    modem = LoRa(125000, 7)
    before, fs, duration = modem.modulate([0xA5], 1)
    with pytest.raises(ValueError, match=r'use set_bandwidth\(\) or set_spreading_factor\(\)'):
        modem.set_baudrate(requested_rate)
    assert modem.get_baudrate() == pytest.approx(7 * 125000 / 128)
    assert modem.get_bandwidth() == 125000
    assert modem.get_spreading_factor() == 7
    after, new_fs, new_duration = modem.modulate([0xA5], 1)
    np.testing.assert_array_equal(after, before)
    assert (new_fs, new_duration) == (fs, duration)

def test_bandwidth_and_spreading_factor_independently_update_bit_rate():
    modem = LoRa(125000, 7)
    modem.set_bandwidth(250000)
    assert modem.get_baudrate() == pytest.approx(7 * 250000 / 128)
    modem.set_spreading_factor(9)
    assert modem.get_baudrate() == pytest.approx(9 * 250000 / 512)
    samples, fs, duration = modem.modulate([0xA5], 2)
    assert fs == 500000
    assert duration == pytest.approx(512 / 250000)
    assert len(samples) / fs == pytest.approx(duration)
    assert modem.demodulate(samples, fs) == [1, 0, 1, 0, 0, 1, 0, 1, 0]

@pytest.mark.parametrize('bw,sf', [(0, 7), (-1, 7), (np.nan, 7), (np.inf, 7), (125000, 6), (125000, 13), (125000, 7.5)])
def test_invalid_configuration(bw, sf):
    with pytest.raises(ValueError):
        LoRa(bw, sf)

@pytest.mark.parametrize('data,L', [([-1], 1), ([256], 1), ([1.5], 1), ([0], 0), ([0], 1.5)])
def test_invalid_modulation(data, L):
    with pytest.raises(ValueError):
        LoRa(125000, 8).modulate(data, L)

@pytest.mark.parametrize('samples,fs', [([1], 125000), ([], 0), ([], 187500), ([[1]], 125000), ([np.nan] * 256, 125000)])
def test_invalid_demodulation(samples, fs):
    with pytest.raises(ValueError):
        LoRa(125000, 8).demodulate(samples, fs)
