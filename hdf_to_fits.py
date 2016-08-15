from argparse import ArgumentParser
from astropy.table import Table
import pandas as pd

parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('outputfile')


if __name__ == '__main__':

    args = parser.parse_args()

    df = pd.read_hdf(args.inputfile)
    df.sort_values(['pixel', 'cell'], inplace=True)

    t = Table()
    for key in ['a', 'b', 'c']:
        t[key] = df[key].astype('float32').values

    t.write(args.outputfile)
