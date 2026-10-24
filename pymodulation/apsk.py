#
# apsk.py
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

_APSK_DEFAULT_OVERSAMPLING_FACTOR = 100

class APSK(Modulation):
    """
    16-APSK (4+12) or 32-APSK (4+12+16) baseband modulation.

    Baud denotes the bit rate. Symbols use natural binary labels, assigned
    counterclockwise on each ring, from the innermost ring outward.
    Each ring starts at pi / population radians. Relative radii are (1, 2)
    or (1, 2, 3), normalized to unit mean constellation energy.
    This is a generic APSK mapping, not a DVB-S2 bit mapping.
    Final symbols are zero-padded; demodulation retains the padding bits.
    """

    def __init__(self, baud, order=16):
        """
        Initialize the APSK modulation.

        :param baud: Finite positive bit rate in bits per second.
        :type baud: int or float

        :param order: Constellation size, either 16 or 32. Defaults to 16.
        :type order: int

        :raises ValueError: If the bit rate or constellation size is invalid.
        """
        super().__init__(baud)
        self.set_order(order)

    def set_order(self, order):
        """
        Set the APSK constellation size to 16 or 32.

        :param order: New constellation size, either 16 or 32.
        :type order: int

        :return: None.
        :rtype: None

        :raises ValueError: If the constellation size is invalid.
        """
        if (isinstance(order, (bool, np.bool_)) or not isinstance(order, (int, np.integer)) or order not in (16, 32)):
            raise ValueError("APSK order must be 16 or 32")

        self._order = int(order)

    def get_order(self):
        """
        Return the constellation size.

        :return: Current APSK order.
        :rtype: int
        """
        return self._order

    def _constellation(self):
        """
        Return constellation points indexed by binary labels.

        :return: Complex points normalized to unit mean constellation energy.
        :rtype: numpy.ndarray
        """
        populations = (4, 12) if self._order == 16 else (4, 12, 16)
        points = np.concatenate([radius * np.exp(1j * (2 * np.pi * np.arange(count) + np.pi) / count) for radius, count in enumerate(populations, start=1)])

        return points / np.sqrt(np.mean(np.abs(points) ** 2))

    def modulate(self, data: list, L=_APSK_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Return complex64 IQ samples, sample rate in Hz and duration in seconds.

        Input bytes are serialized most significant bit first. L is a positive
        integer number of samples per symbol; fs = L * baud / log2(order).
        Duration includes any zero padding needed to complete the final symbol.

        :param data: Input integer bytes, each in the range 0 to 255.
        :type data: iterable[int]

        :param L: Positive integer samples per symbol. Defaults to 100.
        :type L: int

        :return: Complex64 IQ samples, sample rate in Hz and duration in seconds.
        :rtype: tuple[numpy.ndarray, float, float]

        :raises ValueError: If the input bytes or samples per symbol are invalid.
        """
        samples, _ = self.modulate_time_domain(data, L)
        fs = L * self.get_baudrate() / (self._order.bit_length() - 1)
        return samples.astype(np.complex64), fs, len(samples) / fs

    def modulate_time_domain(self, data, L=_APSK_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Return rectangular baseband IQ samples and discrete sample indices.

        Data contains integer bytes from 0 to 255. Each symbol is repeated L
        times. Empty input produces empty arrays.

        :param data: Input integer bytes, each in the range 0 to 255.
        :type data: iterable[int]

        :param L: Positive integer samples per symbol. Defaults to 100.
        :type L: int

        :return: Baseband IQ samples and sample indices starting at zero.
        :rtype: tuple[numpy.ndarray, numpy.ndarray]

        :raises ValueError: If the input bytes or samples per symbol are invalid.
        """
        if (isinstance(L, (bool, np.bool_)) or not isinstance(L, (int, np.integer)) or L < 1):
            raise ValueError("Samples per symbol must be a positive integer")

        data = list(data)
        if any(isinstance(byte, (bool, np.bool_)) or not isinstance(byte, (int, np.integer)) or not 0 <= byte <= 255 for byte in data):
            raise ValueError("Data must contain integer bytes from 0 to 255")

        bps = self._order.bit_length() - 1
        bits = np.array(self._int_list_to_bit_list(data), dtype=np.uint8)
        bits = np.pad(bits, (0, (-len(bits)) % bps)).reshape(-1, bps)
        labels = bits @ (1 << np.arange(bps - 1, -1, -1))
        samples = np.repeat(self._constellation()[labels], L)

        return samples, np.arange(len(samples))

    def demodulate(self, samples: np.ndarray, fs) -> list:
        """
        Recover bits from complete, aligned baseband symbol intervals.

        Average each interval and select its nearest constellation point.
        Samples must share the transmitter's amplitude and phase reference.
        Empty input returns an empty list. Final padding bits are retained.

        :param samples: Finite one-dimensional baseband IQ samples containing complete, aligned symbol intervals.
        :type samples: numpy.ndarray or list[complex]

        :param fs: Finite positive sample rate in samples per second, an integer multiple of the symbol rate.
        :type fs: int or float

        :return: Recovered bits, including final-symbol padding bits.
        :rtype: list[int]

        :raises ValueError: If the sample rate is invalid, samples are not finite and one-dimensional, or symbol intervals are incomplete.
        """
        if (isinstance(fs, (bool, np.bool_)) or not isinstance(fs, (int, float, np.integer, np.floating)) or not np.isfinite(fs) or fs <= 0):
            raise ValueError("Sample rate must be a finite positive number")

        bps = self._order.bit_length() - 1
        ratio = fs / (self.get_baudrate() / bps)
        if not np.isfinite(ratio):
            raise ValueError("Sample rate must give finite samples per symbol")

        L = round(ratio)
        if L < 1 or not np.isclose(ratio, L, rtol=1e-9, atol=1e-9):
            raise ValueError("Sample rate must be an integer multiple of symbol rate")

        samples = np.asarray(samples)
        if samples.ndim != 1 or samples.size % L or not np.all(np.isfinite(samples)):
            raise ValueError("Samples must be a finite one-dimensional array of complete symbols")

        if not samples.size:
            return []

        symbols = samples.reshape(-1, L).mean(axis=1)
        labels = np.argmin(np.abs(symbols[:, None] - self._constellation()), axis=1)

        return ((labels[:, None] >> np.arange(bps - 1, -1, -1)) & 1).ravel().tolist()
