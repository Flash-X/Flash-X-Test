## Testing framework

- Install pip package for testing `pip3 install FlashXTest`
- Create a 'Config' file using `FlashXTest init -z <pathToFlash> -s <flashSite>`
- Test information is supplied in 'testInfo.xml'
- Create a single job file e.g. 'All' or separate job files like 'Grid', 'incompFlow'
- Run a job file with tests using `FlashXTest run All` or `FlashXTest run Grid incompFlow` etc.
