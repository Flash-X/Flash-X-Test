#!/usr/bin/env python3

import os
import click
# import xml.etree.ElementTree as ET

@click.group(name='FlashTest')
def FlashTest():
    """
    CLI command for Flash test
    """
    pass

@FlashTest.command(name="setsite")
@click.argument('site', required=True)
@click.argument('pathtoflashx', required=True)
def setsite(site, pathtoflashx):
    print("Configuring site directory: ", site, pathtoflashx)
    try:
        os.mkdir(site)
    except OSError as error:
        # print(error) # Don't throw error if site directory already exists
        pass   
    # .info files are not XML, nodes start with or contains numbers, loading as XML fails
    # Also, there are variables specified as <parfile> etc. these are not xml conforming
    # tree = ET.parse('temp.xml')
    # root = tree.getroot()
    # tree.write('output.xml')
    
    # reading info file as a regular file
    info_filename = site+"_test.info"
    site_infofile = str(site+"/"+info_filename)
    f2 =  open(site_infofile, 'w') 
    with open('all_tests.info') as f:
       lines = f.readlines()
       for line in lines:
          head="<"+site+">"
          foot="</"+site+">"
          line = line.replace("<site>", str(head))
          line = line.replace("</site>", str(foot))
        #   remove baselines
          if ("comparisonBenchmark" in line or "restartBenchmark" in line or "shortPath" in line):
            pass
          else:
              f2.write(line)

    f.close()
    f2.close()

    site_configfile = str(site+"/"+site+"_config")
    f2 =  open(site_configfile, 'w') 
    with open('config_template') as f:
       lines = f.readlines()
       for line in lines:
            # open config file and append pathtoflashx
            line = line.replace("pathToFlash:", str("pathToFlash:        "+pathtoflashx))
            line = line.replace("flashSite:", str("flashSite:          "+ site))
            f2.write(line)
    f.close()
    f2.close()
    
    site_testfile = str(site+"/"+site+"_tests.sh")
    f2 =  open(site_testfile, 'w') 
    with open('config_launch_tests.sh') as f:
        pwd = os.getcwd()
        flashTestSuite = pwd
        flashTest = str(pwd + "/python")
        flashBase = pathtoflashx

        lines = f.readlines()
        for line in lines:
                # open config file and append pathtoflashx
                line = line.replace("FLASH_BASE  ", str("export FLASH_BASE="+flashBase+"  #"))
                line = line.replace("FLASHTEST_BASE  ", str("export FLASHTEST_BASE="+flashTest+"  #"))
                line = line.replace("FLASHTEST_SITES ", str("export FLASHTEST_SITES="+flashTestSuite+"  #"))
                line = line.replace("export SITE =", str("export SITE="+site))
                line = line.replace("export INFOFILE = ", str("export INFOFILE="+info_filename))
  
                
                f2.write(line)
    f.close()
    f2.close()
    chmodcmd = "chmod +x " + site_testfile
    os.system(chmodcmd)
    
    print("\n\ncd into your site dir:", site, " and run only required tests by modifying: ", site_testfile)
    print("\n Make sure your path has required settings for running Flash")
if __name__ == "__main__":
    FlashTest()
