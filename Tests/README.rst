Testing framework
=================

-  Install pip package for testing ``pip3 install FlashXTest``
-  Create a ‘Config’ file using
   ``FlashXTest init -z <pathToFlash> -s <flashSite>``
-  Test information is supplied in ‘TestsMain.xml’
-  Add user tests to ‘TestsUser.xml’
-  Create a job file like ‘Grid’, ‘incompFlow’, etc.
-  Run a job file with tests using
   ``FlashXTest run Grid incompFlow ...`` etc.
