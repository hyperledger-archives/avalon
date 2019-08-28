<!---
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
--->
# Building the common libraries

Make sure you have environment variables `SGX_SDK` and `SGX_SSL` defined
(see [BUILD.md](../../../BUILD.md)) and then run
```
mkdir build
cd build
cmake .. -G "Unix Makefiles" && make
```
