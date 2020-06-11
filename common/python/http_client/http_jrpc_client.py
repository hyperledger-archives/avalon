# Copyright 2019 Intel Corporation
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

import json
import time
import urllib.request
import urllib.error

import logging
logger = logging.getLogger(__name__)


class MessageException(Exception):
    """
    A class to capture communication exceptions when communicating with
    services.
    """
    pass


class HttpJrpcClient(object):
    """
    Class to handle HTTP JSON RPC communication by the client.
    """

    def __init__(self, url):
        self.ServiceURL = url
        self.ProxyHandler = urllib.request.ProxyHandler({})

    def _postmsg(self, request, retries=0):
        """
        Post a request JSON RPC string and return the response.

        Parameters:
            @param request - JSON string request to post
            @param retries - Number of attempts to submit request
        """

        data = request.encode('utf8')
        datalen = len(data)

        url = self.ServiceURL

        logger.debug('post request to %s with DATALEN=%d, DATA=<%s>',
                     url, datalen, data)

        try:
            request = urllib.request.Request(
                url, data,
                {'Content-Type': 'application/json',
                 'Content-Length': datalen})
            opener = urllib.request.build_opener(self.ProxyHandler)
            response = self._open_with_retries(
                opener, request, retries)

        except urllib.error.HTTPError as err:
            logger.warn('operation failed with response: %s', err.code)
            raise MessageException(
                'operation failed with response: {0}'.format(err.code))

        except urllib.error.URLError as err:
            logger.warn('operation failed: %s', err.reason)
            raise MessageException('operation failed: {0}'.format(err.reason))

        except Exception as err:
            logger.exception('no response from server: %s', str(err))
            raise MessageException('no response from server: {0}'.format(err))

        content = response.read()
        headers = response.info()
        response.close()

        encoding = headers.get('Content-Type')
        if encoding != 'application/json':
            logger.info('server responds with message %s of type %s',
                        content, encoding)
            return None

        # Attempt to decode the content if it is not already a string
        try:
            content = content.decode('utf-8')
        except AttributeError:
            pass
        value = json.loads(content)
        return value

    def _open_with_retries(self, opener, request, retries):
        """
        Function to retry opening a given url/request if URLError is
        encountered. URLError for request would encompass HTTPError
        as well as Timeout.

        Parameters:
            @param opener - An instance of OpenerDiretor
            @param request - Request to be sent to the url
            @param retries - Number of attempts to open
        Returns:
            @returns response - Response received
        """
        count = 0
        while count < retries:
            try:
                return opener.open(request, timeout=10)
            except urllib.error.URLError as err:
                logger.error("Connection error - %s", err.reason)
                time.sleep(10)
            except Exception as err:
                raise err
            # Increment counter for each handled Exception
            count += 1
            if count < retries:
                logger.info("Will retry to connect.")
        # Make a final call after retries are exhausted
        return opener.open(request, timeout=10)
