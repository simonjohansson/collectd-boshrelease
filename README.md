# Sensu Client BOSH Release

## What it is

The aims of this release was to enable the following:

* Install the Sensu client in each instance of a Cloud Foundry PaaS deployment using BOSH.
* Provide a script to observe the monit jobs on the instance for failures.
* Have sensu schedule running the script regularly.
* Have the script surface good/bad information for each monit job up to sensu.
* Not use a list of hard-coded monit jobs, so new components will automatically get monitored.
* Output alerts via sensu for a failed/recovered monit job.


## What it isn't

* A completley general purpose Sensu client installation in BOSH with all configuration options surfaced.
* Polished. (it uses the sensu .DEB for example instead of compiling everything from scratch).


### Does it work?

Yes

### Repeatably?

Seems to ;)


## Getting Started
Incomplete

