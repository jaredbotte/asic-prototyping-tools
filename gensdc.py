#!/usr/bin/python3

# Jared Botte
# jbotte@purdue.edu

# January 27, 2022

# This Python script generates the appropriate .sdc file for the Altera DE2-115 development board.
# It uses the pin description file from ECE 437, and is based on the SDC section of the ECE 437
# 'synthesize' script (Credit: Eric Villasenor [evillase@gmail.com])

import os
import sys

# I am going to expect this script to only get called from a makefile, so I am not going to provide much error checking
# in terms of checking command line arguments. 

args = sys.argv[1:]

try:
    basename = args[0]
    clkfreq = args[1]
    sdc_filename = basename + ".sdc"
    #outdir_name = "._" + basename
    #outdir = os.path.join(os.getcwd(), outdir_name) 
    outdir = os.getcwd()
except IndexError:
    print("Missing arguments. Exiting script.")
    print("Usage: python3 gensdc.py basename clockfreq")
    sys.exit("\x1b[91mError: .sdc file not created\x1b[0m")

if not os.path.exists(outdir):
    os.makedirs(outdir)
    print(f"Created new directory: {outdir}")

with open(os.path.join(outdir, sdc_filename), 'w') as sdc_file:
    sdc_file.write(f"create_clock -name CLK [get_ports {{CLK}}] -period {clkfreq}MHz\n")
    sdc_file.write(f"create_clock -name CLK_50 [get_ports {{CLOCK_50}}] -period {clkfreq}MHz\n")
    sdc_file.write(f"create_generated_clock -divide_by 2 -source [get_ports CLK] -name CPUCLK [get_pins CPUCLK|q]\n")
    sdc_file.write(f"create_generated_clock -divide_by 2 -source [get_ports CLOCK_50] -name CPUCLK [get_pins system:SYS|CPUCLK|q]\n")

print("\x1b[92mSuccess: .sdc file created\x1b[0m")
