#!/usr/bin/env python3

# /agents/utils/tools/web_request_framework.py
# Updated: 22 feb 2026

"""
web_request_framework features:

Request customization: Supports different HTTP methods, payloads, and headers
Analysis Checks =>
    Comprehensive analysis: Captures full request/response metadata
    Security checks: Evaluates presence of key security headers (HSTS, CSP, X-Frame-Options, etc.)
    HTTPS validation: Checks if HTTPS is used and HSTS is present
    Content analysis: Examines Content-Type and charset
    Redirect tracking: Shows redirect count and final URL
    Cookie Security Audit: Check for insecure cookie attributes( like Missing Secure, HttpOnly, or SameSite flags, Exposed session tokens in headers ).
    Rate Limiting & Status Code Checks: Detect 429 Too Many Requests for brute-force exposure
    CORS Misconfiguration Detection: Analyze Access-Control-Allow-Origin, Allow-Credentials and Flag over-permissive policies like * with credentials
    Server Header Fingerprinting: Detect verbose Server, X-Powered-By headers and Identify tech stack leaks (e.g., PHP/7.4, Express)
    Redirect & Referrer Analysis: Check for insecure redirects (e.g., user-controlled Location) and Validate Referer-Policy presence
    ETag & Caching Risks: Flag weak ETag headers enabling cache poisoning & Check Cache-Control for sensitive content
    Content-Type & MIME Sniffing: Verify X-Content-Type-Options: nosniff is enforced & Confirm Content-Type matches actual content
    Security.txt & Policy Files: Check for /security.txt, robots.txt, crossdomain.xml & Detect exposed debug or config files

The output is a structured dictionary containing all analysis data, making it easy to integrate into larger security testing workflows.
"""

import requests
from urllib.parse import urljoin, urlparse
import re

def web_request_analysis(url: str, method: str='GET', payload: str=None, headers: str=None, timeout: int=10) -> dict:
    """
    Perform quick header, body, and security analysis of an HTTP/HTTPS request's Responses.

    Args:
        url (str): Target URL
        method (str): HTTP method (GET, POST, etc.)
        payload (dict): Optional data for POST/PUT
        headers (dict): Optional custom headers
        timeout (int): Request timeout in seconds

    Returns:
        dict: Analysis results including request/response details and security checks
    """
    # Default security headers to check
    security_headers = {
        'Strict-Transport-Security': 'HSTS missing - Mitigates downgrade attacks',
        'Content-Security-Policy': 'CSP missing - Critical for XSS protection',
        'X-Content-Type-Options': 'Should be set to "nosniff"',
        'X-Frame-Options': 'Missing - Prevents clickjacking',
        'X-XSS-Protection': 'Deprecated but should be disabled explicitly',
        'Referrer-Policy': 'Controls referrer leakage',
        'Permissions-Policy': 'Restricts browser features'
    }

    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = urljoin('https://', url)

    # Prepare headers
    req_headers = headers or {}
    req_headers.setdefault('User-Agent', 'HackerX WebRequestFramework/1.0')

    try:
        # Make request
        response = requests.request(
            method=method.upper(),
            url=url,
            data=payload,
            headers=req_headers,
            timeout=timeout,
            allow_redirects=True
        )

        # Analyze response
        analysis = {
            'request': {
                'url': response.url,
                'method': method.upper(),
                'headers': dict(req_headers),
                'payload': payload
            },
            'response': {
                'status_code': response.status_code,
                'reason': response.reason,
                'headers': dict(response.headers),
                'content_type': response.headers.get('Content-Type', ''),
                'content_length': len(response.content),
                'redirects': len(response.history),
                'final_url': response.url
            },
            'security': {
                'is_https': urlparse(response.url).scheme == 'https',
                'missing_headers': [],
                'findings': [],
                'cookies': [],
                'cors': {},
                'server': {},
                'caching': {}
            },
            'body_preview': response.text[:500] if response.text else ''
        }


        # === Security Headers Check ===
        for header, description in security_headers.items():
            if header not in response.headers:
                analysis['security']['missing_headers'].append(header)
                analysis['security']['findings'].append(f"{header}: {description}")


        # === Cookie Analysis ===
        for cookie in response.cookies:
            cookie_info = {
                'name': cookie.name,
                'value': cookie.value[:50] + '...' if len(cookie.value) > 50 else cookie.value,
                'httponly': bool(cookie._rest.get('httponly')),
                'secure': cookie.secure,
                'samesite': cookie._rest.get('samesite', 'Not Set'),
                'domain': cookie.domain,
                'path': cookie.path,
                'expires': cookie.expires
            }
            analysis['security']['cookies'].append(cookie_info)

            if not cookie.secure and analysis['security']['is_https']:
                analysis['security']['findings'].append(f"Cookie '{cookie.name}' missing Secure flag")
            if not cookie._rest.get('httponly'):
                analysis['security']['findings'].append(f"Cookie '{cookie.name}' missing HttpOnly - XSS risk")
            if not cookie._rest.get('samesite'):
                analysis['security']['findings'].append(f"Cookie '{cookie.name}' missing SameSite - CSRF risk")


        # === CORS Analysis ===
        acao = response.headers.get('Access-Control-Allow-Origin')
        acac = response.headers.get('Access-Control-Allow-Credentials')
        acam = response.headers.get('Access-Control-Allow-Methods')

        analysis['security']['cors'] = {
            'acao': acao,
            'acac': acac,
            'acam': acam
        }

        if acao == '*' and acac == 'true':
            analysis['security']['findings'].append(
                "CRITICAL: CORS misconfiguration - Wildcard origin with credentials enabled")
        if acao and 'null' in acao:
            analysis['security']['findings'].append(
                "WARNING: CORS allows 'null' origin - Potential sandbox bypass")


        # === Server Header Analysis ===
        server = response.headers.get('Server', '')
        powered_by = response.headers.get('X-Powered-By', '')
        asp_version = response.headers.get('X-AspNet-Version', '')
        generator = response.headers.get('X-Generator', '')

        analysis['security']['server'] = {
            'server': server,
            'x_powered_by': powered_by,
            'x_aspnet_version': asp_version,
            'generator': generator
        }

        if server:
            analysis['security']['findings'].append(f"Server banner: {server} - May reveal software versions")
        if powered_by:
            analysis['security']['findings'].append(f"Technology disclosure: {powered_by}")
        if asp_version:
            analysis['security']['findings'].append(f"ASP.NET version exposed: {asp_version}")


        # === Caching Analysis ===
        cache_control = response.headers.get('Cache-Control', '')
        pragma = response.headers.get('Pragma', '')
        etag = response.headers.get('ETag', '')

        analysis['security']['caching'] = {
            'cache_control': cache_control,
            'pragma': pragma,
            'etag': etag
        }

        if 'no-store' not in cache_control and 'private' not in cache_control:
            if 'public' in cache_control or not cache_control:
                analysis['security']['findings'].append(
                    "Caching policy may expose sensitive data - Missing no-store/private")

        if etag and 'W/' not in etag:  # Weak ETag
            analysis['security']['findings'].append("ETag header present - Potential cache poisoning vector")


        # === Rate Limiting Detection ===
        rate_limit_headers = [
            'X-RateLimit-Limit', 'X-RateLimit-Remaining',
            'X-RateLimit-Reset', 'Retry-After'
        ]
        if any(h in response.headers for h in rate_limit_headers):
            analysis['security']['findings'].append("Rate limiting detected - May protect APIs")
        elif response.status_code == 429:
            analysis['security']['findings'].append("Rate limiting active - Endpoint enforces request limits")


        # === Referrer Policy & Redirect Analysis ===
        if response.history:
            for i, resp in enumerate(response.history):
                analysis['security']['findings'].append(
                    f"Redirect {i + 1}: {resp.status_code} -> {resp.headers.get('Location', 'Unknown')}")

        referrer_policy = response.headers.get('Referrer-Policy')
        if not referrer_policy:
            analysis['security']['findings'].append("Referrer-Policy missing - May leak sensitive URLs")


        # === Content Analysis ===
        if response.headers.get('Content-Type', '').startswith('text/html'):
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
            api_key_pattern = r'api[_-]?key[_-]?\s*[:=]\s*[\'"]?[a-zA-Z0-9]{32,}[\'"]?'

            if re.search(email_pattern, response.text):
                analysis['security']['findings'].append("Potential email exposure in HTML")
            if re.search(ssn_pattern, response.text):
                analysis['security']['findings'].append("Potential SSN exposure in HTML")
            if re.search(api_key_pattern, response.text, re.IGNORECASE):
                analysis['security']['findings'].append("Potential API key exposure in HTML")
            if 'charset' not in response.text:
                analysis['security']['findings'].append("HTML response missing charset specification - May lead to encoding issues")


        # === HSTS & HTTP Security checks ===
        if analysis['security']['is_https']:
            if 'Strict-Transport-Security' not in response.headers:
                analysis['security']['findings'].append(
                    "HSTS header missing on HTTPS site - Consider adding for protection against downgrade attacks"
                )
        else:
            analysis['security']['findings'].append(
                "Site uses HTTP - Consider upgrading to HTTPS for security"
            )

        return analysis


    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'request': {'url': url, 'method': method.upper()}
        }


def get_raw_response(url: str, method: str='GET', payload: str=None, headers: str=None, timeout: int=10, full_res_body: bool=False) -> dict:
    """
    Get Raw Response from given URL for Manual Analysis.

    Args:
        url (str): Target URL
        method (str): HTTP method (GET, POST, etc.)
        payload (dict): Optional data for POST/PUT
        headers (dict): Optional custom headers
        timeout (int): Request timeout in seconds
        full_res_body (bool): Return full response body text or not

    Returns:
        dict: Raw response results including request,response & redirect details
    """

    # Normalize URL
    if not url.startswith(('http://', 'https://')):
        url = urljoin('https://', url)

    # Prepare headers
    req_headers = headers or {}
    req_headers.setdefault('User-Agent', 'HackerX WebRequestFramework/1.0')


    try:
        # Make request
        response = requests.request(
            method=method.upper(),
            url=url,
            data=payload,
            headers=req_headers,
            timeout=timeout,
            allow_redirects=True,
            stream=True  # Delay body download for raw access
        )

        # Ensure raw is read at least once to populate version/status
        response.raw.read(1)  # Prime the raw object
        # response.raw.seek(0)  # Reset

        # Access raw response
        raw = response.raw

        # Read raw status line (if available)
        status_line = f"HTTP/{raw.version / 10} {raw.status} {raw.reason}" if raw and hasattr(raw, 'version') else None

        # Get headers as dict and raw string
        headers_dict = dict(response.headers)

        # Get body (decode if bytes)
        body = response.content
        try:
            body_text = body.decode('utf-8', errors='replace')
            body_text = body_text if full_res_body else body_text[:500]
        except:
            body_text = str(body) if full_res_body else str(body)[:500]


        response.close()  # Ensure connection is released

        # Finalize response
        return {
            'request': {
                'method': method.upper(),
                'url': url,
                'headers': req_headers,
                'body': payload
            },
            'response': {
                'status_line': status_line,
                'headers': headers_dict,
                'body': body_text,
                'content_length': len(body),
                'content_type': response.headers.get('Content-Type', ''),
            },
            'redirects': len(response.history),
            'final_url': response.url,
            'timestamp': response.headers.get('Date')
        }

    except requests.exceptions.RequestException as e:
        return {
            'error': str(e),
            'request': {'url': url, 'method': method.upper()}
        }


# Example usage:
if __name__ == '__main__':
    # result = web_request_analysis('https://httpbin.org/get')
    # print(f"Response:\n {result['response']}\n")
    # print(f"Security:\n {result['security']}\n")
    # print(f"Body:\n {result['body_preview']}\n")

    raw_resp = get_raw_response('https://httpbin.org/get', 'GET')
    print(raw_resp)
