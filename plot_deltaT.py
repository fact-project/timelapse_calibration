from astropy.io import fits
from calc_calib_constants import read_pixel, f
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import click

plt.style.use('ggplot')


@click.command()
@click.argument('datafile',
                type=click.Path(exists=True))
@click.argument('chid',
                default=0)
@click.argument('cell',
                default=0)
def main(datafile: str, chid: int, cell: int):

    fits_file = fits.open(datafile)
    pixel_data = read_pixel(fits_file, chid).query('cell == @cell')

    plt.title('Pixel {}, Cell {}'.format(chid, cell))

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

    low = pixel_data.adc_counts.min()  # quantile(0.01)
    high = pixel_data.adc_counts.max()  # quantile(0.99)

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


if __name__ == '__main__':
    main()
