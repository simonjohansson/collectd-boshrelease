# Sensu Client BOSH Release

<a href="http://docs.cloudfoundry.org/bosh/"><img src="https://raw.githubusercontent.com/FreightTrain/sensu-client-boshrelease/master/docs/images/logos/bosh-clam.png" style="height:60px"/></a> <a href="http://sensuapp.org/"><img src="https://raw.githubusercontent.com/FreightTrain/sensu-client-boshrelease/master/docs/images/logos/sensu_fan.png" style="height:60px"/></a> <a href="https://collectd.org/"><img src="https://raw.githubusercontent.com/FreightTrain/sensu-client-boshrelease/master/docs/images/logos/collectd.png" style="height:60px"/></a>

[![image](https://api.travis-ci.org/FreightTrain/sensu-client-boshrelease.svg?branch=master)](https://travis-ci.org/FreightTrain/sensu-client-boshrelease/builds)

## What it is

This release contains the following:

* A BOSH job to install a [Sensu Client](http://sensuapp.org/docs/0.11/clients).
  * Sensu Client is configured to monitor the vitals of the Host.
  * Sensu Client also monitors the health of Monit jobs running on the machine.
   
* A BOSH job to install [Collectd](https://collectd.org/).
  * Collectd is configured, by default, to send metric data over Sensu.
  * Collectd sends metrics for the vitals of the host.
  * Collectd sends metrics for CloudFoundry applications by monitoring /varz endpoints.
     * Currently supported CloudFoundry Jobs are:
         * GoRouter 

The purpose of this release is to be deployed alongside [cf-release](https://github.com/cloudfoundry/cf-release) to provide monitoring and alerting on the CloudFoundry deployment.

## What it isn't

* A general purpose Sensu Client installation surfacing all configuration options.

## Getting Started

### Example CF Manifest Fragment

    releases:
     - name: cf
       version: xxx
     - name: sensu-client
       version: latest
    
    jobs:
     - name: nats
       templates:
        - name: nats
          release: cf
        - name: sensu_client
          release: sensu-client
        - name: collectd
          release: sensu-client
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
      collectd:
        hostname_prefix: "(( meta.name ))."

### CF Manifest Configuration

We don't report BOSH UUID hostnames to Sensu. Instead we report the hostname to sensu as 

    job_name.deployment_name
    

The prefix is set by the property ```sensu.deployment_name```.

The host names shown in Sensu will look similar to the following:

    dea0.deployment1
    dea1.deployment1
    nats0.deployment1
    ...
    
## Configuring Sensu

### Configuring the Sensu Client

The ```sensu-client``` job contains two config files:

* ```/etc/client.json```<br>To configure the sensu client.

* ```/etc/rabbitmq.json.erb```<br>To configure how sensu client talks to RMQ.

### Configuring checks on the Sensu Server 

A Sensu check should be configured on the Sensu Server attached to subscription ```monitcf``` (default name in the release and check script). 

This executes ```/var/vcap/packages/sensu_client/parsemonit.py``` every 5 seconds.

This check reports the health of each monit job as it's own check (via the localhost:3030 sensu TCP port). The result is that a failed ```nats``` monit job will show in Sensu as check type ```nats```

### Installing a Sensu Server 

This BOSH release does not currently contain jobs to install a Sensu Server. The following references should help you on your way:
  
* [Sensu Documentation :: Installing Sensu](http://sensuapp.org/docs/0.11/installing_sensu)
* [The Puppet and Heira configutation we use :: InstallingSensuServer.md](https://github.com/FreightTrain/sensu-client-boshrelease/blob/master/docs/InstallingSensuServer.md)
         
## Credit

Third Party Code built into this BOSH release:
            
#### collectd-sensu
[github.com/jhmartin/collectd-sensu](https://github.com/jhmartin/collectd-sensu)<br>
This CollectD plugin has been used, with some slight modifications, to publish CollectD values using Sensu.

#### logsearch-boshrelease
[github.com/logsearch/logsearch-boshrelease](https://github.com/logsearch/logsearch-boshrelease)<br>
The BOSH Job for CollectD packaged within this BOSH Release is a customized version of the CollectD job from the Logsearch BOSH release.
