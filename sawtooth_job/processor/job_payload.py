# 
# -----------------------------------------------------------------------------

import cbor

from sawtooth_sdk.processor.exceptions import InvalidTransaction


class JobPayload:

    def __init__(self, payload):
        print('+++payload: ')
        print(payload)
        try:
            # load payload
            jobId, workerId, publisherId, publisherId, start_time, end_time, deadline, base_rewards, extra_rewards, action = payload.decode().split(",")
        except ValueError:
            raise InvalidTransaction("Invalid payload serialization")
        if not jobId:
            raise InvalidTransaction('jobId is required')

        if not workerId:
            raise InvalidTransaction('workerId is required')

        if not publisherId:
            raise InvalidTransaction('publisherId is required')

        if not start_time:
            raise InvalidTransaction('start_time is required')

        if not end_time:
            raise InvalidTransaction('end_time is required')

        if not deadline:
            raise InvalidTransaction('deadline is required')

        if not base_rewards:
            raise InvalidTransaction('base_rewards is required')

        if not extra_rewards:
            raise InvalidTransaction('extra_rewards is required')

        if not action:
            raise InvalidTransaction('Action is required')
        # try:
        #     jobId = content['jobId']
        #     print('++++jobId type: ' + type(jobId))
        # except AttributeError:
        #     raise InvalidTransaction('jobId is required')

        # try:
        #     workerId = content['workerId']
        #     print('++++workerId type: ' + type(workerId))
        # except AttributeError:
        #     raise InvalidTransaction('Name is required')

        # try:
        #     publisherId = content['publisherId']
        #     print('++++publisherId type: ' + type(publisherId))
        # except AttributeError:
        #     raise InvalidTransaction('publisherId is required')

        # try:
        #     start_time = content['start_time']
        #     print('++++start_time type: ' + type(start_time))
        # except AttributeError:
        #     raise InvalidTransaction('start_time is required')

        # try:
        #     end_time = content['end_time']
        #     print('++++end_time type: ' + type(end_time))
        # except AttributeError:
        #     raise InvalidTransaction('publisherId is required')

        # try:
        #     deadline = content['deadline']
        #     print('++++deadline type: ' + type(deadline))
        # except AttributeError:
        #     raise InvalidTransaction('deadline is required')

        # try:
        #     base_rewards = content['base_rewards']
        #     print('++++base_rewards type: ' + type(base_rewards))
        # except AttributeError:
        #     raise InvalidTransaction('base_rewards is required')
        
        # try:
        #     extra_rewards = content['extra_rewards']
        #     print('++++extra_rewards type: ' + type(extra_rewards))
        # except AttributeError:
        #     raise InvalidTransaction('extra_rewards is required')
        
        # try:
        #     action = content['action']
        #     print('++++action type: ' + type(action))
        # except AttributeError:
        #     raise InvalidTransaction('action is required')

        if action not in ('create', 'ggetByIdet', 'getByWorker'):
            raise InvalidTransaction('Invalid action: {}'.format(action))

        self._jobId = jobId
        self._workerId = workerId
        self._publisherId = publisherId
        self._start_time = start_time
        self._end_time = end_time
        self._deadline = deadline
        self._base_rewards = base_rewards
        self._extra_rewards = extra_rewards
        self._action = action

    @staticmethod
    def load_job(payload):
        return JobPayload(payload=payload)

    @property
    def jobId(self):
        return self._jobId

    @property
    def workerId(self):
        return self._workerId

    @property
    def publisherId(self):
        return self._publisherId

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time
    
    @property
    def deadline(self):
        return self._deadline

    @property
    def base_rewards(self):
        return self._base_rewards

    @property
    def extra_rewards(self):
        return self._extra_rewards

    @property
    def action(self):
        return self._action

    
