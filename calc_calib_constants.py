import click
import pandas as pd
import numpy as np
import logging
import os
import sys
from astropy.io import fits
from scipy.optimize import curve_fit
from joblib import Parallel, delayed


logging.basicConfig(level=logging.INFO)


def read_pixel(fits_file, pixel):
    num_events = fits_file[1].data.shape[0]

    data = pd.DataFrame()
    for key in ('cellIDs', 'deltaT', 'Data'):
        data[key] = (
            fits_file[1].data[key][:, pixel * 300: (pixel + 1) * 300]
            .ravel()
            .byteswap()
            .newbyteorder()
        )

    data['sample'] = np.tile(np.arange(300), num_events)
    data.rename(
        columns={
            'cellIDs': 'cell',
            'Data': 'adc_counts',
            'deltaT': 'delta_t',
        },
        inplace=True,
    )
    data.dropna(inplace=True)

    return data


def f(x, a, b, c):
    return a * x ** b + c


def fit(df, cell, plot=False):
    big_time = df.delta_t.quantile(0.75)
    p0 = [
        0.3,
        -0.66,
        df.adc_counts[df.delta_t >= big_time].mean(),
    ]
    try:
        (a, b, c), cov = curve_fit(
            f,
            df['delta_t'],
            df['adc_counts'],
            p0=p0,
            maxfev=100000,
        )
    except RuntimeError:
        logging.error('Could not fit cell {}'.format(cell))
        return np.full(4, np.nan)

    ndf = len(df.index) - 3
    residuals = df['adc_counts'] - f(df['delta_t'], a, b, c)
    chisquare = np.sum(residuals**2) / ndf

    return a, b, c, chisquare


@click.command()
@click.argument('source_file_path',
                default="/net/big-tank/POOL/" +
                        "projects/fact/drs_temp_calib_data/" +
                        "calibration/calculation/drsFiles.txt",
                type=click.Path(exists=True))
@click.argument('store_file_path',
                default="/net/big-tank/POOL/" +
                        "projects/fact/drs_temp_calib_data/" +
                        "calibration/calculation/drsFiles.txt",
                type=click.Path(exists=False))
@click.argument('jobs',
                default=1)
@click.argument('verbosity',
                default=0)
def main(source_file_path: str, store_file_path: str, jobs: int, verbosity: int):

    """
    Fit raw data with powerlaw a*x**b+c and calculate chisquare for every fit.
    data is contained in a pandas data frame.

    Args:
        source_file_path (str):
            Full path to the sourceParameter file with the extension '.h5'
        store_file_path (str):
            Full path to the storeFile with the extension '.h5'
        jobs (int):
            The maximum number of concurrently running jobs,
            or the size of the thread-pool. -Nr of CPUs used
        verbosity (int):
            The verbosity level: if non zero, progress messages are printed.
            Above 50, the output is sent to stdout.
            The frequency of the messages increases with the verbosity level.
            If it more than 10, all iterations are reported.
    """

    pool = Parallel(n_jobs=jobs, verbose=verbosity)
    ids = np.arange(1024)

    if os.path.isfile(store_file_path):
        answer = input('store_file_path exists, overwrite? (y / [n]): ')
        if not answer.lower().startswith('y'):
            sys.exit()

    with pd.HDFStore(store_file_path, 'w') as store:
        f = fits.open(source_file_path)
        num_events = f[1].data.shape[0]
        print(num_events)
        for pixel in range(1440):
            logging.info('%s', pixel)

            data = read_pixel(f, pixel)
            upper_limit = 240 if pixel % 9 == 8 else 290
            data = data[(data['sample'] > 10) & (data['sample'] < upper_limit)]

            by_cell = data.groupby('cell')
            result = pd.DataFrame(
                pool(delayed(fit)(df, name) for name, df in by_cell),
                columns=['a', 'b', 'c', 'chisq_ndf']
            )
            result['pixel'] = pixel
            result['cell'] = ids

            store.append('data', result)


if __name__ == '__main__':
    main()
