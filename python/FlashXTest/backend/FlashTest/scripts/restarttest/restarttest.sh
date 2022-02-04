#! /bin/bash

#########################################################################
#
# Script reqirements:
#   All of these in the same directory: a config file, a chk directory, 
#   and an obj directory
#
# The config file can be the same one used for flashTest on a particular
# machine, or if flashTest has not been set up, the config file needs to
# have the fields pathToFlash, pathToSimulations, and pathToSfocu.  You 
# may also specify flashMakefile or setupper (for which the only supported 
# option is NoClobberSetupper).
#
# A test.info file is also required, and the path to the file should be
# specified as the script's argument.  The test.info file requires, at
# minimum, the fields setupName, comparisonNumber, restartNumber,
# checkpointBasename, parfiles, restartParfiles, numProcs, and setupOptions.
# No field should have more than one entry (this is occasionally violated
# in the FLASH internal tests, and test.info files may have to be
# manually modified to work with this script. However, most FLASH internal
# test.info files work without issues).
#
# The following values may need to be changed depending on your environment
# i.e. mpiexec vs mpirun

MPIEXE="mpirun"
MAKE="gmake"
#
#########################################################################

TESTINFO=$1

rm chk/*
PWD=`pwd`
TOPDIR=$PWD

# *************************************************************************
# Parse the config and test.info files for necessary info

# Figure out the path to Flash and the simulations
PATHTOFLASH=`grep -m 1 pathToFlash: ./config | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
PATHTOSIM=`grep -m 1 pathToSimulations: ./config | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
SFOCU=`grep -m 1 pathToSfocu: ./config | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
PATHTOSIM=${PATHTOSIM/<pathToFlash>/$PATHTOFLASH}
SFOCU=${SFOCU/<pathToFlash>/$PATHTOFLASH}



# Figure out the names of the checkpoint files
SETUPNAME=`grep -m 1 setupName: $TESTINFO | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
COMPARNUM=`grep -m 1 comparisonNumber: $TESTINFO | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
RESTARTNUM=`grep -m 1 restartNumber: $TESTINFO | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
CHKBASE=`grep -m 1 checkpointBasename: $TESTINFO | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
COLDCHK=$CHKBASE$COMPARNUM
RECHK=$CHKBASE$RESTARTNUM

# Locate the parfiles

COLDPAR=`grep -m 1 parfiles: $TESTINFO | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
REPAR=`grep -m 1 restartParfiles: $TESTINFO | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
read -ra COLDPARS <<< "$COLDPAR"
read -ra REPARS <<< "$REPAR"
#echo "Number of coldstart parfiles: " ${#COLDPARS[@]}

NUMPROCS=`grep -m 1 numProcs $TESTINFO | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`

EXEC="$MPIEXE -np $NUMPROCS"

# Generate the setup command
SITE=`hostname -f`
SETUP=`grep -m 1 setupOptions: $TESTINFO | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
SETUP=${SETUP/<flashSite>/$SITE}
MAKEFILE=`grep -m 1 flashMakefile: ./config | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
if [ "$MAKEFILE" != "" ]; then
    MAKEFILE="-makefile=$MAKEFILE"
fi
SETUPPER=`grep -m 1 setupper: ./config | cut -d ":" -f 2 | sed -e "s/^ *//g;s/ *$//g"`
if [ "$SETUPPER" = "NoClobberSetupper" ]; then
    SETUPPER="-noclobber"
else
    SETUPPER=""
fi
SETUP="$PATHTOFLASH/setup $SETUPNAME $SETUP $SETUPPER $MAKEFILE -objdir=${TOPDIR}/obj/"
echo $SETUP

# ************************************************************************
# Run the test

# Run the setup script
$SETUP > chk/setup.log
SUCCESS1=`tail -n 1 chk/setup.log`
if [ $SUCCESS1 = SUCCESS ]; then
    echo "Setup successful"
else
    echo "Failure in setup... Aborting."
    echo "See chk/setup.log for more info"
    exit
fi

cd obj

# Compile
$MAKE > ${TOPDIR}/chk/build.log
SUCCESS1=`tail -n 1 ${TOPDIR}/chk/build.log`
SUCCESS1=${SUCCESS1:0:7}
if [ $SUCCESS1 = SUCCESS ]; then
    echo "Build successful"
else
    echo "Failure in build... Aborting."
    echo "See chk/build.log for more info"
    exit
fi

#run for each parfile
echo "Running tests ..."
for (( i=0; i < ${#COLDPARS[@]}; i++ ));
do
	COLDPAR=${COLDPARS[$i]}
	REPAR=${REPARS[$i]}

	COLDPAR=${COLDPAR/<pathToSimulations>/$PATHTOSIM}
	COLDPAR=${COLDPAR/<setupName>/$SETUPNAME}
	REPAR=${REPAR/<pathToSimulations>/$PATHTOSIM}
	REPAR=${REPAR/<setupName>/$SETUPNAME}

	echo "COLDPAR:" $COLDPAR
	echo "REPAR: "  $REPAR

	cp $COLDPAR ${TOPDIR}/chk/cold.par
	cp $REPAR ${TOPDIR}/chk/re.par
	COLDPAR="${TOPDIR}/chk/cold.par"
	REPAR="${TOPDIR}/chk/re.par"

	# ************************************************************************
	# Synthesize the third necessary parfile by replacing occurrences of nend
	# and tmax in the restart parfile into the synthesized coldstart parfile
	TMAX1=`grep -m 1 tmax $COLDPAR`
	NEND1=`grep -m 1 nend $COLDPAR`
	TMAX2=`grep -m 1 tmax $REPAR`
	NEND2=`grep -m 1 nend $REPAR`
	sed -e "s/$TMAX1/$TMAX2/g" -e "s/$NEND1/$NEND2/g" $COLDPAR > ${TOPDIR}/chk/coldstart_full.par
	COLDFULLPAR="${TOPDIR}/chk/coldstart_full.par"

	# Run the first coldstart and restart, copy the last checkpoint file
	echo "Running the first cold start test"
	$EXEC ${TOPDIR}/obj/flash4 -par_file $COLDPAR > ${TOPDIR}/chk/coldtest1.log
	cp ${TOPDIR}/obj/$COLDCHK ${TOPDIR}/chk/coldstart1.chk

	echo "Running the restart test"
	$EXEC ${TOPDIR}/obj/flash4 -par_file $REPAR > ${TOPDIR}/chk/restart.log
	cp ${TOPDIR}/obj/$RECHK ${TOPDIR}/chk/restart.chk

	# Run the second coldstart, copy the last checkpoint file
	echo "Running the full cold start test"
	$EXEC ${TOPDIR}/obj/flash4 -par_file $COLDFULLPAR > ${TOPDIR}/chk/coldtest2.log
	cp ${TOPDIR}/obj/$RECHK ${TOPDIR}/chk/coldstart2.chk


	# Check with sfocu
	$SFOCU ${TOPDIR}/chk/restart.chk ${TOPDIR}/chk/coldstart2.chk > ${TOPDIR}/chk/sfocu1.log
	SUCCESS1=`tail -n 1 ${TOPDIR}/chk/sfocu1.log`
	if [ $SUCCESS1 = SUCCESS ]; then
    		echo "Transparent restart returned SUCCESS"
	else
    		echo "Transparent restart returned FAILURE"
    		echo "See chk/sfocu1.log for more info"
    		exit
	fi
done
