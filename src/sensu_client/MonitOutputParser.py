import os
import re 

class MonitOutputParser:
    """
    Parse the output from the Monit CLI
    Return the output from Monit as a set of Dictionaries.

    There is a reference for the possible status values from monit is available 
    https://github.com/arnaudsj/monit/blob/master/monitor.c#L142-L143
    """

    def __init__(self):
        pass

    def parse_summary(self, monit_summary_stdout):
        """
        A small parser to consume the output of `monit summary`

        For Example:

        root@2f06434c-b234-4585-9962-8275a09dadfa:~# monit summary
        The Monit daemon 5.2.4 uptime: 2d 13h 29m

        Process 'jenkins_master'            running
        Process 'nginx_jenkins_master'      running
        Process 'configure_jenkins'         running
        System 'system_2f06434c-b234-4585-9962-8275a09dadfa' running
        """
        monit_summary_jobs = {}

        for line in monit_summary_stdout.split(os.linesep):

            if "Process" in line:
                process,job,state = line.split("'",3)


                job_status = {}
                state = state.strip()
                job = job.strip()
                monit_summary_jobs[job] = state

        return monit_summary_jobs

    def parse_status(self, monit_status_stdout):
        """
        The Monit daemon 5.2.4 uptime: 2d 14h 33m

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
        """
        monit_status_jobs = {}
        current_job_status = None
        current_job_name = None

        for line in monit_status_stdout.split(os.linesep):

            # If this is the start of a new process
            if "Process" in line:
                process,job,token = line.split("'",3)
                current_job_status = {}
                current_job_name = job.strip()

            # If this is an Empty Line
            elif not line.strip():
                if current_job_name is not None:
                    monit_status_jobs[current_job_name] = current_job_status
                current_job_status = None
                current_job_name = None

            elif current_job_status is not None:
                # Split on two or more spaces.
                regex = re.compile(r'[ \t\n\r\f\v][ \t\n\r\f\v]+')
                tokens = filter(None,regex.split(line))
                key = tokens.pop(0).strip()
                current_job_status[key] = " ".join(tokens).strip()

        return monit_status_jobs