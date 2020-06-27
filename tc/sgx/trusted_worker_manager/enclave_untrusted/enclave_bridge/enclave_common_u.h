/* Copyright 2020 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// this header file includes worker specific header file generated from edl files
// present in singleton or kme or wpe modules

#ifdef BUILD_SINGLETON
    #include "singleton_enclave_u.h"
#elif BUILD_KME
    #include "kme_enclave_u.h"
#elif BUILD_WPE
    #include "wpe_enclave_u.h"
#else
    #error Unknown enclave build argument
#endif

