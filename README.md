# Sensu Client BOSH Release

![image](https://api.travis-ci.org/FreightTrain/sensu-client-boshrelease.svg?branch=master)

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
* Best practice - Sensu Client is installed .DEB for example instead of compiling everything from scratch.

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


The deployment_name sets a prefix for the instances BOSH job name. 
We don't report real hostnames to Sensu as they are pretty useless (BOSH ensure's we get a new one everytime it blows away a VM or updates a stemcell). Instead we report the hostname to sensu as ```job_name.deployment_name```

For example. We use this for our BOSH deployment name, so my 'hostnames' in sensu will be ```dea0.deployment1```  or ```nats0.deployment1``` etc, allowing me to also monitor a different CF deployment, ie ```dea0.deployment2``` with the same Sensu cluster and not get confused.
    
### Technical Info

#### Startup

The release includes two source files. 

* A debian '.deb' debian package of the standard sensu installation (grabbed directly from Sensu's repo) 
* A custom check script for running monit status/monit summary and parsing the output

the DEB is in the release blobstore, the check script is written (questionably!) in python and under src/

The packaging script just moves the two files to /var/vcap/packages/sensu_client/.
There are also three template files:

    - rabbitmq.json - the configuration file for the sensu client to talk to RMQ
    - client.json - the standard configuration file for the sensu client
    - sensu_client_ctl - a start/stop script based losley on the one from the sensu DEB

The single job, sensu-client then has all the logic (read, hackery) for making the magic happen in it's startup script.

    - Unpacks the DEB at a fake root of /var/vcap/jobs/sensu_client
        - The templated client and rabbitmq .json match up to the needed locations /var/vcap/jobs/sensu_client/etc/sensu/conf.d
        
    - Maps /opt/sensu to /var/vcap/jobs/sensu_client/opt/sensu (ln -s) due to hardcoded paths in Sensu's ruby
    - Moves/updates the custom monit check script into /var/vcap/jobs/sensu_client/etc/sensu/cpgplugins directory (as thats where we have configured the sensu check on the server to execute the script from. Custom DIR for all of our teams plugins)
    
    - Starts sensu
    
#### Normal operation

A Sensu check should be configured on the sensu server attached to subscription 'monitcf' (default name in the release and check script). This executes ```/var/vcap/jobs/sensu_client/etc/sensu/cpgplugins/parsemonit.py``` every 5 seconds.

The script itself then reports the health of each monit job as it's own check (via the localhost:3030 sensu TCP port) speaking sensu's reporting format. Therefore a failed ```nats``` monit job will show in sensu as check type ```nats```

The script queries monit for all jobs and puts them in an error state if they are anything other than 'running', therefore all new monit jobs will be monitored automatically.

Because the script is writing out it's own Sensu style alerts over localhost:3030, the script itself contains some information which needs templating out into the monit configuration, such as:

    - The subscription the reported check is claiming to be on
    - The handlers which should receive the check in sensu-server.
    
I'm currently outputting to twitter at the sensu headend as a demo, using the handler here:
https://github.com/matjohn2/sensu-community-plugins/blob/master/handlers/notification/twitter_v5.rb


## Sensu Server Configuration

Here are some snippets from our sensu server configuration that may be helpful.

We are currently wrapping the sensu puppet module to install the server components with parameterized classes pulling data from heira lookups (standard, but always useful to give people a branch to google from if new to the tech).

Puppet module manifest:

                        class wrapperclass::monitoring::sensuserver($sensu_rabbitmq_password,$sensu_client_rabbitmq_password){
                        
                        ensure_packages(["mysql-devel.x86_64","sqlite-devel.x86_64", "libxml2-devel", "libxslt-devel", "wget", "git", "bzr", "golang"])
                    
            
                        # Needed for sensu-puppet module deps
                        package{ "rubygem-json": ensure => "installed" } ->
                        
                        
                         firewall { "200 allow Sensu API and Dashboard access and 3000 for demo sensu-admin UI":
                            port   => [4567, 8080, 3000],
                            proto  => tcp,
                            state  => NEW,
                            action => accept,
                            }
                        
                        # Use sensu module to install sensu
                        
                        include ::sensu
                        
                        ## Checks
                        
                        ::sensu::check { 'parsemonit':
                            command => '/var/vcap/jobs/sensu_client/etc/sensu/cpgplugins/parsemonit.py',
                            subscribers => 'cfmonit',
                            interval => '5',
                            standalone => false,
                            ensure => 'present'
                          }
                        
                        ## Handlers
                        
                        ::sensu::handler { 'twitter':
                            type => 'pipe',
                            command => '/etc/sensu/handlers/twitter.rb',
                            source => 'puppet:///modules/cpg/monitoring/sensu/handlers/twitter.rb',
                            config => { 
                                      brokenpaas => { 
                                            sensusub => "cfmonit", 
                                            consumer_key => "TheseAreMyAPIKeys",
                                            consumer_secret => "ThereAreManyLikeItButTheseOnesAreMine",
                                            oauth_token => "MyApiKeysLetMeSendAlertsToOtherPeopleViaTwitter",
                                            oauth_token_secret => "SoThatIcanGoToThePub"
                                            } 
                                      }
                            }
            
Heira for Sensu server role:

        ---
        classes:
          - wrapperclass::monitoring::sensuserver
        
        wrapperclass::monitoring::sensuserver::sensu_rabbitmq_password: "somepass"
        wrapperclass::monitoring::sensuserver::sensu_client_rabbitmq_password: "somepass"
        
        sensu::server: true
        sensu::client: true
        
        sensu::api: true
        sensu::dashboard: true
        sensu::dashboard_password: somepass
        sensu::install_repo: true
        sensu::repo: 'unstable'
        sensu::purge_config: false
        sensu::rabbitmq_password: "somepass"
        sensu::rabbitmq_port: 5672
        sensu::rabbitmq_vhost: "sensu"
        sensu::rabbitmq_host: 192.168.1.1
        sensu::redis_host: 192.168.1.1
        sensu::use_embedded_ruby: true
        sensu::subscriptions: 'common'

   

            
         
## Credit

Third Party Code built into this BOSH release:
            
#### collectd-sensu
[github.com/jhmartin/collectd-sensu](https://github.com/jhmartin/collectd-sensu)<br>
This CollectD plugin has been used, with some slight modifications, to publish CollectD values using Sensu.

#### logsearch-boshrelease
[github.com/logsearch/logsearch-boshrelease](https://github.com/logsearch/logsearch-boshrelease)<br>
The BOSH Job for CollectD packaged within this BOSH Release is a customized version of the CollectD job from the Logsearch BOSH release.
