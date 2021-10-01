#!/usr/bin/python3

import pathlib
import logging

import h5py
import csv

class TSurfToHDF5():

    def __init__(self):
        self.h5_filename = None

    def main(self, **kwargs):
        """
        """
        args = argparse.Namespace(**kwargs) if kwargs else self._parse_command_line()
        log_level = logging.DEBUG if args.debug else logging.INFO
        logging.basicConfig(level=log_level, filename=args.log_filename)

        self.h5_filename = args.h5_filename
        
        self.load_metadata(args.metadata_filename)
        self.init_hdf5()
        self.process_tsurfs(args.tsurf_path)
        #self.process_traces(args.trpath)

    def init_hdf5(self):
        h5 = h5py.File(self.h5_filename, "w")
        h5.attrs["coordinate_reference_system"] = "EPSG:26711"
        h5.close()
        
    def load_metadata(self, filename):
        """Load metadata from CSV file.
        """
        SLIP_SENSE = {
            "rlss": "right-lateral strike-slip",
            "llss": "left-lateral strike-slip",
            "n": "normal",
            "r": "reverse/thrust",
            "orlr": "oblique right-lateral reverse",
            "ollr": "oblique left-lateral reverse",
            "orln": "oblique right-lateral normal",
            "olln": "oblique left-lateral normal",
            }
    
        metadata = {}
        with open(filename, "r", newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                obj = row["CFM5.3 Fault Object Name"]
                metadata[obj] = {
                    "fault_area": row["Fault Area/Major Fault System"],
                    "fault_zone": row["Fault Zone/Region"],
                    "fault_section": row["Fault Section"],
                    "fault_name": row["Fault Name"],
                    "source_author": row["Source/Author"],
                    "last_update": row["Last Update"],
                    "avg_strike": row["Avg Strike"],
                    "avg_dip": row["Avg Dip"],
                    "area_km2": row["Area [km^2]"],
                    "exposure": row["Exposure"],
                    "slip_sense": SLIP_SENSE[row["Slip Sense"]],
                    "id_comments": row["ID Comments"],
                    "usgs_id": row["USGS ID"],
                    "description": row["Fault Strand/Model Description"],
                    "references": row["References"],
                }
        self.metadata = metadata

    def process_tsurfs(self, tspath):
        tsfilenames = filepath.glob(tspath, "**/*.ts")
        h5 = h5py.File(self.h5_filename, "a")
        for tsfilename in tsfilenames:
            surface = self._read_tsurf(tsfilename)
            meta_key = tsfilename.name.replace(".ts", "")
            fault_metadata = self.metadata[meta_key]
            # :TODO: extract resolution from tsfilename
            
            h5_path = "{fault_area}/{fault_zone}/{fault_section}/{fault_name}/{resolution}"
            fault = h5.create_group(h5_path)

            h5.create_dataset("geometry", data=surface["geometry"], dtype="float32")
            topology = h5.create_dataset("topology", data=surface["topology"], dtype="int32")
            topology.attrs["shape"] = "tri"

            for attribute, value in fault_metadata.items():
                fault.attrs[attribute] = value
        h5.close()
                
    @staticmethod
    def _read_tsurf(self, filename):
        """Read tsurf file.
        """
        surface = None
        with open(filename, "r") as tsfile:
            pass
        return surface

    def _parse_command_line(self):
        """Parse command line arguments.
        """
        DESCRIPTION = (
            "Python script for converting the SCEC CFM from tsurf files to HDF5."
        )

        parser = argparse.ArgumentParser(description=DESCRIPTION)
        parser.add_argument("--metadata", action="store", dest="metadata_filename", required=True,
                                help="Name of CSV file with CFM metadata.")
        parser.add_argument("--output", action="store", dest="h5_filename", required=True,
                                help="Name of HDF5 file for output.")
        parser.add_argument("--tsurf-path", action="store", dest="tsurf_path", default=".",
                                help="Relative or absolute path to directory with tsurf files.")

        parser.add_argument("--log", action="store", dest="log_filename", default="tsurf_to_hdf5.log")
        parser.add_argument("--debug", action="store_true", dest="debug")
        args = parser.parse_args()
        if args.debug:
            logging.basicConfig(level=logging.DEBUG, filename=args.log_filename)
        else:
            logging.basicConfig(level=logging.INFO, filename=args.log_filename)
        return args
        
if __name__ == "__main__":
    TSurfToHDF5().main()
