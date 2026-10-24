#
# ask.py
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
from scipy.signal import firwin, filtfilt

from pymodulation.modulation import Modulation

_ASK_DEFAULT_OVERSAMPLING_FACTOR=100

class ASK(Modulation):
    """
    ASK modulator/demodulator.

    baud is the bit rate in bps. Symbols use log2(order) bits and normalized
    amplitudes from 0 to 1. The last symbol is zero-padded when necessary.
    """

    def __init__(self, order, baud):
        """
        ASK modulation constructor.

        :param order: ASK order.
        :type: int

        :param baud: The desired data rate in bps.
        :type: int

        :return None
        """
        super().__init__(baud)

        self._order = int()

        self.set_order(order)

    def _validate_sps(self, sps):
        """
        """
        if (isinstance(sps, (bool, np.bool_)) or not isinstance(sps, (int, np.integer)) or sps < 1):
            raise ValueError("Samples per symbol must be a positive integer")

    def _data_bits(self, data):
        """
        """
        data = list(data)
        if any(isinstance(byte, (bool, np.bool_)) or not isinstance(byte, (int, np.integer)) or not 0 <= byte <= 255 for byte in data):
            raise ValueError("Data must contain integer bytes from 0 to 255")

        return np.array(self._int_list_to_bit_list(data), dtype=np.uint8)

    def set_order(self, order):
        """
        Sets the order of the ASK modulation.

        :note: The possible order values are 2, 4 or 8.

        :param order: ASK order (2, 4 or 8).
        :type: int

        :return: None
        """
        if isinstance(order, (bool, np.bool_)) or not isinstance(order, (int, np.integer)) or order not in (2, 4, 8):
            raise ValueError("ASK order must be 2, 4 or 8!")

        self._order = order

    def get_order(self):
        """
        Gets the current order of the ASK modulation.

        :return: The order of the ASK modulation.
        :rtype: int
        """
        return self._order

    def modulate(self, data: list, L=_ASK_DEFAULT_OVERSAMPLING_FACTOR) -> tuple:
        """
        Modulate data into ASK IQ samples (baseband).

        :param data: List of integers with the data bytes.
        :type: list

        :param L: Positive integer samples per symbol.
        :type: int

        :return: Tuple of (IQ samples, sample rate in Hz, transmission duration in seconds)
        :rtype: tuple(np.ndarray, float, float)
        """
        self._validate_sps(L)
        amplitudes = self._bits_to_symbols(self._data_bits(data))
        iq = np.repeat(amplitudes, L).astype(np.complex64)
        fs = L * self.get_baudrate() / int(np.log2(self.get_order()))

        return iq, fs, len(iq) / fs

    def modulate_time_domain(self, data: list, sps: int = _ASK_DEFAULT_OVERSAMPLING_FACTOR, carrier_phase: float = 0.0) -> tuple:
        """
        Generates the ASK modulated signal in time domain.

        :param data: Input integer list to modulate (bytes as integers).
        :type data: list[int]

        :param sps: Samples per symbol.
        :type sps: int

        :param carrier_phase: Initial carrier phase φ₀ in radians.
        :type carrier_phase: float

        :return s_t: ASK modulated signal with carrier s(t) (time domain).
        :rtype s_t: np.ndarray

        :return t: Time base for RF carrier in seconds.
        :rtype t: np.ndarray

        :return samp: Sample rate in S/s.
        :rtype samp: int

        :return dur: Signal duration in seconds.
        :rtype dur: float
        """
        samples, fs, dur = self.modulate(data, sps)
        fc = self.get_baudrate() / int(np.log2(self.get_order()))
        t = np.arange(len(samples)) / fs
        s_t = samples.real.astype(np.float64) * np.cos(2 * np.pi * fc * t + carrier_phase)

        return s_t, t, int(fs) if fs.is_integer() else fs, dur

    def demodulate(self, samples: np.ndarray, fs, lpf_cutoff=None, use_kmeans=False, levels=None) -> list:
        """
        Demodulate complete, symbol-aligned baseband symbols into bits.

        The default detector averages the envelope over each symbol and uses
        the normalized transmitter levels. Input gain must be calibrated.
        Padding bits in the last symbol are retained.

        :param samples: One-dimensional finite IQ samples of complete symbols.
        :type samples: list[int]

        :param fs: Sample rate; a positive integer multiple of the symbol rate.
        :type fs: in

        :param lpf_cutoff: Optional low-pass cutoff in Hz, below fs / 2. None uses rectangular symbol integration without additional filtering.
        :type lpf_cutoff: int

        :param use_kmeans: Opt-in blind level estimation. Requires a payload containing all amplitude levels; cannot resolve missing levels.
        :type use_kmeans: bool

        :param levels: Optional calibrated, strictly increasing nonnegative amplitude levels, one per constellation point. Overrides k-means.
        :type levels: list[int]

        :return: List of bits, including final-symbol padding.
        :rtype:
        """
        bps = int(np.log2(self.get_order()))
        if (not isinstance(fs, (int, float, np.integer, np.floating)) or isinstance(fs, (bool, np.bool_)) or not np.isfinite(fs) or fs <= 0):
            raise ValueError("Sample rate must be a finite positive number")

        ratio = fs / (self.get_baudrate() / bps)
        sps = round(ratio)
        if sps < 1 or not np.isclose(ratio, sps, rtol=1e-9, atol=1e-9):
            raise ValueError("Sample rate must be an integer multiple of symbol rate")

        samples = np.asarray(samples)
        if samples.ndim != 1 or samples.size % sps or not np.all(np.isfinite(samples)):
            raise ValueError("Samples must be a finite one-dimensional array of complete symbols")

        if lpf_cutoff is not None:
            if (not np.isscalar(lpf_cutoff) or not np.isreal(lpf_cutoff) or not np.isfinite(lpf_cutoff) or not 0 < lpf_cutoff < fs / 2):
                raise ValueError("Filter cutoff must be positive and below fs / 2")

        if levels is not None:
            levels = np.asarray(levels, dtype=float)
            if (levels.shape != (self.get_order(),) or not np.all(np.isfinite(levels)) or np.any(levels < 0) or np.any(np.diff(levels) <= 0)):
                raise ValueError("Levels must be finite, nonnegative and strictly increasing")

        if not samples.size:
            return []

        envelope = np.abs(samples).astype(np.float32)
        if lpf_cutoff is not None:
            envelope = self._lowpass_filter(envelope, lpf_cutoff, fs)

        symbol_amps = envelope.reshape(-1, sps).mean(axis=1)

        if levels is None:
            levels = (self._estimate_levels(symbol_amps, self.get_order()) if use_kmeans else np.linspace(0, 1, self.get_order()))

        indices = self._decide_symbols(symbol_amps, levels)

        return self._symbols_to_bits(indices, bps).astype(int).tolist()

    def _lowpass_filter(self, signal: np.ndarray, cutoff: float, sample_rate: float, num_taps: int = 64) -> np.ndarray:
        """
        Zero-phase FIR low-pass filter using a Hann-windowed sinc kernel.

        :param signal: 1-D real array.
        :type: np.ndarray

        :param cutoff: cutoff frequency in Hz.
        :type: float

        :param sample_rate: Sample rate in S/sec.
        :type: float

        :param num_taps: Filter length (must be even; +1 added internally for symmetry).
        :type: int

        :return: Filtered signal (same length as input, no group-delay shift).
        :rtype: np.ndarray
        """
        nyq = sample_rate / 2.0
        # filtfilt needs signal length > padlen ≈ 3 * num_taps; clamp accordingly
        max_taps = max(3, (len(signal) // 3) - 1)
        num_taps = min(num_taps, max_taps)

        if num_taps % 2 == 0:
            num_taps -= 1        # firwin needs odd length for symmetric filter

        num_taps = max(num_taps, 3)
        taps = firwin(num_taps, cutoff / nyq, window="hann")

        return filtfilt(taps, [1.0], signal, padlen=min(3 * len(taps), len(signal) - 1)).astype(np.float32)

    def _estimate_levels(self, symbol_amps: np.ndarray, order: int, min_cluster_ratio: float = 0.5) -> np.ndarray:
        """
        Estimate ASK amplitude levels from received symbol amplitudes using
        k-means clustering (1-D, converges in a few iterations).

        If the data does not exercise all ``order`` amplitude levels (e.g. a
        short packet that never contains the lowest level), k-means will split
        real clusters incorrectly.  The function detects this via a minimum
        inter-centroid spacing check and falls back to uniformly-spaced levels
        anchored to the observed [min, max] range.

        :param symbol_amps: 1-D float array of sampled amplitudes.
        :type: np.ndarray

        :param order: Number of ASK levels (must be a power of 2).
        :type: int

        :param min_cluster_ratio: Centroids whose nearest-neighbour gap is smaller than ``min_cluster_ratio × expected_gap`` trigger the uniform fallback.
        :type: float

        :return: Sorted array of ``order`` estimated level centroids.
        :rtype:
        """
        lo, hi = float(symbol_amps.min()), float(symbol_amps.max())

        # Degenerate: all symbols identical
        if hi - lo < 1e-6:
            return np.linspace(0.0, 1.0, order, dtype=np.float32)

        # Initialise centroids uniformly between observed min and max
        centroids = np.linspace(lo, hi, order, dtype=np.float64)

        for _ in range(200):
            dists = np.abs(symbol_amps[:, None] - centroids[None, :])
            labels = np.argmin(dists, axis=1)
            new_centroids = np.array(
                [
                    symbol_amps[labels == k].mean() if np.any(labels == k) else centroids[k]
                    for k in range(order)
                ],
                dtype=np.float64,
            )
            if np.allclose(centroids, new_centroids, atol=1e-9):
                break
            centroids = new_centroids

        centroids = np.sort(centroids)

        # Sanity-check: if adjacent centroids are suspiciously close the payload
        # likely doesn't cover all levels → fall back to a uniform grid.
        if order > 1:
            gaps = np.diff(centroids)
            expected_gap = (hi - lo) / (order - 1)
            if np.any(gaps < min_cluster_ratio * expected_gap):
                centroids = np.linspace(lo, hi, order, dtype=np.float64)

        return centroids.astype(np.float32)

    def _find_symbol_offset(self, envelope: np.ndarray, sps: int) -> int:
        """
        Find the best sampling phase within one symbol period.

        Picks the offset that maximises the variance of sampled values —
        high variance means we're sampling near symbol centres rather than
        transitions.

        :param envelope: Real envelope signal.
        :type: np.ndarray

        :param sps: Samples per symbol.
        :type: int

        :return: Best integer offset in [0, sps-1].
        :rtype: int
        """
        best_offset, best_var = 0, -1.0
        for offset in range(sps):
            samples = envelope[offset::sps]
            v = float(np.var(samples))
            if v > best_var:
                best_var = v
                best_offset = offset

        return best_offset

    def _decide_symbols(self, symbol_amps: np.ndarray, levels: np.ndarray) -> np.ndarray:
        """
        Map each amplitude sample to the nearest level index.

        :param symbol_amps: 1-D float array.
        :type: np.ndarray

        :param levels: Sorted array of level centroids (length = ASK order).
        :type: np.ndarray

        :return: Integer array of symbol indices in [0, order-1].
        :rtype: np.ndarray
        """
        dists = np.abs(symbol_amps[:, None] - levels[None, :])

        return np.argmin(dists, axis=1).astype(np.uint8)

    def _bits_to_symbols(self, bits: np.ndarray) -> np.ndarray:
        """
        Pack `log2(order)` consecutive bits into one symbol amplitude.

        :param bits: flat uint8 bit array (MSB-first within each symbol)
        :type: np.ndarray

        :return: float32 array of per-symbol amplitudes, length = len(bits) / log2(order)
        :rtype: np.ndarray
        """
        bps = int(np.log2(self.get_order()))
        pad = (-len(bits)) % bps
        if pad:
            bits = np.append(bits, np.zeros(pad, dtype=np.uint8))

        weights = 1 << np.arange(bps - 1, -1, -1)   # Big-endian weights
        indices = bits.reshape(-1, bps) @ weights   # Integer indices

        return (indices / (self.get_order() - 1)).astype(np.float32)

    def _symbols_to_bits(self, indices: np.ndarray, bits_per_symbol: int, msb_first: bool = True) -> np.ndarray:
        """
        Convert symbol indices to a flat bit array.

        :param indices: Integer array of symbol indices.
        :type: np.ndarray

        :param bits_per_symbol: Bits per symbol.
        :type: int

        :param msb_first: Flag for bit order within each symbol.
        :type: bool

        :return: Flat uint8 bit array
        :rtype: np.ndarray
        """
        bits = np.zeros(len(indices) * bits_per_symbol, dtype=np.uint8)
        for i, idx in enumerate(indices):
            for b in range(bits_per_symbol):
                bit_pos = (bits_per_symbol - 1 - b) if msb_first else b
                bits[i * bits_per_symbol + b] = (int(idx) >> bit_pos) & 1

        return bits
