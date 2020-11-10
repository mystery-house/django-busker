*********
Changelog
*********

0.7.2
* Add Python 3.9 to setup.cfg and .travis.yml

0.7.1
#####
* Refactor unit tests so they can be run without an existing django project (``python runtests.py``)
* Add config for Travis-CI

0.7.0
#####
* Nicely formatted error pages
* 100% test coverage (as assessed by coverage.py; see TODO comments in tests for possible improvements)

0.6.0
#####
* Includes batch message on code redemption confirmation page
* adds new code redeem / file download signals

0.5.2
#####
Add logging of code redemptions and file downloads to busker.views (When configuring in the settings.py LOGGING dict, the logger name is 'busker.views')

0.5.1
#####
First "official" release of the 'busker' download code management app for Django.
