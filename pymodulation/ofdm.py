#
# ofdm.py
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

_OFDM_DEFAULT_OVERSAMPLING_FACTOR = 100

class OFDM(Modulation):
    """
    OFDM modulation
    """

    def __init__(self, baud):
        """
        Initialize the OFDM modulation.

        :param baud: Finite positive bit rate in bps.
        :type baud: int or float

        :raises ValueError: If the bit rate is invalid.
        """
        super().__init__(baud)

    def modulate(self, data, sps=_OFDM_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Return (complex64 IQ samples, sample rate, duration).

        Input contains integer bytes, serialized most significant bit first.
        Each symbol uses its first half of bits for I and its second for Q.
        Rectangular pulses repeat each symbol ``sps`` times.

        :param data: Input integer bytes, each in the range 0 to 255.
        :type data: iterable[int]

        :param sps: Positive integer samples per symbol.
        :type sps: int

        :returns: Complex64 baseband IQ samples, sample rate in S/s, and signal duration in seconds, including final-symbol padding.
        :rtype: tuple[numpy.ndarray, float, float]

        :raises ValueError: If the input bytes or samples per symbol are invalid.
        """
        pass

    def get_iq(self, data, sps=_OFDM_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Compute the in-phase and quadrature components.

        :param data: Input integer bytes, each in the range 0 to 255.
        :type data: iterable[int]

        :param sps: Positive integer samples per symbol.
        :type sps: int

        :returns: I samples, Q samples, sample rate in S/s, and signal duration in seconds, including final-symbol padding.
        :rtype: tuple[numpy.ndarray, numpy.ndarray, float, float]

        :raises ValueError: If the input bytes or samples per symbol are invalid.
        """
        pass

    def modulate_time_domain(self, data, sps=_OFDM_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Return (real carrier signal, time in seconds, sample rate, duration).

        :param data: Input integer bytes, each in the range 0 to 255.
        :type data: iterable[int]

        :param sps: Positive integer samples per symbol.
        :type sps: int

        :returns: Real carrier signal, time base in seconds, sample rate in S/s, and signal duration in seconds, including padding.
        :rtype: tuple[numpy.ndarray, numpy.ndarray, float, float]

        :raises ValueError: If the input bytes or samples per symbol are invalid.
        """
        pass

    def demodulate(self, iq_samples, fs):
        """
        Return (bits, NRZ bits) from complete, aligned baseband symbols.

        :param iq_samples: Finite one-dimensional baseband IQ samples containing complete, symbol-aligned intervals.
        :type iq_samples: numpy.ndarray or list[complex]

        :param fs: Finite positive sample rate in S/s, an integer multiple of the symbol rate.
        :type fs: int or float

        :returns: Demodulated bits and their NRZ representation, including final-symbol padding bits.
        :rtype: tuple[list[int], list[int]]

        :raises ValueError: If the sample rate or IQ samples are invalid.
        """
        pass
