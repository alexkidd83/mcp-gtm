"""MCP server for Google Tag Manager — Gate 1 read, Gate 2 write-capable."""

import os

__version__ = "0.1.0"

# Global read-only flag. When True, all write tools are blocked.
# Keep true by default; set GTM_MCP_READ_ONLY=false to allow Gate 2 writes.
_read_only: bool = os.environ.get("GTM_MCP_READ_ONLY", "true").strip().lower() not in {
    "0",
    "false",
    "no",
    "off",
}


def main() -> None:
    """CLI entry point — start the GTM MCP server."""
    from gtm_mcp.server import mcp

    mcp.run()
