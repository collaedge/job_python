# state class turn job info into bytes and store in the validator's Radix-Merkle tree
# and turn bytes into job info
# 
# -- stored job info --
# - job id
# - publisher id 
# - worker id
# - working time, it is the time that worker spend on the job
# - deadline
# - base rewards
# - extra rewards
# -----------------------------------------------------------------------------

import hashlib
import cbor

from sawtooth_sdk.processor.exceptions import InternalError


JOB_NAMESPACE = hashlib.sha512('job'.encode("utf-8")).hexdigest()[0:6]


def _make_job_address(name):
    return JOB_NAMESPACE + \
        hashlib.sha512(name.encode('utf-8')).hexdigest()[:64]


class Job:
    def __init__(self, jobId, workerId, working_time, deadline, base_rewards, extra_rewards):
        self.jobId = jobId
        self.workerId = workerId
        self.working_time = working_time
        self.deadline = deadline
        self.base_rewards = base_rewards
        self.extra_rewards = extra_rewards


class JobState:

    TIMEOUT = 3

    def __init__(self, context):
        """Constructor.

        Args:
            context (sawtooth_sdk.processor.context.Context): Access to
                validator state from within the transaction processor.
        """
        self._context = context
        self._address_cache = {}

    def set_job(self, jobId, job):
        """Store the job in the validator state.

        Args:
            jobId (str): The id.
            job (Job): The information specifying the current job.
        """

        jobs = self._load_jobs(jobId=jobId)
        print('+++++++++++++++++++++++++++jobs before set:')
        print(jobs)
        jobs[jobId] = job
        print('+++++++++++++++++++++++++++jobs after set:')
        print(jobs)
        self._store_job(jobId, jobs=jobs)

    def get_job(self, jobId):
        """Get the job associated with jobId.

        Args:
            jobId (str): The ids.

        Returns:
            (Job): All the information specifying a job.
        """

        return self._load_jobs(jobId=jobId).get(jobId)

    def _store_job(self, jobId, jobs):
        address = _make_job_address(jobId)
        print('+++++++++++++++++++++++++++jobs address:')
        print(address)
        state_data = cbor.dumps(jobs)
        print('state data' + state_data)
        self._address_cache[address] = state_data

        self._context.set_state(
            {address: state_data},
            timeout=self.TIMEOUT)

    def _load_jobs(self, jobId):
        address = _make_job_address(jobId)

        if address in self._address_cache:
            if self._address_cache[address]:
                serialized_jobs = self._address_cache[address]
                jobs = cbor.loads(serialized_jobs)
            else:
                jobs = {}
        else:
            state_entries = self._context.get_state(
                [address],
                timeout=self.TIMEOUT)
            if state_entries:

                self._address_cache[address] = state_entries[0].data

                jobs = cbor.loads(state_entries[0].data)

            else:
                self._address_cache[address] = None
                jobs = {}

        return jobs

