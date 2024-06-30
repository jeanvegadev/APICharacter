# APICharacter
API for character table

#  Choose  a method to deploy the api

1. Deploy Using Docker
2. Deploy Using Virtual Environment in Windows

## 1. Deploy Using Docker

Use the docker build command to create an image from your Dockerfile.

```sh
docker build -t character-api .
```

Use the docker run command to start a container from your image.

```sh
docker run -d -p 5000:5000 character-api
```

## 2. Deploy Using Virtual Environment in Windows

Activate the virtual environment

```sh
venv\Scripts\activate
```

Run the app.py

```py
python app.py
```

# Documentation

The API documentation is generated using Swagger.

## Offline Documentation

- **File:** `api-documentation.pdf`
- **Location:** `docs` folder

You can find detailed offline documentation in the `api-documentation.pdf` file located within the `docs` folder.

## Online Documentation

- **URL:** `/`

Once the API is running, you can access the online Swagger documentation by navigating to the root path (`/`) in your browser.

---