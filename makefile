# Jared Botte
# jbotte@purdue.edu
#
# January 28, 2022
#
# This makefile compiles and downloads a design to the board. It also makes sure it connects the pins...

SRCDIR = source
DPATHDIR = datapath  # Only used for FIR filter lab

CLKFREQ := 100

vpath %.sv $(SRCDIR)
vpath %.sv $(DPATHDIR)
vpath %.tcl $(wildcard ._*)
vpath %.sdc $(wildcard ._*)

%.tcl:
	@gentcl.py $* $(CLKFREQ)

%.sdc:
	@gensdc.py $* $(CLKFREQ)

%.sof: %.sv %.tcl %.sdc
	quartus_sh --64bit -t $(word 2,$^)
	quartus_map --64bit $* -c $*
	quartus_fit --64bit $* -c $*
	quartus_drc $* -c $*
	quartus_sta --64bit $* -c $*
	quartus_asm $* -c $*


.PRECIOUS: %.tcl %.sdc %.sof

%: %.sof
	quartus_pgm -m jtag -o "p;$<"

%_compile: %.sv %.tcl %.sdc
	quartus_sh --64bit -t $(word 2,$^)
	quartus_map --64bit $* -c $*

clean:
	@rm -rf *.qpf
	@rm -rf *.qsf
	@rm -rf *.tcl
	@rm -rf *.sdc
	@rm -rf *.rpt
	@rm -rf *.smsg
	@rm -rf *.summary
	@rm -rf *.jdi
	@rm -rf *.pin
	@rm -rf *.pof
	@rm -rf *.sld
	@rm -rf *.sof

veryclean: clean
	@rm -rf db
	@rm -rf incremental_db

help:
	@echo ""
	@echo "Using this makefile:"
	@echo " 	'make <module_name>' to build module and program it to the connected board"
	@echo " 	'make <module_name>.sdc' to build the .sdc file for the module"
	@echo " 	'make <module_name>.tcl' to build the .tcl file for the module"
	@echo " 	'make <module_name>.sof' to build module but don't program it"
	@echo "Clean rules:"
	@echo " 	'make clean' to remove all generated files"
	@echo " 	'make veryclean' to also remove all generated directories"
	@echo ""
