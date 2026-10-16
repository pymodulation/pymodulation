#
# lora.py
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

from pymodulation.modulation import Modulation

_LORA_DEFAULT_OVERSAMPLING_FACTOR = 100

class LoRa(Modulation):
    """
    Raw LoRa chirp spread spectrum modulator/demodulator.

    Bytes are unpacked MSB first into SF-bit symbols. The last symbol is
    zero-padded, and demodulation retains those padding bits. No packet
    framing, whitening, interleaving or forward error correction is applied.
    Demodulation expects symbol-aligned samples without a frequency offset.
    """

    def __init__(self, bw, sf):
        """
        Class constructor with modulation initialization.

        :param bw: Bandwidth in Hz.
        :type: float

        :param sf: Spreading Factor (7 to 12).
        :type: int

        :return None
        """
        self.set_bandwidth(bw)
        self.set_spreading_factor(sf)

    def set_baudrate(self, baud):
        """
        Reject direct bit-rate configuration; LoRa derives it from BW and SF.

        :param baud: Requested bit rate in bps (not applied).
        :type: int

        :raises ValueError: Always; use set_bandwidth or set_spreading_factor.
        """
        raise ValueError(
            "LoRa bit rate is derived from bandwidth and spreading factor; "
            "use set_bandwidth() or set_spreading_factor() instead"
        )

    def set_bandwidth(self, bw):
        """
        Sets the bandwidth.

        :param bw: Bandwidth in Hz.
        :type: float

        :return None
        """
        if not np.isscalar(bw) or not np.isreal(bw) or not np.isfinite(bw) or bw <= 0:
            raise ValueError("Bandwidth must be a finite positive number")
        self._bandwidth = float(bw)
        if hasattr(self, '_sf'):
            self._compute_params()

    def get_bandwidth(self):
        """
        Gets the bandwidth.

        :return The current bandwidth.
        :rtype: float
        """
        return self._bandwidth

    def set_spreading_factor(self, sf):
        """
        Sets the spreading factor.

        :param sf: Spreading Factor (7 to 12).
        :type: int

        :return None
        """
        if isinstance(sf, (bool, np.bool_)) or not isinstance(sf, (int, np.integer)) or not 7 <= sf <= 12:
            raise ValueError("Spreading factor must be an integer from 7 to 12!")
        self._sf = int(sf)
        self._compute_params()

    def get_spreading_factor(self):
        """
        Gets the spreading factor.

        :return The current spreading factor.
        :rtype: int
        """
        return self._sf

    def modulate(self, data: list, L=_LORA_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Modulate data into LoRa IQ samples (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :param L: Positive integer samples per chip (sample rate = L * bw).
        :type: int

        :return Tuple of (IQ samples, sample rate in Hz, transmission duration in seconds)
        :rtype: tuple(np.ndarray, float, float)
        """
        if isinstance(L, (bool, np.bool_)) or not isinstance(L, (int, np.integer)) or L < 1:
            raise ValueError("Oversampling factor must be a positive integer!")

        data = list(data)

        if any(isinstance(byte, (bool, np.bool_)) or
               not isinstance(byte, (int, np.integer)) or not 0 <= byte <= 255
               for byte in data):
            raise ValueError("Data must contain integer bytes from 0 to 255!")

        bits = self._int_list_to_bit_list(data)
        bits.extend([0] * (-len(bits) % self._sf))
        count = len(bits) // self._sf
        chips = 2 ** self._sf
        samples_per_symbol = chips * int(L)
        samples = np.empty(count * samples_per_symbol, dtype=np.complex64)
        t = np.arange(samples_per_symbol) / L
        for index in range(count):
            symbol = 0
            for bit in bits[index * self._sf:(index + 1) * self._sf]:
                symbol = (symbol << 1) | bit
            # A cyclic shift wraps the chirp frequency within the bandwidth.
            phase_time = (t + symbol) % chips
            samples[index * samples_per_symbol:(index + 1) * samples_per_symbol] = np.exp(
                1j * np.pi * (phase_time ** 2 / chips - phase_time))

        fs = self._bandwidth * L

        return samples, fs, count * self._Ts

    def demodulate(self, samples: np.ndarray, fs) -> list:
        """
        Demodulate LoRa IQ samples into bits.

        :param samples: IQ samples.
        :type: np.ndarray

        :param fs: Sample rate in S/s
        :type: int

        :return Demodulated bits (0 or 1), including final symbol padding.
        :rtype: list
        """
        if not np.isscalar(fs) or not np.isreal(fs) or not np.isfinite(fs) or fs <= 0:
            raise ValueError("Sample rate must be a finite positive number!")

        ratio = fs / self._bandwidth
        L = round(ratio)

        if L < 1 or not np.isclose(ratio, L, rtol=1e-9, atol=1e-9):
            raise ValueError("Sample rate must be an integer multiple of bandwidth!")

        samples = np.asarray(samples)
        chips = 2 ** self._sf
        samples_per_symbol = chips * L

        if samples.ndim != 1 or samples.size % samples_per_symbol:
            raise ValueError("Samples must be a one-dimensional array of complete symbols!")

        if not np.all(np.isfinite(samples)):
            raise ValueError("Samples must be finite")

        t = np.arange(chips)
        downchirp = np.exp(-1j * np.pi * (t ** 2 / chips - t))
        bits = []
        for start in range(0, samples.size, samples_per_symbol):
            # At chip rate, dechirping produces a tone at the symbol's FFT bin.
            dechirped = samples[start:start + samples_per_symbol:L] * downchirp
            symbol = int(np.argmax(np.abs(np.fft.fft(dechirped))))
            bits.extend((symbol >> shift) & 1 for shift in range(self._sf - 1, -1, -1))

        return bits

    def _compute_params(self):
        """
        Update chip period, symbol period and uncoded bit rate.

        :return None
        """
        self._T = 1 / self._bandwidth
        self._Ts = (2**self._sf) * self._T
        self._baudrate = self._sf / self._Ts
