Testing framework
=================

-  Install **FlashTest** package from Python directory
-  Create a **config** file using
   ``flashtest init -z <pathToFlash> -s <flashSite>``
-  Test information is supplied in **testInfo.xml**
-  Add user tests to **testInfo.xml**
-  Create a job file. See **jobFile** for example
-  Run  with tests using
   ``flashtest run <jobFile1> <jobFile2> <jobFile3>`` or
   ``flashtest run`` to use default **jobFile**
