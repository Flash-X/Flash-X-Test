### Design Requirements

- The history of baselines shall be managed by a few privileged gatekeepers such that the risk of accidentally deleting or altering files is low and such that all files in the history are backed up regularly by experts.

- There is no need to share the baseline history with the general public. Limiting access to the baseline history shall be a priority if such constraints simplify interactions with the baselines, decrease frequency of interacting with the baselines, or decrease the risk of mistakes when interacting with the baselines.

- Baselines shall not be placed into the baseline history by automated means. The altering of test.info to add a test or to use new baselines shall not be automated. This is motivated by the belief that human-in-the-loop will add an extra layer of security toward ensuring that the baselines and tests are correct.

- The specification of tests in test.info and in the code that specifies what tests are to be run on a particular platform shall be protected by gatekeepers (that work in accord with standards set by the council?).

- The full baseline history shall be maintained so long as our storage solution permits. However, the desire to store a full history shall not be sufficient motivation to push us toward a bad, complex, or risky storage solution.  This is reasonable since pruning files will require more effort and increase risk.

- The public shall be allowed to directly and independently download the full results of the last successful test suite run on each testing platform so that they can use the contents to study our test suites and access the most current test results that we qualify as correct.

- The design of tests shall be documented by the designer in accord with some minimal level of necessary detail (as determined by whom?) so that the knowledge that they generated with respect to their code and test is captured and communicated. SHOULD THIS BE PUBLIC?

- The motivation and justification for changes to test designs shall be documented. If the changes address a bug or test defect, the impact of the bug/defect shall be documented.

- The motivation and justification for changes to baselines shall be documented.

- If test.info is known to be a security risk, then test.info shall not be made publicly available nor circulated to others without communicating that such risk exists.

- Users shall be able to establish baselines on their local machines and use Flash-X testing infrastructure to test the code on the local machines.  OTHERS KNOW BETTER THAN ME WHAT THIS AND RELATED REQUIREMENTS ARE.

- Priority shall be given to proven and mature solutions that have been used successfully in the past and to use these with hopefully limited alteration.

- Make existing testing framework less of a barrier for new users to implement for their own testing requirements, and avoid proliferation of “alternative” testing methodologies.

- Consolidating different utilities into one (i.e. FlashTest, FlashTestView)
