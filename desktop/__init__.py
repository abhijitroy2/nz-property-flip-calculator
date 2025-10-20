"""Desktop Batch Analyzer package.

This package provides a Windows-friendly batch runner that reuses the
existing analysis pipeline to generate periodic PDF reports and
optionally email them to recipients.
"""

__all__ = [
    "config",
    "runner",
    "scheduler",
    "pdf_renderer",
    "email_sender",
]


