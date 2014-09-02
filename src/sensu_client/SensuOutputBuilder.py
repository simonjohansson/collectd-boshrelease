
import json

class SensuOutputBuilder:
    """
    Build the responses we send to sensu

    The 'status' returned is a Nagios NPRE Return Code
    See: https://nagios-plugins.org/doc/guidelines.html#RETURNCODES
    """

    def __init__(self):

        self.npre_codes = {'running' : 0}
        self.sensu_handlers = ['twitter']
    

    def create_output_for_job(self, job_name, monit_job_output):

        job_status = self.get_npre_code(monit_job_output['status'])

        report = {}
        report['output']      = 'Monit Job ' + job_name + ' is ' + monit_job_output['status']
        report['name']        = job_name
        report['handlers']    = self.sensu_handlers
        report['subscribers'] = 'cfmonit'
        report['status']      = job_status
        report['type']        = 'monit'

        for key,value in monit_job_output.iteritems():
            report['monit data ' + key] = value
            
        return json.dumps(report)

        
    def get_npre_code(self, monit_status):
        """
        Convert a monit status to an NPRE Code
        The 'status' returned is a Nagios NPRE Return Code
        See: https://nagios-plugins.org/doc/guidelines.html#RETURNCODES
        """

        status = 2 # Default to failure

        if monit_status in self.npre_codes:
            status = self.npre_codes[monit_status]

        return status
