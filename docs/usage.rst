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

The *modulate* method returns the IQ samples of the generated signal, the corresponding sampling rate, and the signal duration in seconds. The *demodulate* method allows the demodulation of a ASK signal, taking the corresponding IQ samples as input, and producing as output the data bitstream contained in the signal and the baseband signal samples (in NRZ format).

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

    bits, bb_sig = mod.demodulate(fs, samples)

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

    bits, bb_sig = mod.demodulate(fs, samples)

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