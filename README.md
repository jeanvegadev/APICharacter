# APICharacter
API for character table


## Using Docker

Use the docker build command to create an image from your Dockerfile.

```sh
docker build -t character-api .
```

Use the docker run command to start a container from your image.

```sh
docker run -d -p 5000:5000 character-api
```