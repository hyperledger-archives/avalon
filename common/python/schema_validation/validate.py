# Copyright 2020 Intel Corporation
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
import pkg_resources
from jsonschema import validate, ValidationError, SchemaError


def schema_validation(method, params):
    """
    Validate params dictionary for existence of
    fields and mandatory fields

    Parameters:
    params    Parameter dictionary to validate

    Returns:
    True and empty string on success and
    False and string with error message on failure.
    """
    if len(params) == 0:
        return False, "Empty params in the request"

    schema = {}
    file_name = "data/" + method + ".json"

    data_file = pkg_resources.resource_string(__name__, file_name)
    schema = json.loads(data_file)
    try:
        validate(params, schema)
    except ValidationError as e:
        if e.validator == 'additionalProperties' or \
                e.validator == 'required':
            return False, e.message
        else:
            return False, e.schema["error_msg"]
    except SchemaError as err:
        return False, err.message
    except Exception as err:
        return False, str(err)

    return True, ""
