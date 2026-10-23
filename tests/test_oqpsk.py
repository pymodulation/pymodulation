#
# test_oqpsk.py
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

from oqpsk import OQPSK, _OQPSK_DEFAULT_OVERSAMPLING_FACTOR

# Shared oversampling factor used in all tests (kept small for speed)
L = 10

@pytest.fixture
def oqpsk():
    return OQPSK(baud=1000)

def test_modulate_time_domain_uses_normalized_gray_constellation(oqpsk):
    signal, time = oqpsk.modulate_time_domain([0x1B], L)

    expected_symbols = np.array([
        1 + 1j, -1 + 1j, 1 - 1j, -1 - 1j,
    ]) / np.sqrt(2)
    base = np.repeat(expected_symbols, L)
    expected = np.zeros(len(base) + L // 2, dtype=complex)
    expected[:len(base)] = base.real
    expected[L // 2:] += 1j * base.imag
    np.testing.assert_array_equal(signal, expected)
    np.testing.assert_array_equal(time, np.arange(len(signal)))

def test_modulate_returns_complex_samples_and_oqpsk_timing(oqpsk):
    samples, fs, duration = oqpsk.modulate([0xA5, 0x5A], L)

    assert samples.dtype == np.complex64
    assert len(samples) == 2 * 8 // 2 * L + L // 2
    assert fs == pytest.approx(oqpsk.get_baudrate() / 2 * L)
    assert duration == pytest.approx(17 / oqpsk.get_baudrate())

@pytest.mark.parametrize("data", [
    [0x00],
    [0xFF],
    [0xA5],
    [0xDE, 0xAD, 0xBE, 0xEF],
    list(range(256)),
])
def test_round_trip_recovers_bits(oqpsk, data):
    samples, fs, _ = oqpsk.modulate(data, L)

    assert oqpsk.demodulate(samples, fs) == oqpsk._int_list_to_bit_list(data)

def test_round_trip_with_small_complex_awgn(oqpsk):
    data = list(range(16))
    samples, fs, _ = oqpsk.modulate(data, L)
    rng = np.random.default_rng(seed=42)
    noise = rng.normal(0, 0.05, len(samples)) + 1j * rng.normal(0, 0.05, len(samples))

    assert oqpsk.demodulate(samples + noise, fs) == oqpsk._int_list_to_bit_list(data)

@pytest.mark.parametrize("factor", [2, 6, _OQPSK_DEFAULT_OVERSAMPLING_FACTOR])
def test_round_trip_with_even_oversampling(oqpsk, factor):
    data = list(range(256))
    samples, fs, duration = oqpsk.modulate(data, factor)
    assert oqpsk.demodulate(samples, fs) == oqpsk._int_list_to_bit_list(data)
    assert duration == pytest.approx(len(samples) / fs)

@pytest.mark.parametrize("factor", [0, -2, 1, 3, 2.5, True])
def test_rejects_invalid_oversampling(oqpsk, factor):
    with pytest.raises(ValueError):
        oqpsk.modulate([0x00], factor)

def test_empty_input(oqpsk):
    samples, fs, duration = oqpsk.modulate([])
    assert samples.size == 0
    assert duration == 0
    assert oqpsk.demodulate(samples, fs) == []

def test_i_and_q_never_change_together(oqpsk):
    samples, _, _ = oqpsk.modulate([0x33, 0xCC], L)
    assert not np.any((np.diff(samples.real) != 0) & (np.diff(samples.imag) != 0))

@pytest.mark.parametrize("fs", [0, 1500, 1250, float("nan")])
def test_rejects_invalid_sample_rate(oqpsk, fs):
    with pytest.raises(ValueError):
        oqpsk.demodulate(np.ones(45), fs)


def test_rejects_incomplete_waveform(oqpsk):
    samples, fs, _ = oqpsk.modulate([0xA5], L)
    with pytest.raises(ValueError):
        oqpsk.demodulate(samples[:-1], fs)

def test_public_import():
    from pymodulation import OQPSK as PublicOQPSK, QPSK
    assert issubclass(PublicOQPSK, QPSK)
