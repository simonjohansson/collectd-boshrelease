# Installing a Sensu Server

This release does not currently contain a Sensu Server Job (feel free to contribute one).

We manage our Sensu Server with Puppet rather than BOSH. The following is the Puppet configuration used.

## Sensu Server Configuration

Here are some snippets from our sensu server configuration that may be helpful.

We are currently wrapping the sensu puppet module to install the server components with parameterized classes pulling data from heira lookups.

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
