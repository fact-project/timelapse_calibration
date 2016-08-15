from argparse import ArgumentParser
from astropy.io import fits
from calc_calib_constants import read_pixel, f
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


plt.style.use('ggplot')

parser = ArgumentParser()
parser.add_argument('datafile')
parser.add_argument('-p', '--pixel', dest='pixel', type=int, default=0)
parser.add_argument('-c', '--cell', dest='cell', type=int, default=0)


if __name__ == '__main__':

    args = parser.parse_args()
    fits_file = fits.open(args.datafile)

    pixel_data = read_pixel(fits_file, args.pixel).query('cell == @args.cell')

    plt.title('Pixel {}, Cell {}'.format(args.pixel, args.cell))

    mask1 = pixel_data['sample'] > 9
    mask2 = pixel_data['sample'] <= 240

    plt.scatter(
        'delta_t', 'adc_counts',
        lw=0, s=5,
        data=pixel_data[mask1 & mask2],
        label='10 ≤ sample ≤ 240',
        color='b',
    )
    plt.scatter(
        'delta_t', 'adc_counts',
        lw=0, s=5,
        data=pixel_data[~mask1],
        label='sample < 10',
        color='gray',
    )
    plt.scatter(
        'delta_t', 'adc_counts',
        lw=0, s=5,
        data=pixel_data[~mask2],
        label='sample > 240',
        color='black',
    )


    low = pixel_data.adc_counts.min() # quantile(0.01)
    high = pixel_data.adc_counts.max() # quantile(0.99)

    r = high - low

    plt.ylim(
        low - 0.05 * r,
        high + 0.05 * r,
    )

    plt.xscale('log')
    plt.xlim(1e-4, 1e0)
    plt.xlabel('$\Delta t \,/\, \mathrm{s}$')
    plt.ylabel('adc counts')
    plt.legend()

    plt.show()
