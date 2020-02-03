/* Copyright 2018 Intel Corporation
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

#include <assert.h>
#include <stdio.h>
#include <string.h>
//#include "tSgxSSL_api.h"
#include <pwd.h>
#include <unistd.h>
#define MAX_PATH FILENAME_MAX

#include "TestApp.h"
#include "TestEnclave_u.h"
#include "sgx_urts.h"
#include "c11_support.h"

/* Global EID shared by multiple threads */
sgx_enclave_id_t global_eid = 0;

typedef struct _sgx_errlist_t
{
    sgx_status_t err;
    const char* msg;
    const char* sug; /* Suggestion */
} sgx_errlist_t;

/* Error code returned by sgx_create_enclave */
static sgx_errlist_t sgx_errlist[] = {
    {SGX_ERROR_UNEXPECTED, "Unexpected error occurred.", NULL},
    {SGX_ERROR_INVALID_PARAMETER, "Invalid parameter.", NULL},
    {SGX_ERROR_OUT_OF_MEMORY, "Out of memory.", NULL},
    {SGX_ERROR_ENCLAVE_LOST, "Power transition occurred.",
     "Please refer to the sample \"PowerTransition\" for details."},
    {SGX_ERROR_INVALID_ENCLAVE, "Invalid enclave image.", NULL},
    {SGX_ERROR_INVALID_ENCLAVE_ID, "Invalid enclave identification.", NULL},
    {SGX_ERROR_INVALID_SIGNATURE, "Invalid enclave signature.", NULL},
    {SGX_ERROR_OUT_OF_EPC, "Out of EPC memory.", NULL},
    {SGX_ERROR_NO_DEVICE, "Invalid SGX device.",
     "Please make sure SGX module is enabled in the BIOS, and install SGX driver afterwards."},
    {SGX_ERROR_MEMORY_MAP_CONFLICT, "Memory map conflicted.", NULL},
    {SGX_ERROR_INVALID_METADATA, "Invalid enclave metadata.", NULL},
    {SGX_ERROR_DEVICE_BUSY, "SGX device was busy.", NULL},
    {SGX_ERROR_INVALID_VERSION, "Enclave version was invalid.", NULL},
    {SGX_ERROR_INVALID_ATTRIBUTE, "Enclave was not authorized.", NULL},
    {SGX_ERROR_ENCLAVE_FILE_ACCESS, "Can't open enclave file.", NULL},
};

/* Check error conditions for loading enclave */
void print_error_message(sgx_status_t ret)
{
    size_t idx = 0;
    size_t ttl = sizeof sgx_errlist / sizeof sgx_errlist[0];

    for (idx = 0; idx < ttl; idx++)
    {
        if (ret == sgx_errlist[idx].err)
        {
            if (NULL != sgx_errlist[idx].sug)
                printf("Info: %s\n", sgx_errlist[idx].sug);
            fprintf(stderr, "Error: %s\n", sgx_errlist[idx].msg);
            break;
        }
    }

    if (idx == ttl)
        fprintf(stderr,
            "Error code is 0x%X. Please refer to the \"Intel SGX SDK Developer Reference\" for "
            "more details.\n",
            ret);
}

/* Initialize the enclave:
 *   Step 1: try to retrieve the launch token saved by last transaction
 *   Step 2: call sgx_create_enclave to initialize an enclave instance
 *   Step 3: save the launch token if it is updated
 */
int initialize_enclave(void)
{
    char token_path[MAX_PATH] = {'\0'};
    sgx_launch_token_t token = {0};
    sgx_status_t ret = SGX_ERROR_UNEXPECTED;
    int updated = 0;

    /* Step 1: try to retrieve the launch token saved by last transaction
     *         if there is no token, then create a new one.
     */
    /* try to get the token saved in $HOME */
    const char* home_dir = getpwuid(getuid())->pw_dir;

    /* 1st 1 is length("/"), 2nd 1 is null terminator */
    if (home_dir != NULL &&
        (strnlen(home_dir, MAX_PATH) + 1 + sizeof(TOKEN_FILENAME) + 1) <= MAX_PATH)
    {
        /* compose the token path */
        strncpy_s(token_path, MAX_PATH, home_dir, strnlen(home_dir, MAX_PATH));
        strncpy_s(&token_path[strnlen_s(token_path, MAX_PATH-1)], MAX_PATH-1,
                  "/\0", 2); //Includes copying null
        strncpy_s(&token_path[strnlen_s(token_path, MAX_PATH-1)], MAX_PATH-1,
                  TOKEN_FILENAME, sizeof(TOKEN_FILENAME) + 1); // Includes copying null
    }
    else
    {
        /* if token path is too long or $HOME is NULL */
        strncpy_s(token_path, MAX_PATH, TOKEN_FILENAME, sizeof(TOKEN_FILENAME));
    }

    FILE* fp = fopen(token_path, "rb");
    if (fp != NULL)
    {
        /* read the token from saved file */
        size_t read_num = fread(token, 1, sizeof(sgx_launch_token_t), fp);
        if (read_num != 0 && read_num != sizeof(sgx_launch_token_t))
        {
            /* if token is invalid, clear the buffer */
            memset(&token, 0x0, sizeof(sgx_launch_token_t));
            fprintf(stderr, "Warning: Invalid launch token read from "
                "\"%s\".\n", token_path);
        }
    }
    else
    {
        /* create file since it does not exist */
        if ((fp = fopen(token_path, "wb")) == NULL)
        {
            fprintf(stderr, "Warning: Failed to create/open the launch token "
                " file \"%s\".\n", token_path);
        }
    }

    /* Step 2: call sgx_create_enclave to initialize an enclave instance */
    /* Debug Support: set 2nd parameter to 1 */
    ret = sgx_create_enclave(ENCLAVE_FILENAME, SGX_DEBUG_FLAG, &token, &updated, &global_eid, NULL);
    if (ret != SGX_SUCCESS)
    {
        print_error_message(ret);
        if (fp != NULL)
            fclose(fp);
        return -1;
    }

    /* Step 3: save the launch token if it is updated */
    if (updated == FALSE || fp == NULL)
    {
        /* if the token is not updated, or file handler is invalid, do not perform saving */
        if (fp != NULL)
            fclose(fp);
        return 0;
    }

    /* reopen the file with write capability */
    fp = freopen(token_path, "wb", fp);
    if (fp == NULL)
        return 0;
    size_t write_num = fwrite(token, 1, sizeof(sgx_launch_token_t), fp);
    if (write_num != sizeof(sgx_launch_token_t))
        fprintf(stderr, "Warning: Failed to save launch token to \"%s\".\n", token_path);
    fclose(fp);
    return 0;
}

/* OCall functions */
void ocall_print_string(const char* str)
{
    /* Proxy/Bridge will check the length and null-terminate
     * the input string to prevent buffer overflow.
     */
    printf("%s", str);
}

/* Application entry */
int SGX_CDECL main(int argc, char* argv[])
{
    (void)(argc);
    (void)(argv);

    int result;

    printf("Test TRUSTED Common API.\n");

    /* Initialize the enclave */
    if (initialize_enclave() < 0)
    {
        fprintf(stderr, "Error: could not initialize SGX Enclave\n");
        return -1;
    }

    test(global_eid, &result);
    /* Destroy the enclave */
    sgx_destroy_enclave(global_eid);

    if (result != 0)
    {
        fprintf(stderr, "ERROR: TRUSTED Common API test FAILED.\n");
        return -1;
    }

    printf("Test TRUSTED Common API SUCCESSFUL!\n");

    return 0;
}
