import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import click

from astropy.io import fits
from calc_calib_constants import read_pixel, f

plt.style.use('ggplot')


@click.command()
@click.argument('datafile',
                type=click.Path(exists=True))
@click.argument('calibconstants_path',
                type=click.Path(exists=True))
@click.argument('chid',
                default=0)
@click.argument('cell',
                default=0)
def main(datafile: str, calibconstants_path: str, chid: int, cell: int):
    fits_file = fits.open(datafile)

    pixel_data = read_pixel(fits_file, chid).query('cell == @cell')
    calibconstants = pd.read_hdf(calibconstants_path)

    t = np.logspace(-4, -0.5, 10000)

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

    plt.axvline(2**14 * 1e-6)

    q = 'pixel == @chid & cell == @cell'
    params = calibconstants.query(q)[['a', 'b', 'c']].values[0]

    plt.plot(
        t,
        f(t, *params),
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
