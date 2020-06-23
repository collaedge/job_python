# Copyright 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
from __future__ import division

import uuid
import hashlib
import base64
from base64 import b64encode
import time
import random
import requests
import yaml
import cbor

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

from sawtooth_job.job_exceptions import JobException


def _sha512(data):
    return hashlib.sha512(data).hexdigest()

# constant
P = 0.8
class JobClient:
    

    def __init__(self, base_url, keyfile=None):

        self._base_url = base_url

        if keyfile is None:
            self._signer = None
            return

        try:
            with open(keyfile) as fd:
                private_key_str = fd.read().strip()
        except OSError as err:
            raise JobException(
                'Failed to read private key {}: {}'.format(
                    keyfile, str(err)))

        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as e:
            raise JobException(
                'Unable to load private key: {}'.format(str(e)))

        self._signer = CryptoFactory(create_context('secp256k1')) \
            .new_signer(private_key)

    def create(self, wokerId, publisherId, start_time, end_time, deadline, base_rewards, wait=None):
        jobId = str(uuid.uuid1())
        extra_rewards = ((P*(deadline - (end_time - start_time))) / deadline)*base_rewards
        return self._send_transaction(
            jobId,
            wokerId,
            publisherId,
            start_time,
            end_time,
            base_rewards,
            extra_rewards,
            "create",
            wait=wait,
            )

    def getJob(self, jobId, space, wait=None):
        return self._send_transaction(
            jobId=jobId,
            action="get",
            wait=wait)

    def list(self):
        prefix = self._get_prefix()

        result = self._send_request(
            "state?address={}".format(prefix),
            )

        try:
            encoded_entries = yaml.safe_load(result)["data"]

            return [
                base64.b64decode(entry["data"]) for entry in encoded_entries
            ]

        except BaseException:
            return None

    def show(self, jobId):
        address = self._get_address(jobId)

        result = self._send_request(
            "state/{}".format(address),
            jobId=jobId,
            )
        try:
            return base64.b64decode(yaml.safe_load(result)["data"])

        except BaseException:
            return None

    def _get_status(self, batch_id, wait):
        try:
            result = self._send_request(
                'batch_statuses?id={}&wait={}'.format(batch_id, wait),
                )
            return yaml.safe_load(result)['data'][0]['status']
        except BaseException as err:
            raise JobException(err)

    def _get_prefix(self):
        return _sha512('job'.encode('utf-8'))[0:6]

    def _get_address(self, jobId):
        prefix = self._get_prefix()
        job_address = _sha512(jobId.encode('utf-8'))[0:64]
        return prefix + job_address

    def _send_request(self,
                      suffix,
                      data=None,
                      content_type=None,
                      jobId=None):
        if self._base_url.startswith("http://"):
            url = "{}/{}".format(self._base_url, suffix)
        else:
            url = "http://{}/{}".format(self._base_url, suffix)

        headers = {}

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if result.status_code == 404:
                raise JobException("No such job: {}".format(jobId))

            if not result.ok:
                raise JobException("Error {}: {}".format(
                    result.status_code, result.reason))

        except requests.ConnectionError as err:
            raise JobException(
                'Failed to connect to {}: {}'.format(url, str(err)))

        except BaseException as err:
            raise JobException(err)

        return result.text

    def _send_transaction(self,
                    jobId,
                    wokerId,
                    publisherId,
                    start_time,
                    end_time,
                    base_rewards,
                    extra_rewards,
                    action,
                    wait=None):
        # Serialization is just a delimited utf-8 encoded string
        payload = cbor.dumps({
            'jobId': jobId,
            'wokerId': wokerId,
            'publisherId': publisherId,
            'start_time': start_time,
            'end_time': end_time,
            'base_rewards': base_rewards,
            "extra_rewards": extra_rewards,
            "action": action
        })

        # Construct the address
        address = self._get_address(jobId)

        header = TransactionHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            family_name="job",
            family_version="1.0",
            inputs=[address],
            outputs=[address],
            dependencies=[],
            payload_sha512=_sha512(payload),
            batcher_public_key=self._signer.get_public_key().as_hex(),
            nonce=hex(random.randint(0, 2**64))
        ).SerializeToString()

        signature = self._signer.sign(header)

        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=signature
        )

        batch_list = self._create_batch_list([transaction])
        batch_id = batch_list.batches[0].header_signature

        if wait and wait > 0:
            wait_time = 0
            begin_time = time.time()
            response = self._send_request(
                "batches", batch_list.SerializeToString(),
                'application/octet-stream'
                )
            while wait_time < wait:
                status = self._get_status(
                    batch_id,
                    wait - int(wait_time)
                    )
                wait_time = time.time() - begin_time

                if status != 'PENDING':
                    return response

            return response

        return self._send_request(
            "batches", batch_list.SerializeToString(),
            'application/octet-stream',
            )

    def _create_batch_list(self, transactions):
        transaction_signatures = [t.header_signature for t in transactions]

        header = BatchHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            transaction_ids=transaction_signatures
        ).SerializeToString()

        signature = self._signer.sign(header)

        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature)
        return BatchList(batches=[batch])
