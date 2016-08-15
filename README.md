# timelapse_calibration
Python scripts to calculate DRS4 calibration constants like in cta-obersatory/dragonboard_testbench



## Data taking

To calculate timelapse calibration constants, we need Pedestal data
with different times between consecutive events.

Right now, we can do this with the arduino connected to the external 
trigger and a custom data run.

See https://github.com/fact-project/trigger_arduino for more details.



## Data extraction

Running
```
java -jar <jar> timelapse_data_extraction.xml -Dinfile=<infile> -Doutfile=<outfile>
```
will produce the needed inputfile to calculate the timelapse constants.

For now, you will need to `git checkout timelapse_calib` in fact-tools, 
as the necessary code is not yet in the master.


## Calculate the timelapse constants

Run:
```
python calc_calib_constants.py <inputfile> <outputfile>
```

This will perform 1440 * 1024 least squares fits. You might want to run that in parallel or on a cluster.

Processing on 24 Cores took something like half an hour for me.

## Convert to FACT-Tools readable output

run
```
python hdf_to_fits.py <input> <output>
```
To create a fits file with the calib constants, that fact-tools can use


