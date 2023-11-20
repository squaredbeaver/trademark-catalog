from enum import IntEnum


class HttpCode(IntEnum):
    ok = 200
    created = 201
    bad_request = 400
    not_found = 404
    conflict = 409
    internal_error = 500
