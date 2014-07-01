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

## Getting Started

### CF Manifest snippets

    releases:
     - name: cf
       version: xxx
     - name: sensu-client
       version: latest
    
    jobs:
     - name: nats
       templates:
        - name: sensu_client
          release: sensu-client
        - name: nats
          release: cf
        instances: 1
        resource_pool: infrastructure
        networks:
          (( merge ))
    
    properties:
      sensu:
        client:
           rabbitmq:
             host: "<Sensu RMQ Host>"
             user: "<RMQ Sensu client user>"
             password: "<Monitoring Client RMQ Password>"
           subscriptions: ["cfmonit"]
           deployment_name: (( meta.name ))
           
The deployment_name sets a prefix for the instances BOSH job name. 
We don't report real hostnames to Sensu as they are pretty useless (BOSH ensure's we get a new one everytime it blows away a VM or updates a stemcell). Instead we report the hostname to sensu as ```job_name.deployment_name```

For example. We use this for our BOSH deployment name, so my 'hostnames' in sensu will be ```dea0.deployment1```  or ```nats0.deployment1``` etc, allowing me to also monitor a different CF deployment, ie ```dea0.deployment2``` with the same Sensu cluster and not get confused.

### Final releases

There are no final releases yet, so you'll need to do the following to upload the release to your bosh director;

    $ git clone https://github.com/FreightTrain/sensu-client-boshrelease.git
    $ cd sensu-client-boshrelease
    $ bosh create release --force
    $ bosh upload release --rebase

