.. usage.rst

   Copyright The PyModulation Contributors.

   PyModulation Documentation

   This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
   International License. To view a copy of this license,
   visit http://creativecommons.org/licenses/by-sa/4.0/.

*****
Usage
*****

This section presents examples of how to use the library for each supported modulation type.

ASK
===

The ASK modulation can be used through the *ASK* class, using the modulate and demodulate methods. An example of usage can be seen in the code below:

.. code-block:: python

    from pymodulation import ASK

    mod = ASK(4, 9600)    # Order = 4, Baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits = mod.demodulate(samples, fs)

    print("Demodulated bits:", list(map(int, bits)))

The *modulate* method returns complex baseband IQ samples, the sampling rate in samples per second, and the signal duration in seconds. The constructor parameter *baud* denotes the bit rate. Each symbol carries ``log2(order)`` bits, and *L* specifies samples per symbol, giving ``fs = L * baud / log2(order)``. For order 8, zeros are added to complete the last symbol; the duration includes this padding.

The *demodulate* method takes symbol-aligned IQ samples and their sampling rate and returns only a list of bits, including final-symbol padding. Use the known payload length to trim the result, for example ``bits = bits[:len(data) * 8]``. The sampling rate must be a positive integer multiple of the symbol rate, and the input must contain complete symbols.

By default, demodulation averages the envelope over each symbol and uses the transmitter's normalized amplitude levels from 0 to 1. Calibrate receiver gain before decoding, or pass the known received amplitudes through *levels*, for example ``levels=[0, 2/3, 4/3, 2]`` for a 4-ASK signal with amplitude gain 2. Blind level estimation remains available with ``use_kmeans=True``, but requires all constellation levels to be present; it cannot reliably infer missing levels from a payload. The default is now ``use_kmeans=False``.

No additional low-pass filter is applied by default. An optional *lpf_cutoff* in Hz must be positive and below half the sampling rate. The symbol averaging itself provides rectangular matched filtering. The *modulate_time_domain* method returns a real carrier signal, time values in seconds, the sampling rate, and the duration; its carrier frequency is the symbol rate.

OOK
***

For OOK, the usage is very similar to ASK, but with the difference that there is no need to define the order of the modulation (as expected for OOK, it is fixed as 2):

.. code-block:: python

    from pymodulation import OOK

    mod = OOK(9600)    # Baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits = mod.demodulate(samples, fs)

    print("Demodulated bits:", list(map(int, bits)))

BPSK
====

The BPSK modulation can be used through the *BPSK* class, using the modulate and demodulate methods. An example of usage can be seen in the code below:

.. code-block:: python

    from pymodulation import BPSK

    mod = BPSK(9600)    # Baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits = mod.demodulate(samples, fs)

    print("Demodulated bits:", list(map(int, bits)))

The *modulate* method returns the IQ samples of the generated signal, the corresponding sampling rate, and the signal duration in seconds. The *demodulate* method allows the demodulation of a BPSK signal, taking the corresponding IQ samples as input, and producing as output the data bitstream contained in the signal and the baseband signal samples (in NRZ format).

GFSK
====

The GFSK modulation can be used through the *GFSK* class, using the modulate and demodulate methods. An example of usage can be seen in the code below:

.. code-block:: python

    from pymodulation import GFSK

    mod = GFSK(2.5, 0.5, 9600)  # Modulation index = 2.5, BT = 0.5, Baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits, bb_sig = mod.demodulate(samples, fs)

    print("Demodulated bits:", list(map(int, bits)))

The *modulate* method returns the IQ samples of the generated signal, the corresponding sampling rate, and the signal duration in seconds. The *demodulate* method allows the demodulation of a GFSK signal, taking the corresponding IQ samples and sampling rate as input, and producing as output the data bitstream contained in the signal and the baseband signal samples (in NRZ format).

GMSK
====

This modulation can be used in a manner almost identical to GFSK modulation, with the difference that in this case the modulation index is fixed at 0.5, as expected for this type of modulation. An example of usage can be seen in the code below.

.. code-block:: python

    from pymodulation import GMSK

    mod = GMSK(0.5, 9600)   # BT = 0.5, baudrate = 9600 bps

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits, bb_sig = mod.demodulate(samples, fs)

    print("Demodulated bits:", list(map(int, bits)))

QPSK
====

The QPSK modulation can be used through the *QPSK* class, using the modulate and demodulate methods. An example of usage can be seen in the code below:

.. code-block:: python

    from pymodulation import QPSK

    mod = QPSK(9600)    # Bit rate = 9600 bps; symbol rate = 4800 baud

    data = list(range(100))

    samples, fs, dur = mod.modulate(data)

    print("IQ Samples:", samples[:10])

    bits = mod.demodulate(samples, fs)

    print("Demodulated bits:", list(map(int, bits)))

The *modulate* method returns the IQ samples of the generated signal, the corresponding sampling rate, and the signal duration in seconds. The *demodulate* method takes the IQ samples and their sampling rate and returns a list of recovered bits (0 or 1).

The constructor parameter *baud* specifies the bit rate in bits per second. Each QPSK symbol carries two bits, so the symbol rate is *baud / 2*. The optional *L* argument to *modulate* specifies samples per symbol (default 100), giving a sample rate of ``L * baud / 2``. For byte input, the output contains ``len(data) * 4 * L`` samples. The *modulate_time_domain* method returns the baseband samples and their integer sample indices.

.. _oqpsk-usage:

OQPSK
=====

The OQPSK modulation can be used through the *OQPSK* class, which inherits from *QPSK*, using the modulate and demodulate methods. An example of usage can be seen in the code below:

.. code-block:: python

    from pymodulation import OQPSK

    mod = OQPSK(9600)    # Bit rate = 9600 bps; symbol rate = 4800 baud

    data = list(range(100))

    samples, fs, dur = mod.modulate(data, L=100)

    print("IQ Samples:", samples[:10])

    bits = mod.demodulate(samples, fs)

    print("Demodulated bits:", bits)
    expected_bits = [int(bit) for byte in data for bit in f"{byte:08b}"]
    assert bits == expected_bits

The *modulate* method returns complex64 baseband IQ samples, the sampling rate in samples per second, and the waveform duration in seconds. The constructor parameter *baud* specifies the bit rate, and each symbol carries two bits. The optional *L* argument specifies samples per symbol (default 100) and must be an even integer greater than or equal to two, giving a sampling rate of ``L * baud / 2``.

The Q component is delayed by ``L // 2`` samples relative to I. For nonempty byte input, the waveform contains ``len(data) * 4 * L + L // 2`` samples and its duration is ``(len(data) * 8 + 1) / baud`` seconds, including the final half-symbol needed to transmit Q completely. Empty input produces empty samples and zero duration. The *modulate_time_domain* method returns the baseband IQ samples and their integer sample indices.

The *demodulate* method compensates for the Q delay and returns a list of recovered bits (0 or 1). Input must be a one-dimensional waveform aligned to the beginning of I, containing complete symbols and the final Q half-symbol. The sample rate must correspond to an even integer number of samples per symbol greater than or equal to two. Invalid sample rates, incomplete waveforms, and invalid *L* values raise *ValueError*. Configure the transmitter and receiver with the same bit rate and use the transmitter's amplitude and phase reference.

LoRa
====

The *LoRa* class takes a positive bandwidth in Hz and a spreading factor from 7 to 12. The *modulate* method accepts integer bytes from 0 to 255 and an optional positive integer oversampling factor *L* (samples per chip, default 100). It returns complex baseband IQ samples, the sample rate in samples per second, and the transmission duration in seconds, including final-symbol padding.

.. code-block:: python

    from pymodulation import LoRa

    mod = LoRa(bw=125000, sf=7)
    data = [0x48, 0x65, 0x6C, 0x6C, 0x6F]  # "Hello"

    samples, fs, dur = mod.modulate(data, L=4)
    print("Sample rate:", fs)
    print("Duration:", dur)

    bits = mod.demodulate(samples, fs)
    # Use the known payload length to remove final-symbol padding.
    bits = bits[:len(data) * 8]
    recovered_data = [
        int("".join(map(str, bits[i:i + 8])), 2)
        for i in range(0, len(bits), 8)
    ]
    print("Demodulated data:", recovered_data)
    assert recovered_data == data

The *demodulate* method returns a list of bits, including any zeros used to pad the final SF-bit symbol. The payload length must be known separately to remove this padding. Samples must form a one-dimensional array of complete, aligned symbols, and *fs* must be a positive integer multiple of the configured bandwidth. The transmitter and receiver must use the same bandwidth and spreading factor.

Use *set_bandwidth* and *set_spreading_factor* to change the configuration; both update the derived timing and uncoded bit rate. The corresponding values are available through *get_bandwidth*, *get_spreading_factor*, and *get_baudrate*.

For LoRa, *get_baudrate* returns the uncoded bit rate in bits per second, calculated as ``sf * bw / 2**sf``. This value is derived from the configuration: calling *set_baudrate* raises *ValueError* without changing it. Adjust the bandwidth or spreading factor to change the bit rate.

.. _qam-usage:

QAM
===

Use ``QAM(order, baud)`` with a square constellation order (4, 16, 64, 256, ...) and a finite positive bit rate in bps. The optional ``sps`` argument specifies positive integer samples per symbol (default 100). Input values must be integer bytes from 0 to 255.

Modulation and demodulation
***************************

The following example transmits bytes using 16-QAM and recovers them without channel noise:

.. code-block:: python

    import numpy as np
    from pymodulation import QAM

    mod = QAM(order=16, baud=1200)
    data = [0x48, 0x65, 0x6C, 0x6C, 0x6F]  # "Hello"
    samples, fs, duration = mod.modulate(data, sps=20)

    bits, nrz = mod.demodulate(samples, fs)
    # The payload length is needed to remove final-symbol padding.
    payload_bits = bits[:len(data) * 8]
    recovered = np.packbits(np.array(payload_bits, dtype=np.uint8)).tolist()

    print("Sample rate:", fs)  # 6000 S/s
    print("Duration:", duration)
    print("Recovered bytes:", recovered)
    assert recovered == data

``modulate`` returns complex64 baseband IQ samples, the sample rate in S/s, and the duration in seconds. The sample rate is ``sps * baud / log2(order)``. Duration includes any zero padding needed to complete the last symbol; for example, one byte requires two 64-QAM symbols, carrying 12 bits in total.

``demodulate`` returns a tuple of two lists: recovered bits (0 or 1) and their NRZ representation (-1 for zero, +1 for one). Both include final-symbol padding. Samples must be a finite, one-dimensional sequence of complete, aligned symbols, and ``fs`` must be a positive integer multiple of the symbol rate. Configure both ends with the same order and bit rate and use the transmitter's amplitude and phase reference.

Separate I/Q components and real carrier
****************************************

.. code-block:: python

    import numpy as np
    from pymodulation import QAM

    mod = QAM(order=64, baud=9600)
    data = [0xA5, 0x5A]
    i, q, fs, duration = mod.get_iq(data, sps=20)
    signal, time, carrier_fs, carrier_duration = mod.modulate_time_domain(
        data, sps=20
    )

    assert len(i) == len(q) == len(signal) == len(time)
    assert (fs, duration) == (carrier_fs, carrier_duration)
    assert np.isrealobj(signal)
    print("Carrier signal samples:", signal[:10])

``get_iq`` returns I samples, Q samples, sample rate, and duration. ``modulate_time_domain`` returns the real carrier signal, time values in seconds, sample rate, and duration. Its carrier frequency equals the symbol rate; choose ``sps > 2`` to sample above the carrier's Nyquist rate. Pass complex baseband IQ samples to ``demodulate``; the real carrier signal requires downconversion first.

Use ``set_order`` and ``set_baudrate`` to change the configuration, and ``get_order`` and ``get_baudrate`` to inspect it.

.. _apsk-usage:

APSK
====

Use ``APSK(baud, order=16)`` with a finite positive bit rate in bps and an order of 16 or 32. The optional ``L`` argument specifies positive integer samples per symbol (default 100). Input values must be integer bytes from 0 to 255.

Modulation and demodulation
***************************

The following example transmits bytes using 16-APSK and recovers them without channel noise:

.. code-block:: python

    import numpy as np
    from pymodulation import APSK

    mod = APSK(baud=1200, order=16)
    data = [0x48, 0x65, 0x6C, 0x6C, 0x6F]  # "Hello"
    samples, fs, duration = mod.modulate(data, L=20)

    bits = mod.demodulate(samples, fs)
    payload_bits = bits[:len(data) * 8]
    recovered = np.packbits(np.array(payload_bits, dtype=np.uint8)).tolist()

    print("Sample rate:", fs)  # 6000 S/s
    print("Duration:", duration)
    print("Recovered bytes:", recovered)
    assert recovered == data

``modulate`` returns complex64 baseband IQ samples, the sample rate in S/s, and duration in seconds. The sample rate is ``L * baud / log2(order)``. Duration includes any final-symbol padding. ``demodulate`` returns a list of bits, including padding; use the original payload length to remove it before converting back to bytes.

For example, one byte requires two 32-APSK symbols, carrying ten bits in total:

.. code-block:: python

    from pymodulation import APSK

    mod = APSK(baud=1200, order=32)
    samples, fs, duration = mod.modulate([0xA5], L=20)
    bits = mod.demodulate(samples, fs)

    assert bits == [1, 0, 1, 0, 0, 1, 0, 1, 0, 0]
    assert len(samples) == 40
    assert fs == 4800
    assert abs(duration - 10 / 1200) < 1e-12

Samples must form a finite, one-dimensional sequence of complete, aligned symbols. The sample rate must be a positive integer multiple of the symbol rate. Configure both ends with the same order and bit rate, and use the transmitter's amplitude and phase reference. Invalid bytes, orders, bit rates, oversampling factors, sample rates or incomplete symbol intervals raise ``ValueError``.

Baseband waveform
*****************

``modulate_time_domain`` returns rectangular baseband IQ samples and integer sample indices starting at zero. Divide the indices by the sample rate to obtain time in seconds:

.. code-block:: python

    import numpy as np
    from pymodulation import APSK

    mod = APSK(baud=1200, order=16)
    data = [0xA5, 0x5A]
    waveform, indices = mod.modulate_time_domain(data, L=20)
    samples, fs, duration = mod.modulate(data, L=20)
    time = indices / fs

    np.testing.assert_allclose(waveform, samples)
    assert len(time) == len(samples)
    assert time[0] == 0

Use ``set_order`` and ``set_baudrate`` to change the configuration, and ``get_order`` and ``get_baudrate`` to inspect it. The full example in ``examples/example_apsk.py`` adds AWGN, recovers the bytes and plots the received samples alongside the ideal constellation points.
