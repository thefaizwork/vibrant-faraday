"""
Security and Sandboxing utilities for rendering generated web code.
"""

from typing import Dict


class SandboxSecurity:
    # Content Security Policy preventing external data exfiltration or arbitrary remote script execution
    CSP_HEADER_VALUE = (
        "default-src 'self' 'unsafe-inline' data:; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' data: https://fonts.gstatic.com; "
        "img-src 'self' data: https:; "
        "connect-src 'self'; "
        "frame-ancestors 'self';"
    )

    @classmethod
    def get_security_headers(cls) -> Dict[str, str]:
        return {
            "Content-Security-Policy": cls.CSP_HEADER_VALUE,
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "Referrer-Policy": "no-referrer",
        }

    @classmethod
    def sanitize_preview_html(cls, html: str) -> str:
        """
        Injects a protective meta CSP tag into the HTML head if not already present.
        """
        csp_meta = f'<meta http-equiv="Content-Security-Policy" content="{cls.CSP_HEADER_VALUE}">'
        if "<head>" in html:
            return html.replace("<head>", f"<head>\n  {csp_meta}")
        elif "<HEAD>" in html:
            return html.replace("<HEAD>", f"<HEAD>\n  {csp_meta}")
        return f"{csp_meta}\n{html}"
