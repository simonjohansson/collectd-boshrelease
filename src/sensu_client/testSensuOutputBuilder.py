import json
import unittest

from SensuOutputBuilder import SensuOutputBuilder

class TestSequenceFunctions(unittest.TestCase):
    """
    Test the SensuOutputBuilder
    """

    def setUp(self):

        self.sensu_healthy_job_output = {'status' : 'running'}
        self.sensu_healthy_json_output='{"status": 0, "name": "test job", "handlers": ["twitter"], "monit data status": "running", "subscribers": "cfmonit", "output": "Monit Job test job is running", "type": "monit"}'
        self.sensu_unhealthy_job_output = {'status' : 'not monitored'}
        self.sensu_pending_action_job_output = {'status' : 'restart pending'}

    def test_sensu_output_contains_the_correct_data(self):
        """
        Make sure the basic parser returns the correct JSON
        """
        sensu_output_healthy = SensuOutputBuilder().create_output_for_job('test job', self.sensu_healthy_job_output)
        self.assertEqual(sensu_output_healthy, self.sensu_healthy_json_output)

    def test_sensu_output_contains_all_required_fields(self):
        """
        Make sure the summary parser returns the correct number of jobs.
        """
        sensu_output_healthy = SensuOutputBuilder().create_output_for_job('test job', self.sensu_healthy_job_output)
        sensu_output_healthy_json = json.loads(sensu_output_healthy)
        self.assertTrue('type' in sensu_output_healthy_json)
        self.assertTrue('output' in sensu_output_healthy_json)
        self.assertTrue('handlers' in sensu_output_healthy_json)
        self.assertTrue('subscribers' in sensu_output_healthy_json)
        self.assertTrue('name' in sensu_output_healthy_json)
        self.assertTrue('status' in sensu_output_healthy_json)

    def test_sensu_output_returns_heathly_status_for_healthy_jobs(self):
        """
        Make sure the summary parser returns the correct number of jobs
        """
        sensu_output_healthy = SensuOutputBuilder().create_output_for_job('test job', self.sensu_healthy_job_output)
        sensu_output_healthy_json = json.loads(sensu_output_healthy)
        self.assertTrue('status' in sensu_output_healthy_json)
        self.assertEqual(sensu_output_healthy_json['status'], 0)

    def test_sensu_output_returns_error_status_for_failed_jobs(self):
        """
        Make sure the summary parser returns the correct number of jobs
        """
        sensu_output_dead = SensuOutputBuilder().create_output_for_job('test job', self.sensu_unhealthy_job_output)
        sensu_output_dead_json = json.loads(sensu_output_dead)
        self.assertTrue('status' in sensu_output_dead_json)
        self.assertEqual(sensu_output_dead_json['status'], 2)

    def test_sensu_output_returns_warning_status_for_pending_jobs(self):
        """
        Make sure the summary parser returns the correct number of jobs
        """
        sensu_output_pending = SensuOutputBuilder().create_output_for_job('test job', self.sensu_pending_action_job_output)
        sensu_output_pending_json = json.loads(sensu_output_pending)
        self.assertTrue('status' in sensu_output_pending_json)
        self.assertEqual(sensu_output_pending_json['status'], 1)

if __name__ == '__main__':
    unittest.main()
