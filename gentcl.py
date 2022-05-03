#!/usr/bin/python3

# Jared Botte
# jbotte@purdue.edu

# January 27, 2022

# This Python script generates the appropriate .tcl file for the Altera DE2-115 development board.
# It uses the pin description file from ECE 437, and is based on the TCL section of the ECE 437
# 'synthesize' script (Credit: Eric Villasenor [evillase@gmail.com]

import os
import sys

# I am going to expect this script to get called from a makefile, so I am not going to provide much error checking
# in terms of checking command line arguments. 

args = sys.argv[1:]

try:
    basename = args[0]
    clkfreq = args[1]
    tcl_filename = basename + ".tcl"
    sdc_filename = basename + ".sdc"
    #outdir_name = "._" + basename
    #outdir = os.path.join(os.getcwd(), outdir_name) 
    outdir = os.getcwd()
    include_path = os.path.join(os.getcwd(), "include")
except IndexError:
    print("Missing arguments. Exiting script.")
    print("Usage: python3 gentcl.py basename clockfreq")
    sys.exit("\x1b[91mError: .tcl file not created\x1b[0m")

try:
    toolsdir = os.environ["TOOLSDIR"]
except KeyError:
    print("$TOOLSDIR not found. Please set it to the path of your tools directory!")
    sys.exit("\x1b[91mError: .tcl file not created\x1b0m")

if not os.path.exists(outdir):
    os.makedirs(outdir)
    print(f"Created new directory: {outdir}")

preamble =f"""package require ::quartus::project
if ([project_exists {basename}]) {{
  project_open -revision {basename} {basename}
}} else {{
  project_new -revision {basename} {basename}
}}
set_global_assignment -name PROJECT_OUTPUT_DIRECTORY {outdir}
set_global_assignment -name EDA_TIME_SCALE "1 ps" -section_id eda_simulation
set_global_assignment -name EDA_MAINTAIN_DESIGN_HIERARCHY ON -section_id eda_simulation
set_global_assignment -name PARTITION_FITTER_PRESERVATION_LEVEL PLACEMENT_AND_ROUTING -section_id Top
set_global_assignment -name PARTITION_NETLIST_TYPE SOURCE -section_id Top
set_global_assignment -name NUM_PARALLEL_PROCESSORS 4
set_global_assignment -name SMART_RECOMPILE ON
set_global_assignment -name FMAX_REQUIREMENT "{clkfreq} MHz"
set_global_assignment -name SDC_FILE {sdc_filename}
set_global_assignment -name TIMEQUEST_DO_REPORT_TIMING ON
set_global_assignment -name VERILOG_SHOW_LMF_MAPPING_MESSAGES OFF
set_global_assignment -name VERILOG_INPUT_VERSION SYSTEMVERILOG_2005
set_global_assignment -name ENABLE_DRC_SETTINGS ON
set_global_assignment -name SEARCH_PATH {include_path}

set_global_assignment -name EDA_GENERATE_FUNCTIONAL_NETLIST ON -section_id eda_simulation
set_global_assignment -name SYNTH_TIMING_DRIVEN_SYNTHESIS ON
set_global_assignment -name EDA_SIMULATION_TOOL "ModelSim (Verilog)"
set_global_assignment -name EDA_OUTPUT_DATA_FORMAT "Verilog" -section_id eda_simulation
"""

## The below section adds all existing .sv, .v, .vh, and .vhd files to the compilation rule so that they can be seen
## when it comes time to synthsize and map them. Currently, the 'source' and 'datapath' directories are searched.

with open(os.path.join(outdir, tcl_filename), 'w') as tcl_file:
    tcl_file.writelines(preamble)
    for source_file in os.listdir(os.path.join(os.getcwd(), "source")):
        filetype = ""
        ext = os.path.splitext(source_file)[1]
        if(ext == ".sv"):
            filetype = "SYSTEMVERILOG_FILE"
        elif (ext == ".v" or ext == ".vh"):
            filetype = "VERILOG_FILE"
        elif (ext == ".vhd"):
            filetype = "VHDL_FILE"

        if filetype != "":
            tcl_file.write(f"set_global_assignment -name {filetype} {os.path.join(os.getcwd(), 'source', source_file)}\n")

    try:
        dpath_files = os.listdir(os.path.join(os.getcwd(), "datapath"))
    except FileNotFoundError:
        dpath_files = []
        print("Did not find datapath directory.")

    for datapath_file in dpath_files:
        filetype = ""
        ext = os.path.splitext(datapath_file)[1]
        if(ext == ".sv"):
            filetype = "SYSTEMVERILOG_FILE"
        elif (ext == ".v" or ext == ".vh"):
            filetype = "VERILOG_FILE"
        elif (ext == ".vhd"):
            filetype = "VHDL_FILE"

        if filetype != "":
            tcl_file.write(f"set_global_assignment -name {filetype} {os.path.join(os.getcwd(), 'datapath', datapath_file)}\n")


    tcl_file.write("\n\n")
    with open(os.path.join(toolsdir, "EP4CE115")) as pins:
        tcl_file.write(pins.read())

    tcl_file.write("\nexport_assignments\n")
    tcl_file.write("\nproject_close\n")

print("\x1b[92mSuccess: .tcl file created\x1b[0m")
