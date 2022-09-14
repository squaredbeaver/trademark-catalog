## Simple exact/fuzzy search engine for registered trademarks

### Key features

- Exact string search
- Fuzzy string search (using trigrams)

### Getting started

First, you should build a docker image for the backend API service:

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

and populate the database with data

```shell
make load-data LOAD_DATA_FROM=/path/to/directory/with/xml/files
```

### API

#### Find a trademark with an exactly matching title

```
GET /find-exact-trademark
```

Query params:

- `title` - string, trademark title to match with

Response HTTP codes:
- `200` - Success - trademark with given title has been found
- `400` - Invalid request
- `404` - Not found - no such trademark
- `500` - Internal server error

Response format - `json`:

- `trademark`
    - `id` - string, unique identifier of trademark record
    - `title` - string, trademark title
    - `application_number` - string, trademark application number
    - `registration_date` - date in ISO format, trademark registration date
    - `expiry_date` - date in ISO format, expiry date

Example:

```json
{
  "trademark": {
    "id": "66e01b8d-5df8-4ad7-a672-8d33f427f6cb",
    "title": "WATA WAVE",
    "application_number": "018221920",
    "registration_date": "2020-07-22",
    "expiry_date": "2030-04-06"
  }
}
```

#### Find trademarks with similar titles

```
GET /find-similar-trademarks
```

Query params:

- `title` - string, trademark title to fuzzy-match with

Response HTTP codes:
- `200` - Success
- `400` - Invalid request
- `500` - Internal server error

Response format - `json`:

- `trademarks` - list of `trademark` objects, like in `/find-exact-trademark` request
    - `id` - string, unique identifier of trademark record
    - `title` - string, trademark title
    - `application_number` - string, trademark application number
    - `registration_date` - date in ISO format, trademark registration date
    - `expiry_date` - date in ISO format, expiry date

Example:

```json
{
  "trademarks": [
    {
      "id": "7d92e944-899d-4c24-bc63-4bacc270f1ad",
      "title": "WAVE",
      "application_number": "018188180",
      "registration_date": "2020-06-11",
      "expiry_date": "2030-01-28"
    },
    {
      "id": "66e01b8d-5df8-4ad7-a672-8d33f427f6cb",
      "title": "WATA WAVE",
      "application_number": "018221920",
      "registration_date": "2020-07-22",
      "expiry_date": "2030-04-06"
    }
  ]
}
```
