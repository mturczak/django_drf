
# Django REST Image Uploader

This is a Django project for an image uploader API using django-rest-framework. It includes a Django app called `Django_API` which contains models, serializers, views, and URLs for handling image uploads and retrieval. The project also includes a Dockerfile for containerization.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mturczak/django_drf.git
   cd django_drf
   ```

2. **Run Docker Compose**
   ```bash
   docker-compose up -d
   ```

The application should now be running at http://localhost:9000.

### Admin panel

Admin panel should be located in:
http://localhost:9000/admin

## Usage

The API allows you to upload images and retrieve them. It also generates thumbnails for uploaded images.

Browsing app is made with GET and POST request, i suggest using applications such Postman to browse API. Except for that, there is implemented admin panel, with default admin user(credentials: ```admin:admin```)
There is a possibility to create own super user using command:
    ```
    python migrate.py createsuperuser
    ```
While using these commands you need to authenticate yourself whilse sending request, i suggest to use builtin "Basic Auth", that are a part of API browse applications such as Postman.

API requests to use:

```POST http://localhost:9000/image/upload/``` - uploading an image, in body should be included field with key: image, and value: actual image. In Response included are:

- specified in tier thumbnails
- optional original image link 
- optional expire_link_example link

```GET http://localhost:9000/image/list/``` - getting the list of the user's image. In Response indluded are:

For all images:
- specified in tier thumbnails
- optional original image link
- optional expire_link_example link


