import pandas as pd
import click

from astropy.table import Table


@click.command()
@click.argument('source_file_path',
                type=click.Path(exists=True))
@click.argument('store_file_path',
                type=click.Path(exists=False))
def main(source_file_path: str, store_file_path: str):
    args = parser.parse_args()

    df = pd.read_hdf(args.inputfile)
    df.sort_values(['pixel', 'cell'], inplace=True)

    t = Table()
    for key in ['a', 'b', 'c']:
        t[key] = df[key].astype('float32').values

    t.write(args.outputfile)


if __name__ == '__main__':
    main()
