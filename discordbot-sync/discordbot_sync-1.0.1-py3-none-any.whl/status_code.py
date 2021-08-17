# http
ok = 200
created = 201
no_content = 204
not_modified = 304
bad_request = 400
unauthorized = 401
forbidden = 403
not_found = 404
method_not_allowed = 405
too_many_requests = 429
gateway_unavailable = 502

http_success = [
    ok,
    created,
    no_content,
    not_modified
]

http_bad_request = [
    bad_request,
    not_found,
    method_not_allowed
]

http_insufficient_permissions = [
    unauthorized,
    forbidden
]

http_try_later = [
    too_many_requests,
    gateway_unavailable
]