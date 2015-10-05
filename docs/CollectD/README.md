# CollectD

The [CollectD](http://collectd.org/) Job in this release deploys CollectD onto a BOSH managed Machine.


## Connecting to graphite

Configure graphite.server and optionally graphite.port properties (unless you want to use default port 2003). You can also configure collectd prefix via graphite.prefix property.
	
## Dynamic Configuration (collectd.d_dynamic)

This is a folder of CollectD configuration which is dynamically enabed and disabled when the presence of other BOSH jobs is detected on the VM.

### 20-cf-gorouter.conf.erb

This CollectD configuration uses the [json_curl](https://collectd.org/wiki/index.php/Plugin:cURL-JSON) plugin for CollectD to read the CloudFoundry [GoRouter /varz](https://github.com/cloudfoundry/gorouter#instrumentation) output.

The GoRouter varz JSON output used to develop the current configuration is available at: [router_varz_example.json](https://github.com/FreightTrain/sensu-client-boshrelease/blob/master/docs/CollectD/router_varz_example.json)
