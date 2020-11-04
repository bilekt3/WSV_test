### Changes

- Removed write/read to YAML file as state (docker needs volume, and it cost money)
- Moved class parametrization into YAML file
- Simplified app layout (to single file)
- Added namespace `comap.azurecr.io/wsv` for Docker images to second stage (push to ComAp registry)

### Config

Configuration moved to file `config.local.json` (see `config.sample.json` for more details)

### Docker

Create reusable docker image

```shell script
docker build -f Dockerfile.base -t comap.azurecr.io/wsv/python-selenium:b001 .
``` 

Build app
```shell script
docker build -f Dockerfile -t comap.azurecr.io/wsv/wsv-testing:b001 .
````
 
Finally, run container
```shell script
# For testing
docker run --name wsv-testing  comap.azurecr.io/wsv/wsv-testing:b001
````

### Notes
- Please adjust docker files and build versions accordingly

