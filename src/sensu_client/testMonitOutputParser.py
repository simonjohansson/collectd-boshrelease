import random
import unittest

from MonitOutputParser import MonitOutputParser

class TestSequenceFunctions(unittest.TestCase):
    """
    Test the MonitOutputParser
    """

    def setUp(self):

        self.test_output_monit_summary_three_monit_jobs_running="""The Monit daemon 5.2.4 uptime: 2d 13h 29m"
Process 'jenkins_master'            running
Process 'nginx_jenkins_master'      running
Process 'configure_jenkins'         running
System 'system_2f06434c-b234-4585-9962-8275a09dadfa' running
"""

        self.test_output_monit_summary_all_statuses="""The Monit daemon 5.2.4 uptime: 2d 13h 29m"
Process 'job_a'                     not monitored
Process 'job_b'                     monitored
Process 'job_c'                     initializing
Process 'job_d'                     accessible
Process 'job_e'                     running
Process 'job_f'                     online with all services
System 'system_2f06434c-b234-4585-9962-8275a09dadfa' running
"""

        self.test_output_monit_status_three_jobs_running="""The Monit daemon 5.2.4 uptime: 2d 14h 33m

Process 'jenkins_master'
  status                            running
  monitoring status                 monitored
  pid                               27102
  parent pid                        1
  uptime                            15d 0h 35m
  children                          0
  memory kilobytes                  3357076
  memory kilobytes total            3357076
  memory percent                    40.9%
  memory percent total              40.9%
  cpu percent                       1.4%
  cpu percent total                 1.4%
  data collected                    Tue Sep  2 12:03:22 2014

Process 'nginx_jenkins_master'
  status                            running
  monitoring status                 monitored
  pid                               27339
  parent pid                        1
  uptime                            15d 0h 35m
  children                          1
  memory kilobytes                  892
  memory kilobytes total            6052
  memory percent                    0.0%
  memory percent total              0.0%
  cpu percent                       0.0%
  cpu percent total                 0.0%
  data collected                    Tue Sep  2 12:03:22 2014

Process 'configure_jenkins'
  status                            running
  monitoring status                 monitored
  pid                               30080
  parent pid                        1
  uptime                            13d 9h 35m
  children                          0
  memory kilobytes                  62944
  memory kilobytes total            62944
  memory percent                    0.7%
  memory percent total              0.7%
  cpu percent                       0.0%
  cpu percent total                 0.0%
  data collected                    Tue Sep  2 12:03:22 2014

System 'system_2f06434c-b234-4585-9962-8275a09dadfa'
  status                            running
  monitoring status                 monitored
  load average                      [0.86] [0.72] [0.75]
  cpu                               7.0%us 0.5%sy 0.1%wa
  memory usage                      3659048 kB [44.6%]
  swap usage                        0 kB [0.0%]
  data collected                    Tue Sep  2 12:03:22 2014"""


        self.test_output_monit_status_job_failing="""
The Monit daemon 5.2.4 uptime: 19m

Process 'jenkins_master'
  status                            running
  monitoring status                 monitored
  pid                               27102
  parent pid                        1
  uptime                            15d 1h 58m
  children                          0
  memory kilobytes                  3288416
  memory kilobytes total            3288416
  memory percent                    40.1%
  memory percent total              40.1%
  cpu percent                       0.0%
  cpu percent total                 0.0%
  data collected                    Tue Sep  2 13:26:41 2014

Process 'nginx_jenkins_master'
  status                            not monitored
  monitoring status                 not monitored
  data collected                    Tue Sep  2 13:26:41 2014

Process 'configure_jenkins'
  status                            Does not exist
  monitoring status                 monitored
  data collected                    Tue Sep  2 13:26:42 2014

System 'system_2f06434c-b234-4585-9962-8275a09dadfa'
  status                            running
  monitoring status                 monitored
  load average                      [0.74] [0.86] [0.92]
  cpu                               0.0%us 0.0%sy 0.2%wa
  memory usage                      3527292 kB [43.0%]
  swap usage                        0 kB [0.0%]
  data collected                    Tue Sep  2 13:26:42 2014"""


    # Make sure the summary parser returns the correct number of jobs
    def test_monit_summary_correct_number_jobs_returned(self):
        monit_summary = MonitOutputParser().parse_summary(self.test_output_monit_summary_three_monit_jobs_running)
        self.assertEqual(len(monit_summary.keys()), 3)

    # Make sure the summary parser populates the correct keys
    def test_correct_keys_returned(self):
        monit_summary = MonitOutputParser().parse_summary(self.test_output_monit_summary_three_monit_jobs_running)
        self.assertTrue('jenkins_master' in monit_summary.keys())
        self.assertTrue('nginx_jenkins_master' in monit_summary.keys())
        self.assertTrue('configure_jenkins' in monit_summary.keys())

    # Make sure the summary parser populates the correct status values
    def test_correct_status_returned(self):
        monit_summary = MonitOutputParser().parse_summary(self.test_output_monit_summary_three_monit_jobs_running)
        self.assertTrue(monit_summary['jenkins_master'] == 'running')
        self.assertTrue(monit_summary['nginx_jenkins_master'] == 'running')
        self.assertTrue(monit_summary['configure_jenkins'] == 'running')

    # Make sure the summary parser works for all known Monit statuses
    def test_correct_status_returned(self):
        monit_summary = MonitOutputParser().parse_summary(self.test_output_monit_summary_all_statuses)
        self.assertEqual(len(monit_summary.keys()), 6)
        self.assertTrue(monit_summary['job_a'] == 'not monitored')
        self.assertTrue(monit_summary['job_b'] == 'monitored')
        self.assertTrue(monit_summary['job_c'] == 'initializing')
        self.assertTrue(monit_summary['job_d'] == 'accessible')
        self.assertTrue(monit_summary['job_e'] == 'running')
        self.assertTrue(monit_summary['job_f'] == 'online with all services')

    # Make sure the status parser returns the right number of jobs
    def test_monit_status_correct_number_jobs_returned(self):
        monit_status = MonitOutputParser().parse_status(self.test_output_monit_status_three_jobs_running)
        self.assertEqual(len(monit_status.keys()), 3)

    # Make sure the status parser works
    def test_monit_status_correct_job_name_retuened(self):
        monit_status = MonitOutputParser().parse_status(self.test_output_monit_status_three_jobs_running)
        self.assertTrue('jenkins_master' in monit_status.keys())
        self.assertTrue('nginx_jenkins_master' in monit_status.keys())
        self.assertTrue('configure_jenkins' in monit_status.keys())

    # Make sure the status parser returns the correct jobs
    def test_monit_status_correct_job_name_retuened(self):
        monit_status = MonitOutputParser().parse_status(self.test_output_monit_status_three_jobs_running)
        self.assertTrue('jenkins_master' in monit_status.keys())
        self.assertTrue('nginx_jenkins_master' in monit_status.keys())
        self.assertTrue('configure_jenkins' in monit_status.keys())

    # Make sure the status parser returns the correct values for the jobs
    def test_monit_status_correct_job_name_returned(self):
        monit_status = MonitOutputParser().parse_status(self.test_output_monit_status_three_jobs_running)
        self.assertTrue(monit_status['jenkins_master']['status'] == 'running')
        self.assertTrue(monit_status['jenkins_master']['monitoring status'] == 'monitored')
        self.assertTrue(monit_status['jenkins_master']['pid'] == '27102')

    # Make sure the status parser works if a job is failing
    def test_monit_status_correct_when_jobs_are_failing(self):
        monit_status = MonitOutputParser().parse_status(self.test_output_monit_status_job_failing)
        self.assertEqual(len(monit_status.keys()), 3)
        self.assertTrue(monit_status['configure_jenkins']['status'] == 'Does not exist')
        self.assertTrue(monit_status['configure_jenkins']['monitoring status'] == 'monitored')
        self.assertTrue(monit_status['nginx_jenkins_master']['status'] == 'not monitored')
        self.assertTrue(monit_status['nginx_jenkins_master']['monitoring status'] == 'not monitored')

if __name__ == '__main__':
    unittest.main()