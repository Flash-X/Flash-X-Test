"""
Minimalistic static site generator for FlashXTest Webview.

This package is intentionally self-contained and **does not** rely on the old
CGI-based implementation (as before), or any HTML template engines. Instead it
offers a tiny, modern Python 3 interface that turns a *target* FlashXTest output
directory (normally passed by `-vv` option to `flashxtest init`) into fully static
HTML pages which can be served by any HTTP server or simply opened in a browser.

Usage (from the repository root)::

    @ TODO

The resulting `output` folder will contain:

* `index.html`                    – the invocation lists.
* `invocations/<invocation>.html` - the list of builds in the <invocation>.
* `<site>/<invocation>/<build>`   - the details of the builds.
"""

from .generator import generate_flashx_testview
