

import os, datetime, hashlib, hmac
from urllib.parse import urlencode, quote
import json

import boto3
import requests

class NoRegionError(Exception):
    pass

def send_request_with_v4_signature(method: str, base_url: str, request_parameters: dict):

    # Key derivation functions. See:
    # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def getSignatureKey(key, dateStamp, regionName, serviceName):
        kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = sign(kDate, regionName)
        kService = sign(kRegion, serviceName)
        kSigning = sign(kService, 'aws4_request')
        return kSigning

    # ************* REQUEST VALUES *************
    method = method
    service = 'execute-api'
    host = base_url.split('//')[1].split('/')[0] # base url with no https:// or /stage/endpoint eg. 3jcsohz7af.execute-api.us-west-2.amazonaws.com
    region = os.getenv('AWS_REGION')
    if region is None:
        raise NoRegionError
    endpoint = base_url # full base url with stage and endpoint path eg. https://3jcsohz7af.execute-api.us-west-2.amazonaws.com/staging/view/results/atc
    content_type = None
    amz_target = ''

    if method == 'POST':
        # POST requests use a content type header. For DynamoDB,
        # the content is JSON.
        content_type = 'application/x-amz-json-1.0'
        if type(request_parameters) is dict:
            request_parameters = json.dumps(request_parameters)

    # Read AWS access key from env. variables or configuration file. Best practice is NOT
    # to embed credentials in code.
    session = boto3.Session()
    credentials = session.get_credentials()
    access_key = credentials.access_key
    secret_key = credentials.secret_key

    # Create a date for headers and the credential string
    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope

    # ************* TASK 1: CREATE A CANONICAL REQUEST *************
    # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

    # Step 1 is to define the verb (GET, POST, etc.)--already done.

    # Step 2: Create canonical URI--the part of the URI from domain to query
    # string (use '/' if no path)
    canonical_uri = f"/{'/'.join(base_url.split('//')[1].split('/')[1:])}"
    print(f"canonical_uri: {canonical_uri}")

    # Step 3: Create the canonical query string. In this example (a GET request),
    # request parameters are in the query string. Query string values must
    # be URL-encoded (space=%20). The parameters must be sorted by name.
    # For this example, the query string is pre-formatted in the request_parameters variable.
    canonical_querystring = ''
    if method == 'GET':
        canonical_querystring = urlencode(request_parameters, encoding='utf-8', quote_via=quote)
        print(f"canonical_querystring: {canonical_querystring}")

    # Step 4: Create the canonical headers and signed headers. Header names
    # must be trimmed and lowercase, and sorted in code point order from
    # low to high. Note that there is a trailing \n.
    if method == 'GET':
        canonical_headers = 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n'
        print(f"canonical_header: {canonical_headers}")
    else:
        canonical_headers = 'content-type:' + content_type + '\n' + 'host:' + host + '\n' + 'x-amz-date:' + amzdate + '\n' + 'x-amz-target:' + amz_target + '\n'
        print(f"canonical_header: {canonical_headers}")

    # Step 5: Create the list of signed headers. This lists the headers
    # in the canonical_headers list, delimited with ";" and in alpha order.
    # Note: The request can include any headers; canonical_headers and
    # signed_headers lists those that you want to be included in the
    # hash of the request. "Host" and "x-amz-date" are always required.
    if method == 'GET':
        signed_headers = 'host;x-amz-date'
        print(f"signed_headers: {signed_headers}")
    else:
        signed_headers = 'content-type;host;x-amz-date;x-amz-target'
        print(f"signed_headers: {signed_headers}")

    # Step 6: Create payload hash (hash of the request body content). For GET
    # requests, the payload is an empty string ("").
    if method == 'GET':
        payload_hash = hashlib.sha256(('').encode('utf-8')).hexdigest()
        print(f"payload_hash: {payload_hash}")
    else:
        payload_hash = hashlib.sha256(request_parameters.encode('utf-8')).hexdigest()
        print(f"payload_hash: {payload_hash}")

    # Step 7: Combine elements to create canonical request
    canonical_request = method + '\n' + canonical_uri + '\n' + canonical_querystring + '\n' + canonical_headers + '\n' + signed_headers + '\n' + payload_hash
    print(f"canonical_request: {canonical_request}")

    # ************* TASK 2: CREATE THE STRING TO SIGN*************
    # Match the algorithm to the hashing algorithm you use, either SHA-1 or
    # SHA-256 (recommended)
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
    print(f"canonical_scope: {credential_scope}")
    string_to_sign = algorithm + '\n' + amzdate + '\n' + credential_scope + '\n' + hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    print(f"string to sign: {string_to_sign}")

    # ************* TASK 3: CALCULATE THE SIGNATURE *************
    # Create the signing key using the function defined above.
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    print(f"signing_key: {signing_key}")

    # Sign the string_to_sign using the signing_key
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
    print(f"signature: {signature}")

    # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
    # The signing information can be either in a query string value or in
    # a header named Authorization. This code shows how to use a header.
    # Create authorization header and add to request headers
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature
    print(f"auth_header: {authorization_header}")

    # The request can include any headers, but MUST include "host", "x-amz-date",
    # and (for this scenario) "Authorization". "host" and "x-amz-date" must
    # be included in the canonical_headers and signed_headers, as noted
    # earlier. Order here is not significant.
    # Python note: The 'host' header is added automatically by the Python 'requests' library.
    if method == 'GET':
        headers = {'x-amz-date': amzdate,
                   'Authorization': authorization_header}
    else:
        headers = {'Content-Type': content_type,
                   'X-Amz-Date': amzdate,
                   'X-Amz-Target': amz_target,
                   'Authorization': authorization_header}

    if method == 'GET':
        # ************* SEND GET REQUEST *************
        request_url = endpoint + '?' + canonical_querystring
        # r = requests.get(request_url, headers=headers)
        return request_url, headers
    else:
        # ************* SEND POST REQUEST *************
        # r = requests.post(endpoint, data=request_parameters, headers=headers)
        return endpoint, request_parameters, headers
