#
# oqpsk.py
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

from pymodulation.qpsk import QPSK

_OQPSK_DEFAULT_OVERSAMPLING_FACTOR = 100

class OQPSK(QPSK):
    """
    Offset QPSK with the Q arm delayed by half a symbol.

    As in QPSK, baud denotes the bit rate and L the samples per symbol.
    L must be a positive even integer to represent the offset exactly.
    The waveform includes the final half-symbol needed to transmit Q.

    :param baud: Data rate in bits per second.
    :type baud: int or float
    """

    @staticmethod
    def _validate_oversampling(L):
        """
        Validate the samples per symbol required for the Q offset.

        :param L: Even number of samples per symbol, at least two.
        :type L: int

        :return: None.
        :rtype: None

        :raises ValueError: If L is not an even integer greater than or equal to two.
        """
        if isinstance(L, (bool, np.bool_)) or not isinstance(L, (int, np.integer)) or L < 2 or L % 2:
            raise ValueError("OQPSK requires an even integer L >= 2")

    def modulate(self, data: list, L=_OQPSK_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Return complex64 IQ samples, sample rate and waveform duration.

        The sample rate is L * baud / 2. For nonempty data, duration includes the half-symbol Q delay (1 / baud seconds).

        :param data: List of integers containing the data bytes.
        :type data: list[int]

        :param L: Even number of samples per symbol, at least two.
        :type L: int

        :return: IQ samples, sample rate in Hz and transmission duration in seconds.
        :rtype: tuple[numpy.ndarray, float, float]

        :raises ValueError: If L is not an even integer greater than or equal to two.
        """
        samples, fs, _ = super().modulate(data, L)

        return samples, fs, len(samples) / fs

    def modulate_time_domain(self, data, L=_OQPSK_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Return offset IQ samples and their discrete sample indices.

        For N symbols, the signal contains N * L + L / 2 samples.
        Each arm is zero outside its transmission interval. Empty input produces empty arrays.

        :param data: List of integers containing the data bytes.
        :type data: list[int]

        :param L: Even number of samples per symbol, at least two.
        :type L: int

        :return: Baseband IQ signal and sample indices starting at zero.
        :rtype: tuple[numpy.ndarray, numpy.ndarray]

        :raises ValueError: If L is not an even integer greater than or equal to two.
        """
        self._validate_oversampling(L)
        signal, _ = super().modulate_time_domain(data, L)
        if not len(signal):
            return signal, np.arange(0)

        delay = L // 2
        samples = np.zeros(len(signal) + delay, dtype=signal.dtype)
        samples[:len(signal)] = signal.real
        samples[delay:] += 1j * signal.imag

        return samples, np.arange(len(samples))

    def demodulate(self, samples: np.ndarray, fs) -> list:
        """
        Recover bits by aligning the Q arm before QPSK detection.

        Samples must start at the beginning of the I arm and include the final half-symbol of Q, as returned by :meth:`modulate`.

        :param samples: One-dimensional array of baseband IQ samples.
        :type samples: numpy.ndarray

        :param fs: Sample rate in samples per second, corresponding to an even integer number of samples per symbol greater than or equal to two.
        :type fs: int or float

        :return: Demodulated bits, each equal to zero or one.
        :rtype: list[int]

        :raises ValueError: If the sample rate is invalid, samples are not one-dimensional, or the waveform is incomplete.
        """
        samples_per_symbol = fs / (self.get_baudrate() / 2)
        if not np.isfinite(samples_per_symbol) or samples_per_symbol != int(samples_per_symbol):
            raise ValueError("Sample rate must give an integer number of samples per symbol")

        L = int(samples_per_symbol)
        self._validate_oversampling(L)
        samples = np.asarray(samples)
        if samples.ndim != 1:
            raise ValueError("IQ samples must be a one-dimensional array")

        if not samples.size:
            return []

        delay = L // 2
        if len(samples) <= delay or (len(samples) - delay) % L:
            raise ValueError("IQ samples must contain complete OQPSK symbols and the Q delay")

        aligned = samples[:-delay].real + 1j * samples[delay:].imag

        return super().demodulate(aligned, fs)
