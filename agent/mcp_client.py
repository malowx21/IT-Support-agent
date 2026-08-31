import sys
from langchain_mcp_adapters.client import MultiServerMCPClient


def create_mcp_client():
    return MultiServerMCPClient({
        "support-server":{
            "command":sys.executable,
            "args":["-m","mcp_server.server"],
            "transport":"stdio"}        }
    )
