# CollectD

The [CollectD](http://collectd.org/) Job in this release deploys CollectD onto a BOSH managed Machine.


## Getting Data From CollectD

Currently there are two output options for the CollectD data:

1. **Sensu**

	Enabled by default. This can be configured in your BOSH manifest:
	
	    collectd.sensu_output_enabled: [true|false]

    CollectD data will be sent to a local Sensu Client [using a CollectD plugin](https://github.com/jhmartin/collectd-sensu). By default the Sensu output expects the Sensu Client to listen on ```localhost:3030```.


2. **CSV**

	Disabled by default. This can be enabled in your BOSH manifest:
	
		collectd.csv_output_enabled: [true|false]
		
    CSVs will be written to the directory:
    
	    /var/vcap/sys/run/collectd/
	
## Dynamic Configuration (collectd.d_dynamic)

This is a folder of CollectD configuration which is dynamically enabed and disabled when the presence of other BOSH jobs is detected on the VM.

### 20-cf-gorouter.conf.erb

This CollectD configuration uses the [json_curl](https://collectd.org/wiki/index.php/Plugin:cURL-JSON) plugin for CollectD to read the CloudFoundry [GoRouter /varz](https://github.com/cloudfoundry/gorouter#instrumentation) output.

The GoRouter varz JSON output used to develop the current configuration is available at: [router_varz_example.json](https://github.com/FreightTrain/sensu-client-boshrelease/blob/master/docs/CollectD/router_varz_example.json)