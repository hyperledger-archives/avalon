<!--
Licensed under Creative Commons Attribution 4.0 International License
https://creativecommons.org/licenses/by/4.0/
-->

# Santander AML DEMO SGX WEB CLIENT

## Compiles and hot-reloads for development
```
npm install
npm run serve
```

## Deployment in production


1. Go to **Project Root Folder**

2. Build Trusted Compute Framework using "docker-compose-aml-web-client.yaml"

```
docker-compose -f docker-compose-aml-web-client.yaml up
```

3. Go back to this folder (web-client)

4. Change variable "SERVER_URL" in file "src/config.js"

5. Change variable "server_name" in file "deployment/nginx.conf. It must be the same url than the specified in "config.js" file

6. Install dependencies executing in this folder

```
npm install
```

7. Compile for production executing in this folder

```
npm run build
```

8. Go to "deployment" folder.

9. Execute

```
docker-compose up
```

10. Open a browser and check if everything is deployed correctly. There must be some workers in "Available Workers" slot.
