	
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

	return np.array(ltses)


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

	noise_spectrum_average = noise_ffts_stacked.mean(axis=0)
	noise_powerspectrum_ffts = noise_ffts_stacked**2
	noise_power_by_frame = noise_powerspectrum_ffts.mean(axis=1)

	return noise_spectrum_average, noise_power_by_frame



def compute_LTSD_for_frame(ltse, noise_spectrum_average):
	
	if ltse.all() <= 0:
		return 0
	
	ltse_power = (ltse**2)/(noise_spectrum_average**2)
	ltsd = ltse_power.mean()
	ltsd = 10*np.log10(ltsd)

	return ltsd


def compute_LTSDs(ltses, noise_spectrum_average):
	#import pdb; pdb.set_trace()
	ltsds = []
	
	for i in np.arange(len(ltses)):
		ltsd = compute_LTSD_for_frame(ltses[i], noise_spectrum_average)
		ltsds.append(ltsd)

	return np.array(ltsds)


def set_lambda(power_noise_frame, power_noise_min, power_noise_max, lambda_min=12, lambda_max=30):

	if power_noise_frame <= power_noise_min:
		return lambda_min

	if power_noise_frame >= power_noise_max:
		return lambda_max

	else:
		k = (power_noise_frame - power_noise_min)/(power_noise_min - power_noise_max)
		lamb = k*(lambda_min - lambda_max) + lambda_min
		return lamb


# def update_noise_spectrum(it_is_speech, noise_spectrum_avg, k, l, alpha):

# 	if it_is_speech==False:
# 		noise_spectrum_avg[k][l] = alpha*noise_spectrum_avg[k][l-1] + (1-alpha)*noise_spectrum_avg[k][l]		
# 	else:
# 		noise_spectrum_avg[k][l] = alpha*noise_spectrum_avg[k][l-1]
	
# 	return noise_spectrum_avg



# def update_power_noise_frame(it_is_speech, power_noise_frame, l, alpha=0.95):
	
# 	if it_is_speech==False:
# 		power_noise_frame[l] = alpha*power_noise_frame[l-1] + (1-alpha)*power_noise_frame[l]
# 	else:
# 		power_noise_frame[l] = power_noise_frame[l-1]

# 	return power_noise_frame


def classify_frame(ltsd, lamb):

	if ltsd >= lamb:
		return True
	else:
		return False



def hangover(it_is_speech, ltsds, n_hangover=8, ltsd_limit=30):
	
	it_is_speech_ho = []
	n_silences = 0
	for i in np.arange(len(ltsds)):

		# turnoff hangovere
		if ltsds[i] > ltsd_limit:
			it_is_speech_ho.append(it_is_speech[i])
			n_silences = 0
		
		else :
			if it_is_speech[i] == False:
				n_silences += 1
			else:
				n_silences = 0

			if n_silences >= n_hangover:
				it_is_speech_ho.append(False)
			else:
				it_is_speech_ho.append(True)

	return it_is_speech_ho