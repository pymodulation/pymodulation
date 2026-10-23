.. modulations.rst

   Copyright The PyModulation Contributors.

   PyModulation Documentation

   This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
   International License. To view a copy of this license,
   visit http://creativecommons.org/licenses/by-sa/4.0/.

***********
Modulations
***********

ASK
===

Amplitude Shift Keying (ASK) is a digital modulation technique in which the amplitude of a carrier signal is varied according to the transmitted digital information while its frequency and phase remain constant. In its binary form (2-ASK), two different amplitude levels are used to represent the binary symbols 0 and 1.

The ASK signal can be expressed as:

.. math::

    s(t) = A_i \cos(2\pi f_c t)

where:

* :math:`A_i` is the carrier amplitude associated with the transmitted symbol;
* :math:`f_c` is the carrier frequency.

For binary ASK, :math:A_i assumes one of two possible values, corresponding to the transmitted bit. Since information is conveyed through the carrier amplitude, ASK receivers are more susceptible to amplitude distortions caused by channel noise, fading, and interference than phase- or frequency-based modulation schemes. Nevertheless, ASK offers a simple transmitter and receiver architecture, making it suitable for low-cost and low-power wireless communication systems.

Compared to modulation schemes such as BPSK and FSK, ASK generally provides lower noise immunity but requires relatively simple hardware implementation. Consequently, it is commonly employed in applications such as RFID systems, optical communications, short-range wireless devices, and low-data-rate telemetry links.

OOK
***

On-Off Keying (OOK) is the simplest form of binary ASK modulation. In OOK, one binary symbol is represented by transmitting the carrier at a fixed amplitude, while the other is represented by the absence of the carrier. Typically, a binary 1 is transmitted as a carrier with amplitude :math:`A`, whereas a binary 0 corresponds to zero amplitude.

The OOK signal can be expressed as:

.. math::

    s(t) =
    \begin{cases}
    A \cos(2\pi f_c t), & \text{for binary } 1, \\
    0, & \text{for binary } 0.
    \end{cases}

Because the transmitter is inactive during the transmission of one of the binary symbols, OOK provides improved power efficiency compared to conventional ASK. This characteristic makes it particularly attractive for battery-powered and energy-constrained devices. However, the absence of a carrier during part of the transmission increases the modulation's sensitivity to channel impairments and noise, requiring adequate receiver synchronization and detection techniques.

Due to its simplicity and low power consumption, OOK is widely used in low-cost wireless sensors, remote controls, passive RFID systems, optical communication links, and Internet of Things (IoT) devices.

BPSK
====

Binary Phase Shift Keying (BPSK) is one of the simplest and most robust digital modulation schemes used in wireless and satellite communications. In BPSK, digital information is transmitted by changing the phase of a carrier signal between two possible states separated by 180 degrees. Typically, a binary `0` is represented by a carrier phase of 0°, while a binary `1` is represented by a phase of 180°.

The BPSK signal can be expressed as:

.. math::

   s(t) = A \cos(2\pi f_c t + \phi)

where:

* :math:`A` is the signal amplitude;
* :math:`f_c` is the carrier frequency;
* :math:`\phi` is the carrier phase, taking values of 0 or :math:`\pi` radians according to the transmitted bit.

BPSK offers excellent noise immunity and achieves a low bit error rate (BER) for a given signal-to-noise ratio (SNR). Its simplicity allows for straightforward implementation in both transmitters and receivers. However, since each symbol conveys only one bit of information, BPSK has lower spectral efficiency than higher-order modulation schemes such as QPSK and QAM.

Due to its robustness and implementation simplicity, BPSK is widely employed in satellite telemetry and telecommand links, deep-space communications, navigation systems, and other applications requiring reliable data transmission under challenging channel conditions.

GFSK
====

Gaussian Frequency Shift Keying (GFSK) is a modulation technique derived from Frequency Shift Keying (FSK), where digital data is transmitted by shifting the carrier frequency between discrete values. Unlike traditional FSK, GFSK applies a Gaussian filter to the baseband pulses before modulation, which smooths the phase transitions and reduces spectral bandwidth. This filtering minimizes abrupt frequency changes, resulting in a more compact power spectrum and reduced interference with adjacent channels. GFSK is particularly advantageous in wireless communication systems where efficient bandwidth utilization and low power consumption are critical.  

One of the most notable applications of GFSK is in Bluetooth technology, where it is used for its robustness and spectral efficiency. The Gaussian filtering helps mitigate intersymbol interference (ISI) and improves performance in noisy environments. Additionally, GFSK supports both coherent and non-coherent detection, offering flexibility in receiver design. Its constant envelope property ensures efficient power amplifier operation, making it suitable for battery-powered devices. Overall, GFSK strikes a balance between simplicity, spectral efficiency, and reliability, making it a popular choice for short-range wireless communication systems.

GMSK
====

Gaussian Minimum Shift Keying (GMSK) is a continuous-phase modulation scheme derived from Frequency Shift Keying (FSK), where the digital signal is filtered using a Gaussian filter before modulation. This filtering smooths the phase transitions, resulting in a nearly constant envelope and significantly reduced spectral sidelobes compared to traditional FSK. The key feature of GMSK is its ability to achieve high spectral efficiency while maintaining low out-of-band emissions, making it ideal for bandwidth-constrained wireless systems.  

A notable application of GMSK is in the Global System for Mobile Communications (GSM), where it was chosen for its robustness against interference and efficient use of available spectrum. The modulation's constant envelope allows for the use of highly efficient nonlinear power amplifiers, reducing power consumption in mobile devices. Additionally, GMSK's resistance to multipath fading and phase noise enhances performance in challenging radio environments. Despite its slightly higher complexity in demodulation compared to simpler FSK schemes, GMSK remains a widely adopted modulation technique due to its excellent balance between spectral efficiency, power efficiency, and reliability in wireless communication systems.

QPSK
====

Quadrature Phase Shift Keying (QPSK) is a widely used digital modulation scheme that improves spectral efficiency by transmitting two bits of information per symbol. Unlike Binary Phase Shift Keying (BPSK), which uses two carrier phases, QPSK employs four equally spaced phase states separated by 90 degrees. Each phase represents a unique pair of bits, typically according to a Gray-coded mapping to minimize the bit error rate.

The QPSK signal can be expressed as:

.. math::

   s(t) = A \cos(2\pi f_c t + \phi)

where:

* :math:`A` is the signal amplitude;
* :math:`f_c` is the carrier frequency;
* :math:`\phi` is the carrier phase, taking one of four values: :math:`0`, :math:`\pi/2`, :math:`\pi`, or :math:`3\pi/2` radians, according to the transmitted symbol.

Since each QPSK symbol carries two bits, the symbol rate is half the bit rate for the same data throughput, resulting in twice the spectral efficiency of BPSK. When Gray coding is used, adjacent constellation points differ by only one bit, reducing the probability of multiple bit errors caused by incorrect symbol decisions. Under equivalent energy-per-bit conditions, QPSK achieves the same bit error rate (BER) performance as BPSK in an additive white Gaussian noise (AWGN) channel.

Due to its excellent balance between bandwidth efficiency, power efficiency, and implementation complexity, QPSK is extensively used in satellite communications, wireless local area networks (WLANs), cellular communication systems and digital broadcasting standards.

OQPSK
=====

Offset Quadrature Phase Shift Keying (OQPSK) is a variation of QPSK in which the quadrature (Q) component is delayed by half a symbol relative to the in-phase (I) component. Each symbol still carries two bits, but the two components change at different instants, avoiding simultaneous sign reversals and limiting phase changes to 90 degrees during the overlapping transmission interval.

The complex baseband signal can be expressed as:

.. math::

    x(t) = I(t) + jQ(t - T_s/2), \qquad
    T_s = \frac{2}{R_b}, \qquad
    f_s = L \frac{R_b}{2}

where:

* :math:`I(t)` and :math:`Q(t)` are the rectangular pulse trains generated from the QPSK constellation;
* :math:`T_s` is the symbol duration in seconds;
* :math:`R_b` is the bit rate in bits per second, configured through ``baud``;
* :math:`L` is the number of samples per symbol, which must be an even integer greater than or equal to two.

The *OQPSK* class inherits from *QPSK* and uses the same normalized Gray-coded constellation. Input bytes are serialized most significant bit first; the first bit of each pair selects Q and the second selects I. The Q component is delayed by ``L // 2`` samples. Each component is zero outside its transmission interval, and the final half-symbol is retained so that the last Q pulse is transmitted completely.

For a nonempty payload of :math:`N` symbols, the waveform contains :math:`NL + L/2` samples and lasts :math:`(2N + 1)/R_b` seconds. The receiver removes the Q offset before applying QPSK detection. It requires samples aligned to the beginning of I, including the final Q half-symbol, with the transmitter's amplitude and phase reference; synchronization and carrier recovery are not implemented. See :ref:`oqpsk-usage` for a usage example.

LoRa
====

LoRa uses Chirp Spread Spectrum (CSS) modulation, representing each symbol with a cyclically shifted chirp whose frequency sweeps across the configured bandwidth. The spreading factor (SF) determines the number of bits per uncoded symbol and the number of chips in each chirp.

The timing and uncoded bit rate used by the *LoRa* class are:

.. math::

    T_c = \frac{1}{BW}, \qquad
    T_{sym} = \frac{2^{SF}}{BW}, \qquad
    R_b = \frac{SF \cdot BW}{2^{SF}}

where:

* :math:`BW` is the bandwidth in Hz;
* :math:`SF` is the spreading factor, an integer from 7 to 12;
* :math:`T_c` is the chip period in seconds;
* :math:`T_{sym}` is the symbol duration in seconds;
* :math:`R_b` is the uncoded bit rate in bits per second, before accounting for final-symbol padding.

At a fixed bandwidth, increasing the spreading factor increases symbol duration and reduces the uncoded bit rate. The oversampling factor :math:`L` specifies samples per chip, giving a sample rate of :math:`f_s = L \cdot BW` and :math:`L \cdot 2^{SF}` samples per symbol.

PyModulation implements raw chirp modulation and FFT-based demodulation. Input bytes are unpacked most significant bit first into SF-bit symbols, with zeros added to complete the final symbol. The receiver dechirps each symbol and selects the strongest FFT bin to recover its bits.

This implementation does not include packet framing, whitening, interleaving, or forward error correction. It expects symbol-aligned samples without a frequency offset and does not implement synchronization or frequency-offset correction. It therefore provides a raw modulation building block rather than a complete LoRa or LoRaWAN packet transceiver.

QAM
===

Quadrature Amplitude Modulation (QAM) conveys information through the amplitudes of two orthogonal carrier components: in-phase (I) and quadrature (Q). Each pair of amplitudes defines a point in a complex constellation. PyModulation implements square QAM with an order :math:`M` that is a power of four, such as 4, 16, 64, or 256.

The complex baseband symbol and corresponding real carrier signal are:

.. math::

    x_k = I_k + jQ_k, \qquad
    s(t) = I_k \cos(2\pi f_c t) - Q_k \sin(2\pi f_c t)

Each symbol carries :math:`b = \log_2 M` bits. The constructor parameter ``baud`` denotes the bit rate :math:`R_b` in bits per second, giving:

.. math::

    R_s = \frac{R_b}{\log_2 M}, \qquad
    f_s = \mathrm{sps} \cdot R_s

For example, 16-QAM at 1200 bps transmits 300 symbols per second. With 20 samples per symbol, the sample rate is 6000 S/s.

Input bytes are serialized most significant bit first. The first half of each symbol's bits selects I and the second half selects Q. Each axis uses Gray coding, so adjacent constellation points differ by one bit. Axis levels are the odd integers from :math:`-(\sqrt{M}-1)` to :math:`\sqrt{M}-1`, divided by :math:`\sqrt{2(M-1)/3}`. This gives unit average symbol energy over the full constellation, although an individual payload's average power may differ.

The transmitter uses rectangular pulses and adds zero bits to complete the final symbol when necessary. The receiver averages each complete symbol interval and selects the nearest constellation point. It requires symbol-aligned baseband samples with the transmitter's amplitude and phase reference; timing recovery, carrier recovery, and channel equalization are not implemented.

Increasing the order carries more bits per symbol, but reduces the distance between normalized constellation points and makes detection more sensitive to noise. See :ref:`qam-usage` for executable examples.

APSK
====

Amplitude and Phase Shift Keying (APSK) encodes information using both the amplitude and phase of complex symbols arranged on concentric rings. PyModulation supports 16-APSK with 4 and 12 points on two rings, and 32-APSK with 4, 12 and 16 points on three rings.

For ring index :math:`r`, starting at one, and point index :math:`k`, starting at zero, the constellation is:

.. math::

    x_{r,k} = \frac{r}{\sqrt{E}}\exp\left(j\frac{2\pi k + \pi}{n_r}\right),
    \qquad E = \frac{1}{M}\sum_r n_r r^2

Here :math:`n_r` is the number of points on ring :math:`r`, and :math:`M` is the total constellation size. Relative radii are (1, 2) for 16-APSK and (1, 2, 3) for 32-APSK. Normalization gives unit average energy over all constellation points. This implementation uses a generic APSK constellation and binary labeling, rather than the DVB-S2 mapping.

Input bytes are serialized most significant bit first into groups of :math:`b = \log_2 M` bits. Natural binary labels select points counterclockwise on each ring, from the innermost ring outward. The transmitter repeats each symbol for :math:`L` samples and adds zero bits to complete the final symbol when necessary.

The constructor parameter ``baud`` denotes the bit rate :math:`R_b`, so the symbol rate, sample rate and waveform duration are:

.. math::

    R_s = \frac{R_b}{b}, \qquad f_s = L R_s, \qquad
    T = \frac{N b}{R_b}

Here :math:`N` is the number of symbols, including any final-symbol padding. For example, 16-APSK at 1200 bps transmits 300 symbols per second, giving 6000 S/s with 20 samples per symbol.

The receiver averages each complete symbol interval and selects the nearest constellation point by Euclidean distance. It retains padding bits and requires aligned baseband samples with the transmitter's amplitude and phase reference. Timing recovery, carrier recovery and channel equalization are not implemented. See :ref:`apsk-usage` for executable examples.
