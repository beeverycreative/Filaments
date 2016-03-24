#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import sys
import glob
import re
import argparse
import xml.etree.ElementTree as ET

"""bee2cura.py: This script attempts to generate ini files to be used in Cura
from the XML files that are located in the folder this script is located in. 
The resulting ini files will be deposited in the path requested by the user."""

__author__ = 'João Grego'
__email__ = "jgrego@beeverycreative.com"

COMPATIBLE_VERSION="2.0.0"

def fetch_files(path_to_files, version):
    """
    Obtain a list of XML files present in the current folder, check their
    version and, if the version is compatible, add them to a list.
    In the end, return that list.

    Args:
        path_to_files: the path where the search for XML files will be 
        performed
        version: string of the version of the XML filament files that are to
        be fetched

    Returns: 
        List of XML files (as an ElementTree structure, starting at the root) 
    """
    xml_temp_list = []
    for filename in glob.glob(path_to_files + "/*.xml"):
        tree = ET.parse(filename)
        root = tree.getroot()
        version = root.find('version').text

        if(version == COMPATIBLE_VERSION):
            xml_temp_list.append(root)

    return xml_temp_list


def generate_ini_from_xml(xml_file, output_path):
    """
    Receive a XML file (as an ElementTree structure) and output the resulting
    ini files to the given path.

    Args:
        xml_file: XML file, as an ElementTree structure
        output_path: path to the folder in which the ini files will be placed

    Returns:
        the number of ini files generated from the given XML
    """
    defaults = {}
    count = 0

    filament_name = xml_file.find('name').text.strip()
    #filament_name = xml_file.find('name').text.replace(' ', '_')
    #filament_name = filament_name.replace('-','_')
    #filament_name = re.sub('_+', '_', filament_name).strip()
    
    for param in xml_file.find('defaults').findall('parameter'):
        defaults[param.get('name')] = param.get('value')

    for printer in xml_file.findall('printer'):
        printer_name = printer.get('type')
        for nozzle in printer.findall('nozzle'):
            nozzle_size = nozzle.get('type')
            for res in nozzle.findall('resolution'):
                resolution = res.get('type')

                if resolution == "high+":
                    resolution = "highplus"

                output_filename = filament_name + "_" + printer_name + \
                                  "_" + resolution + "_" + "NZ" + \
                                  nozzle_size + ".ini" 
                count += 1

                overrides = {}
                for param in res.findall('parameter'):
                    overrides[param.get('name')] = param.get('value')
                merged_settings = defaults.copy()
                merged_settings.update(overrides)

                output_file = open(output_path + "/" + output_filename, 'w')
                output_file.write("[profile]")
                for param in merged_settings.items():
                    output_file.write('\n' + param[0] + "=" + param[1])
                output_file.close()

    return count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert all the BEESOFT XML "
            "files in a given path to cura compatible ini files.")
    parser.add_argument('xml_path', metavar='INPUT_PATH', type=str, help='path'
            ' where the XML files are located')
    parser.add_argument('ini_path', metavar="OUTPUT_PATH", type=str, help=
            'path where the ini files are to be placed')

    args = parser.parse_args()

    if os.path.isfile(args.xml_path):
        print("ERROR: The given input path is a file. Please specify a path to"
                " a folder.")
        sys.exit(1)

    try:
        os.mkdir(args.ini_path)
    except OSError as ex:
        if ex.errno == 17 and os.path.isfile(args.ini_path):
            print("ERROR: The given output path is a file. Please specify a "
                    "path to a folder.")
            sys.exit(1)
    
    xml_files = fetch_files(args.xml_path, COMPATIBLE_VERSION)

    total_count = 0
    for f in xml_files:
        total_count += generate_ini_from_xml(f, args.ini_path)

    print(str(total_count) + " ini files have been generated")
    sys.exit(0)
