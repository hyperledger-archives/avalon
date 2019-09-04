/* Copyright 2019 iExec Blockchain Tech
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

#include <stdio.h>
#include <stdlib.h>
#include <iostream>
#include <sys/stat.h>
#include <assert.h>
#include <dirent.h>
#include <string.h>
#include <limits.h>
#include "execution_logic.h"


/* read_file
*
*  reads a file into a buffer and returns the buffer
*  and returns the size in argument *size
*
*  returns NULL on error
*
*  expects the call to free the allocated buffer
*/

char* read_file(const char* filename, size_t* size)
{
    *size=-1;
    FILE *f = fopen(filename, "r");
    if (!f) {
        perror ("Error opening file for reading"); 
        return NULL;
    }
    fseek(f, 0, SEEK_END);
    size_t fsize = ftell(f);
    fseek(f, 0, SEEK_SET);  //same as rewind(f);

    char *string = (char *)malloc(fsize + 1);
    if (string == NULL) {
        fprintf(stderr, "cannot allocate sufficient memory '%ld' for file '%s'\n", fsize, filename);
        fclose(f);
        return NULL;
    }
    size_t sz = fread(string, fsize, 1, f);
    if (sz != 1) {
        fprintf(stderr, "reading file '%s': expected %zu bytes but only got %zu\n", filename, fsize, sz);
        free (string);
        fclose(f);
        return NULL;
    }

    fclose(f);
    string[fsize] = 0;
    *size=fsize;
    return string;
}

/* write_file
*
*  writes a file passed in as a buffer with a given size
*
*  returns 0 on error
*
*  frees the buffer unless an error occurred
*/

int write_file(const char* filename, const char* data)
{
    FILE *f = fopen(filename, "w");
    if (!f) { 
        return -1;
    }
    fputs(data, f);
    fclose(f);
    return 0;
}

/*
*  token_validation
*
*  returns 0 on error
*  returns 1 on success
*/
int token_validation(const char* inputfile, const char* outputfile) {
    size_t size = 0;
    char* buffer;

    /* read the input file */
    buffer = read_file(inputfile, &size);
    if (!buffer) {
        return -1;
    }
    std::string input(buffer);

    // Run EEA token execution logic
    std::string result = token_valid_procedure(input);
    free (buffer);
    // save the results
    char* outputString = new char [result.length() + 1];
    strcpy (outputString, result.c_str());
     if (write_file(outputfile, outputString) != 0) {
        return -1;
    }   

    return 0;
}

/*
*  checkAllInputFiles
*
*  check all input files
*/

static int checkAllInputFiles(char* curpath, char* const path, const char* prefix, int index) {
        char ep[PATH_MAX];
        char p[PATH_MAX];
        char to[PATH_MAX];
        DIR *dirp;
        struct dirent entry;
        struct dirent *endp;
        struct stat st;

        if (curpath != NULL)
                snprintf(ep, sizeof(ep), "%s/%s", curpath, path);
        else
                snprintf(ep, sizeof(ep), "%s", path);
        if (stat(ep, &st) == -1)
                return -1;
        if ((dirp = opendir(ep)) == NULL)
                return -1;
        for (;;) {
                endp = NULL;
                if (readdir_r(dirp, &entry, &endp) == -1) {
                        closedir(dirp);
                        return -1;
                }
                if (endp == NULL)
                        break;
                assert(endp == &entry);
                if (strcmp(entry.d_name, ".") == 0 ||
                    strcmp(entry.d_name, "..") == 0)
                        continue;
                if (curpath != NULL)
                        snprintf(ep, sizeof(ep), "%s/%s/%s", curpath,
                            path, entry.d_name);
                else
                        snprintf(ep, sizeof(ep), "%s/%s", path,
                            entry.d_name);
                if (stat(ep, &st) == -1) {
                        closedir(dirp);
                        return -1;
                }
                if (S_ISREG(st.st_mode)) {
                    if (strcmp(entry.d_name, "volume.fspf") != 0) {
                        ep[sizeof(ep)-1]=0;
                        snprintf(to, sizeof(to), "%s/%s", prefix, "output");
                        printf("from file %s to %s\n", ep, to);
                        if (! token_validation(ep, to)) {
                            printf("Error in token_validation\n");
                            exit(1);
                        }
                    }
                }
                if (S_ISDIR(st.st_mode) == 0)
                        continue;
                if (curpath != NULL)
                        snprintf(p, sizeof(p), "%s/%s", curpath, path);
                else
                        snprintf(p, sizeof(p), "%s", path);
                snprintf(ep, sizeof(ep), "%s", entry.d_name);
                checkAllInputFiles(p, ep, prefix, index);
        }
        closedir(dirp);
        return 0;
}

/*
* Copies files from directory  "/encryptedInputs" to "/encryptedOutputs"
*
* note that the files in "/encryptedInputs" will be transparently decrypted by SCONE
* note that the files in "/encryptedOutputs" will be transparently encrypted by SCONE
*/

int main(int argc, char** argv) {
    //TEST
    // token_validation("test/token_request","test/output");

    /* This is for transparent encryption and decryption for Scone secure container */
    printf("%s: # arguments = %d", argv[0], argc);
    for (int i = 1 ; i < argc ; ++i)
        printf("   argument %d: %s", i, argv[i]);
    checkAllInputFiles(NULL, "/encryptedInputs", "/encryptedOutputs", strlen("/encryptedInputs/"));
    /**********************************************************************************/
}
