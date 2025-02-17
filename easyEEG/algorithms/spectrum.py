import logging

import numpy as np

from ..default import *
from .. import structure
from .basic import *
from ..statistics import stats_methods
from ..group import timepoint_parser

import scipy.fftpack
from scipy import signal

comparison_params = dict(test=stats_methods.t_test, win='1ms', method='mean', sig_limit=0.05, need_fdr=False)


def Spectrum(self, compare=False, freq_span=(0, 30), target='power', comparison_params=comparison_params):
    # with the decorator, we can just focuse on case data instead of batch/collection data
    @self.iter('average')
    def to_spetrum(case_raw_data):
        def fft(name, data):
            N = data.shape[1]

            fft_result = scipy.fftpack.fft(data, axis=1)
            if target == 'power':
                fft_result = 2.0 / N * np.abs(fft_result)
            elif target == 'phase':
                fft_result = np.angle(fft_result)
            else:
                raise Exception('Please set the parameter "target" as "power", or "phase".')
            fft_result = fft_result[:, :N // 2]
            if freq_span[0] == 0:
                fft_result[:, 0] = 0

            index = pd.MultiIndex.from_tuples([name], names=['subject', 'condition_group', 'channel_group'])

            fft_result = pd.DataFrame(fft_result, index=index,
                                      columns=np.linspace(0, self.info['sample_rate'], N // 2))  # resolution: sr/N
            fft_result = fft_result.loc[:, freq_span[0]:freq_span[1]]

            fft_result.columns.name = 'frequency'
            return fft_result

        Spectrum_df = convert(case_raw_data, ['subject', 'condition_group', 'channel_group'], fft)
        return Spectrum_df

    spetrum_batch = to_spetrum()
    if compare:
        stats_data = stats_compare(spetrum_batch, comparison_params, levels='frequency', between='condition_group',
                                   in_group='subject')
    else:
        stats_data = None

    default_plot_params = dict(plot_type=['direct', 'spectrum'], y_title='power', err_style='ci_band',
                               color="Set1", style='darkgrid', compare=compare, win=comparison_params['win'],
                               sig_limit=0.05)
    return structure.AnalyzedData('Spectrum', spetrum_batch, stats_data, default_plot_params=default_plot_params)


# grand average
def Time_frequency(self, compare=False, freq_span=(0, 30), mother_wavelet='morlet', w=6, steps=20, log=False, square=False, selected_batch=None, epochs_data=None):
    if freq_span[0] == 0:
        freq_span[0] = freq_span[0] + 0.001

    # whether frequencies should be distributed logarithmically or linear
    if log & (steps != 0):
        # print(f"IN LOG log: {log}, steps:{steps}")
        frequency = np.geomspace(freq_span[0], freq_span[1], steps)
    else:
        # print(f"IN LOG ELSE log: {log}, steps:{steps}")
        frequency = np.arange(freq_span[0], freq_span[1])

    if mother_wavelet == 'morlet':
        sampling_rate = 256
        # widths
        widths = w * sampling_rate / (2 * frequency * np.pi)

    else:
        # widths
        widths = frequency

    # with the decorator, we can just focuse on case data instead of batch/collection data
    @self.iter('average')
    def to_tf(case_raw_data):
        def cwt(name, data):
            if mother_wavelet == 'morlet':
                if square:
                    cwt_result = np.abs(signal.cwt(
                        data=np.array(data)[0], wavelet=signal.morlet2, widths=widths, w=w))**2
                else:
                    cwt_result = np.abs(signal.cwt(
                        data=np.array(data)[0], wavelet=signal.morlet2, widths=widths, w=w))
            else:
                cwt_result = signal.cwt(
                    data=np.array(data)[0], wavelet=signal.ricker, widths=widths)

            cwt_result = pd.DataFrame(cwt_result, columns=data.columns)

            if selected_batch is not None:
                timepoints_list = timepoint_parser(selected_batch, epochs_data)
                cwt_result = cwt_result.loc[:, (slice(None), timepoints_list)]

            cwt_result.index = pd.MultiIndex.from_tuples(
                [(name[0], name[1], i) for i in frequency[0::]], names=('condition_group', 'channel_group', 'freq'))
            return cwt_result

        tf_df = convert(case_raw_data, ['condition_group', 'channel_group'], cwt)

        for level in ['condition_group', 'channel_group']:
            if len(tf_df.index.get_level_values(level).unique()) == 2:
                tf_df = [i for ind, i in tf_df.groupby(level=level)]
                tf_df[0].index = tf_df[0].index.droplevel(level)
                tf_df[1].index = tf_df[1].index.droplevel(level)
                tf_df = tf_df[0] - tf_df[1]

        tf_df.index = tf_df.index.get_level_values('freq')

        return tf_df

    @self.iter('average')
    def to_tf_group_level(case_raw_data):
        def cwt(name, data):
            if mother_wavelet == 'morlet':
                if square:
                    cwt_result = np.abs(signal.cwt(
                        data=np.array(data)[0], wavelet=signal.morlet2, widths=widths, w=w)) ** 2
                else:
                    cwt_result = np.abs(signal.cwt(
                        data=np.array(data)[0], wavelet=signal.morlet2, widths=widths, w=w))
            else:
                cwt_result = signal.cwt(
                    data=np.array(data)[0], wavelet=signal.ricker, widths=widths)
            cwt_result = pd.DataFrame(cwt_result, columns=data.columns)

            if selected_batch is not None:
                timepoints_list = timepoint_parser(selected_batch, epochs_data)
                cwt_result = cwt_result.loc[:, (slice(None), timepoints_list)]

            cwt_result.index = pd.MultiIndex.from_tuples(
                [(name[0], name[1], name[2], i) for i in frequency[0::]],
                names=('condition_group', 'channel_group', 'subject', 'freq'))
            return cwt_result

        tf_df = convert(case_raw_data, ['condition_group', 'channel_group', 'subject'], cwt)

        return tf_df

    tf_batch = to_tf()

    if compare:
        tf_group_level_batch = to_tf_group_level()
        stats_data = stats_compare(tf_group_level_batch, comparison_params, levels=['time', 'freq'],
                                   between='condition_group', in_group='subject')
    else:
        stats_data = None

    default_plot_params = dict(plot_type=['direct', 'heatmap'], x_title='time', y_title='frequency', compare=compare,
                               sig_limit=0.05,
                               color="RdBu_r", style='white', grid=False, cbar_title='Power')
    return structure.AnalyzedData('Time Frequency', tf_batch, stats_data, default_plot_params=default_plot_params)
