#!/bin/bash

#-------------------------------------------------------------------------------
#
# FlashTest does not communicate success or failure using the error code.
# However, this is how Jenkins determines success or failure of each command
# executed in a Build step.
#
# This script
# 1) sets up a clean test environment,
# 2) runs all desired tests in a single FlashTest run regardless of the success
#    of previous tests,
# 3) checks the root errors file for errors, and
# 4) communicates success/failure via the error code.
#
# For FlashTest to work properly, users of this script must first configure
# gce with the correct compilers and libraries using the softenv
# configuration environment.
#
#-------------------------------------------------------------------------------
# Check environment variables
FLASH_BASE        - full path to root of FLASH directory tree
FLASHTEST_BASE    - full path to root of FlashTest repository
FLASHTEST_SITES   - full path to root of sites configuration repository
[ -z "$FLASH_BASE" ]      && { echo "Need to set FLASH_BASE";      exit 1; }
[ -z "$FLASHTEST_BASE" ]  && { echo "Need to set FLASHTEST_BASE";  exit 1; }
[ -z "$FLASHTEST_SITES" ] && { echo "Need to set FLASHTEST_SITES"; exit 1; }

export SITE =
export INFOFILE = 
export CONFIGFILE=${SITE}_config

export OMP_NUM_THREADS=1

FLASHTEST_OUTPUT=${FLASH_BASE}/TestResults

# Build brand-spanking-new version of sfocu
cd $FLASH_BASE/tools/sfocu
make SITE=$SITE NO_NCDF=True sfocu clean
make SITE=$SITE NO_NCDF=True sfocu


CONFIG_PATH=${FLASHTEST_SITES}/${SITE}/${CONFIGFILE} 
INFO_PATH=${FLASHTEST_SITES}/${SITE}/${INFOFILE} 

#launch
$FLASHTEST_BASE/flashTest.py \
                -z "$FLASH_BASE" \
                -o "${FLASHTEST_OUTPUT}" \
                -c "${CONFIG_PATH}" \
                -i "${INFO_PATH}" \
                -v \
                -t \
                -s $SITE \
                UnitTest/Grid/AMR/AMReX/2d/Init \
                UnitTest/Grid/AMR/AMReX/2d/Refine \
                UnitTest/Grid/AMR/AMReX/2d/FluxCorrection \
                UnitTest/Grid/AMR/AMReX/2d/FluxCorrection2 \
                UnitTest/Grid/AMR/AMReX/2d/TestCyl \
                UnitTest/GridAnomalousRefine/2d/Paramesh \
                UnitTest/GridAnomalousRefine/2d/AMReX \
                UnitTest/Eos/helmholtz/3d/pm4dev \
                UnitTest/Eos/helmholtz/3d/AMReX \
                UnitTest/Eos/starkiller/3d/pm4dev \
                UnitTest/Eos/weaklib/3d/pm4dev \
                UnitTest/PointMassGravity/3d/Paramesh \
                UnitTest/PointMassGravity/3d/AMReX \
                UnitTest/PointMassGravity/2dCyl/Paramesh \
                UnitTest/PointMassGravity/2dCyl/AMReX \
                UnitTest/Gravity/AMR/3d/Paramesh \
                UnitTest/Gravity/AMR/2dCyl/Paramesh \
                UnitTest/Multigrid/AMReX/3d \
                UnitTest/LidDrivenCavity/AMReX/2d \
                UnitTest/RisingBubble/AMReX/2d \
                UnitTest/IO/hdf5/3d/pm4dev \
                UnitTest/IO/hdf5/3d/Asyncpm4dev \
                UnitTest/GridAnomalousRefine/2d/pm4AltMortonBittree \
                Composite/Sod/PseudoUG/2d/Paramesh/simpleUnsplit \
                Composite/Sod/AMR/2d/Paramesh/simpleUnsplit \
                Composite/Sod/AMR/2d/pm4Bittree/simpleUnsplit \
                Composite/Sod/PseudoUG/2d/Paramesh/unsplit \
                Composite/Sod/AMR/2d/Paramesh/unsplit \
                Composite/Sod/AMR/2d/pm4AltMortonBittree/unsplit \
                Composite/Sod/AMR/2d/pm4AltMortonBittree/TBL/unsplit \
                Composite/Sod/PseudoUG/2d/Paramesh/sparkMT \
                Composite/Sod/PseudoUG/2d/AMReX/simpleUnsplit \
                Composite/Sod/AMR/2d/AMReX/simpleUnsplit \
                Composite/Sod/PseudoUG/2d/AMReX/unsplit \
                Composite/Sod/AMR/2d/AMReX/unsplit \
                Composite/Sod/PseudoUG/2d/AMReX/spark \
                Composite/Sod/PseudoUG/2d/AMReX/sparkMT \
                Composite/Sedov/PseudoUG/2d/Paramesh/simpleUnsplit \
                Composite/Sedov/AMR/2d/Paramesh/simpleUnsplit \
                Composite/Sedov/PseudoUG/2d/Paramesh/unsplit \
                Composite/Sedov/AMR/2d/Paramesh/unsplit \
                Composite/Sedov/PseudoUG/2d/AMReX/simpleUnsplit \
                Composite/Sedov/AMR/2d/AMReX/simpleUnsplit \
                Composite/Sedov/PseudoUG/2d/AMReX/unsplit \
                Composite/Sedov/AMR/2d/AMReX/unsplit \
                Composite/Sedov/PseudoUG/2d/AMReX/spark \
                Composite/Sedov/AMR/2d/AMReX/spark \
                Composite/Sedov/PseudoUG/3d/Paramesh/unsplit \
                Composite/Sedov/AMR/3d/Paramesh/unsplit \
                Composite/Sedov/AMR/3d/pm4Bittree/unsplit \
                Composite/Sedov/PseudoUG/3d/AMReX/unsplit \
                Composite/Sedov/AMR/3d/AMReX/unsplit \
                Composite/Sedov/PseudoUG/2dCyl/Paramesh/unsplit \
                Composite/Sedov/AMR/2dCyl/Paramesh/unsplit \
                Composite/Sedov/PseudoUG/2dCyl/AMReX/unsplit \
                Composite/Sedov/AMR/2dCyl/AMReX/unsplit \
                Composite/StreamingSineWave/PseudoUG/3d/Paramesh \
                Composite/SNIaDDT/AMR/2d/Paramesh \
                Composite/SNIaShellDet/AMR/2d/Paramesh \
                Composite/DustCollapse/PseudoUG/newMpole/3d/pm4dev \
                Composite/DustCollapse/AMR/newMpole/3d/AMReX \
                Composite/DustCollapse/AMR/newMpole/2dCyl/pm4AltMortonBittree \
                Composite/DustCollapse/AMR/newMpole/2dCyl/pm4AltMorton \
                Composite/DustCollapse/AMR/newMpole/1dSph/pm4dev \
                Composite/Cellular/AMR/2d/Paramesh/unsplit \
                Composite/Yahil/AMR/2dCyl/Paramesh/unsplit \
                Composite/Yahil/AMR/2dCyl/Paramesh/spark \
                Composite/Yahil/AMR/1dSph/Paramesh/unsplit \
                Composite/Yahil/AMR/1dSph/Paramesh/spark \
                Composite/HydroStatic/AMR/2d/Paramesh \
                Composite/IsentropicVortex/PseudoUG/2d/Paramesh/unsplit \
                Composite/IsentropicVortex/PseudoUG/2d/AMReX/unsplit \
                Composite/IsentropicVortex/PseudoUG/2d/AMReX/spark \
                Composite/DustCollapse/AMR/newMpole/3d/pm4dev \
                Composite/HydroStatic/AMR/2d/AMReX \
                Composite/HydroStatic/AMR/2d/pm4AltMortonBittree \
                Composite/Sedov/AMR/3d/AMReX/unsplitAsyncIO \
                Composite/Sedov/PseudoUG/2dCyl/Paramesh/spark \
                Composite/Sod/AMR/2d/AMReX/unsplitAsyncIO \
                Composite/Sod/PseudoUG/2d/AMReX/sparkPIO \
                Composite/Sedov/AMR/3d/AMReX/unsplitPIO \
                Composite/Sedov/AMR/3d/pm4Bittree/AsyncIOunsplit \
                Comparison/Sod/UG/2d/simpleUnsplit \
                Comparison/Sod/UG/2d/unsplit \
                Comparison/Sod/UG/2d/spark \
                Comparison/Sod/AMR/3d/cube16/pm4Nolwf/unsplit \
                Comparison/Sedov/UG/2d/unsplit \
                Comparison/Sedov/UG/2d/spark \
                Comparison/SNIaDDT/AMR/2d/spark \
                Comparison/DustCollapse/AMR/newMpole/2dCyl/AMReX \
                Comparison/DustCollapse/AMR/newMpole/1dSph/AMReX \
                Comparison/DustCollapse/AMR/newMpole/1dSph/spark \
                Comparison/Cellular/AMR/2d/Paramesh/unsplit \
                Comparison/IsentropicVortex/PseudoUG/2d/AMReX/unsplit \
                Comparison/IsentropicVortex/PseudoUG/2d/AMReX/spark \
                Comparison/StreamingSineWave/PseudoUG/3d/AMReX \
                Comparison/CCSN/AMR/1dSph/Paramesh/WeakLib \
                Comparison/Sod/AMR/3d/cube16/Paramesh/unsplit \
                Comparison/Sedov/Part/2d/Paramesh \
                Comparison/Yahil/AMR/1dSph/Paramesh/spark \
                Comparison/Yahil/AMR/2dCyl/Paramesh/spark 

EXITSTATUS=$?



