## Simple catalog of registered trademarks

### Key features

- Register trademark
- Exact string search
- Fuzzy string search (using trigrams)

### Getting started

Prepare - create docker network
```shell
make create-network
```

To build a docker image for the backend API service run:

```shell
make build
```

Then you should be able to run a development setup with docker-compose:

```shell
make start
```

Also you should run the database migrations

```shell
make migrate
```

### API

#### Register a trademark

```
POST /trademark
```

Body params (json):

- `title` - string, trademark title
- `description` - string, trademark description
- `application_number` - string, trademark application number
- `registration_date` - date in ISO format, trademark registration date
- `expiry_date` - date in ISO format, expiry date

Response HTTP codes:
- `201` - Trademark registered successfully
- `400` - Invalid request
- `409` - Trademark with such name is already registered
- `500` - Internal server error

Response format - `json`:

- `result` - `trademark` object
    - `id` - string, unique identifier of trademark record
    - `title` - string, trademark title
    - `description` - string, trademark description
    - `application_number` - string, trademark application number
    - `registration_date` - date in ISO format, trademark registration date
    - `expiry_date` - date in ISO format, expiry date

Example:

```json
{
  "result": {
    "id": "7d92e944-899d-4c24-bc63-4bacc270f1ad",
    "title": "WAVE",
    "description": "blah",
    "application_number": "018188180",
    "registration_date": "2020-06-11",
    "expiry_date": "2030-01-28"
  }
}
```

#### Find a trademark by title

```
GET /trademark
```

Query params:

- `title` - string, trademark title to match with
- `exact_match` - boolean, search for an exact match (default is true)

Response HTTP codes:
- `200` - Success - trademark with given title has been found
- `400` - Invalid request
- `404` - Not found - no such trademark
- `500` - Internal server error

Response format - `json`:

- `result` - list of trademark objects
    - `id` - string, unique identifier of trademark record
    - `title` - string, trademark title
    - `description` - string, trademark description
    - `application_number` - string, trademark application number
    - `registration_date` - date in ISO format, trademark registration date
    - `expiry_date` - date in ISO format, expiry date

Example:

```json
{
  "result": [
    {
      "id": "66e01b8d-5df8-4ad7-a672-8d33f427f6cb",
      "title": "WATA WAVE",
      "description": "blah",
      "application_number": "018221920",
      "registration_date": "2020-07-22",
      "expiry_date": "2030-04-06"
    }
  ]
}
```
