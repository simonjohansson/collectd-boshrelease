import subprocess
import json
import socket 

from MonitOutputParser  import MonitOutputParser
from SensuOutputBuilder import SensuOutputBuilder

class ParseMonit():
    """
    Parse the output of Monit and send that output to Sensu.
    Any monit Job which is not in the "running" state will be sent through as a Critical Alert.
    """

    def __init__(self):
        """
        Setup constants for accessing Monit
        """

        self.MONIT_IP   = '127.0.0.1'
        self.MONIT_PORT = 3030

    def send_alert_to_sensu(self, sensu_json):
        """
        Send the alert to the local Sensu agent.
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.MONIT_IP,self.MONIT_PORT))
        s.send(sensu_json)
        s.close()

    def execute_monit_in_shell(self):
        """
        Call out to the shell to query Monit.
        """
        monit = subprocess.Popen('/var/vcap/bosh/bin/monit status', shell=True, stdout=subprocess.PIPE)
        stdout, stderr = monit.communicate()
        return stdout

    def main(self):
        """
        Run `monit status` the the output and send it to Sensu.
        """
        monit_stdout = self.execute_monit_in_shell()
        monit_status = MonitOutputParser().parse_status(monit_stdout)

        for key in monit_status.keys():
            sensu_json = SensuOutputBuilder().create_output_for_job(key, monit_status[key])
            self.send_alert_to_sensu(sensu_json)

if __name__ == '__main__':
    ParseMonit().main()