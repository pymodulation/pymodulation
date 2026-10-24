#
# qam.py
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

_QAM_DEFAULT_OVERSAMPLING_FACTOR = 100

class QAM(Modulation):
    """
    Square QAM modulator/demodulator with Gray coding on each axis.

    ``order`` is a power of four (4, 16, 64, 256, ...).

    ``baud`` denotes the bit rate in bps; the symbol rate is baud / log2(order). Constellations have unit average energy over all points.
    Incomplete final symbols are padded with zero bits, which are retained by demodulation.
    """

    def __init__(self, order, baud):
        """
        Initialize the QAM modulation.

        :param order: Constellation size, a power of four at least 4.
        :type order: int

        :param baud: Finite positive bit rate in bps.
        :type baud: int or float

        :raises ValueError: If the order or bit rate is invalid.
        """
        super().__init__(baud)
        self.set_order(order)

    def set_order(self, order):
        """
        Set the constellation size to a power of four, at least four.

        :param order: QAM constellation size (4, 16, 64, 256, ...).
        :type order: int

        :returns: None.
        :rtype: None

        :raises ValueError: If the order is not a power of four at least 4.
        """
        if isinstance(order, (bool, np.bool_)) or not isinstance(order, (int, np.integer)):
            raise ValueError("QAM order must be a power of four, at least 4")

        order = int(order)

        if order < 4 or order & (order - 1) or (order.bit_length() - 1) % 2:
            raise ValueError("QAM order must be a power of four, at least 4")

        self._order = order

    def get_order(self):
        """
        Return the constellation size.

        :returns: Current QAM order.
        :rtype: int
        """
        return self._order

    def _axis_levels(self):
        """
        Return amplitudes indexed by their Gray-coded bit labels.

        :returns: Normalized amplitude levels for one constellation axis.
        :rtype: numpy.ndarray
        """
        side = 1 << ((self._order.bit_length() - 1) // 2)
        positions = np.arange(side)
        levels = np.empty(side, dtype=float)
        levels[positions ^ (positions >> 1)] = 2 * positions - (side - 1)

        return levels / np.sqrt(2 * (self._order - 1) / 3)

    def modulate(self, data, sps=_QAM_DEFAULT_OVERSAMPLING_FACTOR):
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
        if (isinstance(sps, (bool, np.bool_)) or not isinstance(sps, (int, np.integer)) or sps < 1):
            raise ValueError("Samples per symbol must be a positive integer")

        data = list(data)
        if any(isinstance(byte, (bool, np.bool_)) or not isinstance(byte, (int, np.integer)) or not 0 <= byte <= 255 for byte in data):
            raise ValueError("Data must contain integer bytes from 0 to 255")

        bits = np.array(self._int_list_to_bit_list(data), dtype=np.uint8)
        bps = self._order.bit_length() - 1
        bits = np.pad(bits, (0, (-len(bits)) % bps)).reshape(-1, bps)
        half = bps // 2
        weights = 1 << np.arange(half - 1, -1, -1)
        levels = self._axis_levels()
        symbols = levels[bits[:, :half] @ weights] + 1j * levels[bits[:, half:] @ weights]
        samples = np.repeat(symbols, sps).astype(np.complex64)
        fs = sps * self.get_baudrate() / bps

        return samples, fs, len(samples) / fs

    def get_iq(self, data, sps=_QAM_DEFAULT_OVERSAMPLING_FACTOR):
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
        samples, fs, dur = self.modulate(data, sps)

        return samples.real, samples.imag, fs, dur

    def modulate_time_domain(self, data, sps=_QAM_DEFAULT_OVERSAMPLING_FACTOR):
        """
        Return (real carrier signal, time in seconds, sample rate, duration).

        The carrier frequency equals the symbol rate. Choose sps > 2 to
        sample that carrier above its Nyquist rate.

        :param data: Input integer bytes, each in the range 0 to 255.
        :type data: iterable[int]

        :param sps: Positive integer samples per symbol.
        :type sps: int

        :returns: Real carrier signal, time base in seconds, sample rate in S/s, and signal duration in seconds, including padding.
        :rtype: tuple[numpy.ndarray, numpy.ndarray, float, float]

        :raises ValueError: If the input bytes or samples per symbol are invalid.
        """
        i, q, fs, dur = self.get_iq(data, sps)
        t = np.arange(len(i)) / fs
        fc = self.get_baudrate() / (self._order.bit_length() - 1)
        phase = 2 * np.pi * fc * t

        return i * np.cos(phase) - q * np.sin(phase), t, fs, dur

    def demodulate(self, iq_samples, fs):
        """
        Return (bits, NRZ bits) from complete, aligned baseband symbols.

        Average each symbol interval and select the nearest constellation
        point. Input must use the transmitter's amplitude and phase reference.
        NRZ bits use -1 for zero and +1 for one; padding bits are retained.

        :param iq_samples: Finite one-dimensional baseband IQ samples containing complete, symbol-aligned intervals.
        :type iq_samples: numpy.ndarray or list[complex]

        :param fs: Finite positive sample rate in S/s, an integer multiple of the symbol rate.
        :type fs: int or float

        :returns: Demodulated bits and their NRZ representation, including final-symbol padding bits.
        :rtype: tuple[list[int], list[int]]

        :raises ValueError: If the sample rate or IQ samples are invalid.
        """
        if (isinstance(fs, (bool, np.bool_)) or not isinstance(fs, (int, float, np.integer, np.floating)) or not np.isfinite(fs) or fs <= 0):
            raise ValueError("Sample rate must be a finite positive number")

        bps = self._order.bit_length() - 1
        ratio = fs / (self.get_baudrate() / bps)
        sps = round(ratio)
        if sps < 1 or not np.isclose(ratio, sps, rtol=1e-9, atol=1e-9):
            raise ValueError("Sample rate must be an integer multiple of symbol rate")

        samples = np.asarray(iq_samples)
        if samples.ndim != 1 or samples.size % sps or not np.all(np.isfinite(samples)):
            raise ValueError("Samples must be a finite one-dimensional array of complete symbols")

        if not samples.size:
            return [], []

        symbols = samples.reshape(-1, sps).mean(axis=1)
        levels = self._axis_levels()
        i = np.argmin(np.abs(symbols.real[:, None] - levels), axis=1)
        q = np.argmin(np.abs(symbols.imag[:, None] - levels), axis=1)
        labels = (i << (bps // 2)) | q
        bits = ((labels[:, None] >> np.arange(bps - 1, -1, -1)) & 1).ravel()

        return bits.tolist(), (2 * bits - 1).tolist()
