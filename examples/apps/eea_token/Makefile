# Copyright 2019 iExec Blockchain Tech
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

token_validation: token_validation.cpp execution_logic.cpp
	g++ -Wall -Wno-write-strings token_validation.cpp execution_logic.cpp -o token_validation -I.

.PHONY: clean
clean :
	-rm -rf token_validation
