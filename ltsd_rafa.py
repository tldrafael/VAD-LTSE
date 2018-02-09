	
import numpy as np
from scipy.io import wavfile

		
def compute_LTSE_for_frame(fft_order_list):

	fft_frames_stacked = np.vstack(fft_order_list)
	# get the maximum value by each bin
	ltse = fft_frames_stacked.max(axis=0)
	return ltse


def compute_LTSEs(ffts_by_frame, n_order):

	ltses = []
	for i in np.arange(len(ffts_by_frame)):
		if i <= n_order:
			current_ltse = np.zeros(ffts_by_frame[i].size)
			ltses.append(current_ltse)
			continue			
		
		fft_order_list = ffts_by_frame[(i-n_order):(i+n_order+1)]
		current_ltse = compute_LTSE_for_frame(fft_order_list)
		ltses.append(current_ltse)

	return ltses


# the window slides by the audio WITHTOUT OVERLAP
def compute_ffts_by_signal(signal, window_size):

	window = np.hanning(window_size)
	n_frames = len(signal)/window_size
	offsets = np.arange(n_frames)*window_size
	ffts_by_frame = []

	for i in np.arange(n_frames):
		frame_signal = signal[offsets[i]:(offsets[i]+window_size)]
		frame_signal_windowed = frame_signal*window

		current_fft = abs(np.fft.fft(frame_signal_windowed))
		current_fft = current_fft[:(window_size/2)]
		ffts_by_frame.append(current_fft)

	return ffts_by_frame



def estimate_noise_params(noise_filepath, window_size):

	noise_fs, noise_signal = wavfile.read(noise_filepath)
	noise_ffts_by_frame = compute_ffts_by_signal(noise_signal, window_size)
	noise_ffts_stacked = np.vstack(noise_ffts_by_frame)

	noise_spectrum_average = np.mean(noise_ffts_stacked, axis=0)

	noise_power_ffts = noise_ffts_stacked**2
	noise_power_average = noise_power_ffts.mean()

	return noise_spectrum_average, noise_power_average



def compute_LTSD_for_frame(ltse, noise_spectrum_average):
	
	if ltse.all() <= 0:
		return 0
	
	ltse_power = (ltse**2)/(noise_spectrum_average**2)
	ltsd = ltse_power.mean()
	ltsd = 10*np.log10(ltsd)

	return ltsd


def compute_LTSDs(ltses, noise_spectrum_average):
	import pdb; pdb.set_trace()
	ltsds = []
	
	for i in np.arange(len(ltses)):
		ltsd = compute_LTSD_for_frame(ltses[i], noise_spectrum_average)
		ltsds.append(ltsd)

	return ltsds


def set_lambda:
	


n_order = 5	
fs, signal = wavfile.read("data/ex-1.wav")
window_size = 256



ffts_by_frame = ltsd.compute_ffts_by_signal(signal, window_size)
ltses = ltsd.compute_LTSEs(ffts_by_frame, n_order)

noise_spectrum_average, noise_power_average = ltsd.estimate_noise_params("data/noise-audio.wav", window_size)

ltsds = ltsd.compute_LTSDs(ltses, noise_spectrum_average)



