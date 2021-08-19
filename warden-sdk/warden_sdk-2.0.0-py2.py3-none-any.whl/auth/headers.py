"""Security headers for requests and responses in http calls.

This module contains all functions necessary to check an http call (in this case Flask requests) for security and to secure a response by adding necessary headers and validating the content being sent back.
"""
import requests
import tldextract
import json

from typing import (Any)


def add_secure_headers(response: dict, **kwargs: dict) -> dict:
   """
   Security headers is used after the request function in flask to append security headers necessary to prevent various attacks, mainly man-in-the-middle (MITM). The headers appended are as::

      - Strict Transport Security: Tells the browser to convert all HTTP requests to HTTPS, preventing man-in-the-middle (MITM) attacks.

      - Content Security Policy: Tell the browser where it can load various types of resource from. This header should be used whenever possible, but requires some work to define the correct policy for your site. A very strict policy.

      - X Content Type Options: Forces the browser to honor the response content type instead of trying to detect it, which can be abused to generate a cross-site scripting (XSS) attack.

      - X Frame Options: Prevents external sites from embedding your site in an iframe. This prevents a class of attacks where clicks in the outer frame can be translated invisibly to clicks on your page’s elements. This is also known as "clickjacking".

      - X XSS Protection: The browser will try to prevent reflected XSS attacks by not loading the page if the request contains something that looks like JavaScript and the response contains the same data.

   Args::
      response (dict): Response object from flask before being sent to requester.

   Returns::
      dict: Contains response object with appended security headers.
   """
   # Tells the browser to convert all HTTP requests to HTTPS, preventing man-in-the-middle (MITM) attacks.
   response.headers[
       'Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

   # Tell the browser where it can load various types of resource from. This header should be used whenever possible, but requires some work to define the correct policy for your site. A very strict policy.
   response.headers['Content-Security-Policy'] = "default-src 'self'"

   # Forces the browser to honor the response content type instead of trying to detect it, which can be abused to generate a cross-site scripting (XSS) attack.
   response.headers['X-Content-Type-Options'] = 'nosniff'

   # Prevents external sites from embedding your site in an iframe. This prevents a class of attacks where clicks in the outer frame can be translated invisibly to clicks on your page’s elements. This is also known as "clickjacking".
   response.headers['X-Frame-Options'] = 'SAMEORIGIN'

   # The browser will try to prevent reflected XSS attacks by not loading the page if the request contains something that looks like JavaScript and the response contains the same data. LEGACY
   response.headers['X-XSS-Protection'] = '1; mode=block'

   return response


def check_ssl_cert(request: Any) -> None:
   """
      Check Request checks whether the requester is safe by validating key headers and if asked through a HTTPS protocol. If not disabled, Warden checks if the requester has an Authorization header and sends that token to be checked by the Warden API.

      Args::
         request (dict): Request object from flask with all information to check if the requester is valid and safe.

      Raises::

      """
   criteria: list = [
       request.is_secure,
       request.headers.get('X-Forwarded-Proto', 'http') == 'https'
   ]

   # If any are true, continue
   # In the future, this should be all()
   if any(criteria):
      return

   raise Exception(
       'Unauthorized request. The client does not have access rights to the content.'
   )


def check_referrer(request: Any) -> None:
   """
   Check Referrer header from the requester and compare to the list of available headers for this particular API. If the Referrer is in the list of allowed referrers, proceed. Otherwise, raise an error.

   Args::
      - requester (Any): Request object from flask with all information to check if the requester is valid and safe

   Raises::
      - InvalidReferrer: Referrer origin does not match the acceptable referrers.
   """
   try:
      __referrer = request.headers.get('Referrer')
   except:
      raise Exception('Referrer header does not exist')

   __ext = tldextract.extract(__referrer)  # Extract all data from referrer

   if __ext.domain != 'ferant.io':  # Verify domain
      raise Exception('Invalid domain.')

   allowed_sub: list = ['api.clerk', 'api.warden', 'vault', 'edu']
   if not any(__ext.subdomain == sub for sub in allowed_sub):
      raise Exception('invalid_referrer')


def cors_list() -> list:
   """Get list of domains allowed to access the API based on the Client ID.

   Returns::
      list: List of domains allowed in CORS
   """
   raise NotImplementedError()

   resp: dict = requests.get('https://api.warden_sdk.ferant.io/oauth2/v1/cors',)
   resp = json.loads(resp.text)

   return resp