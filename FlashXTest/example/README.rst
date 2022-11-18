Testing framework
=================

-  Install **FlashTest** package from Python directory
-  Create a **config** file using
   ``flashxtest init -z <pathToFlash> -s <flashSite>``
-  Test information is supplied in **testInfo.xml**
-  Add user tests to **testInfo.xml**
-  Create a job file. See **jobFile** for example
-  Run  with tests using
   ``flashxtest run <jobFile1> <jobFile2> <jobFile3>`` or
   ``flashxtest run`` to use default **jobFile**
