from scipy.io import wavfile
import numpy as np
import ltsd


def compute_power_frame_from_spectrum(spectrum):
    power_frame = (spectrum**2).mean()
    return power_frame


def mount_treated_signal(it_is_speech_ho, signal, window_size):
    new_signal = []
    kk = []
    for i in np.arange(len(it_is_speech_ho)):
        kk.append(signal[i*window_size:(i+1)*window_size])
        if it_is_speech_ho[i]:
            new_signal.append(signal[i*window_size:(i+1)*window_size])
        else:
            new_signal.append(np.repeat(8, window_size))

    return new_signal


if __name__ == '__main__':
    n_order = 5
    fs, signal = wavfile.read("data/ex-1.wav")
    window_size = 256

    noise_spectrum_avg, noise_power_by_frame = ltsd.estimate_noise_params("data/noise-audio.wav", window_size)
    power_noise_avg = noise_power_by_frame.mean()
    power_noise_min = noise_power_by_frame.min()
    power_noise_max = noise_power_by_frame.max()

    signal_spectrum_by_frame = ltsd.compute_ffts_by_signal(signal, window_size)
    ltses = ltsd.compute_LTSEs(signal_spectrum_by_frame, n_order)
    ltsds = ltsd.compute_LTSDs(signal_spectrum_by_frame, noise_spectrum_avg)

    signal_power_by_frame = [compute_power_frame_from_spectrum(s) for s in signal_spectrum_by_frame]
    lambdas = np.array([ltsd.set_lambda(p, power_noise_min, power_noise_max) for p in signal_power_by_frame])

    it_is_speech = []
    for i in np.arange(len(ltsds)):
        it_is_speech.append(ltsd.classify_frame(ltsds[i], lambdas[i]))

    it_is_speech_ho = ltsd.hangover(it_is_speech, ltsds)

    new_signal = mount_treated_signal(it_is_speech_ho, signal, window_size)
    wavfile.write("out.wav", fs, np.concatenate(new_signal))
