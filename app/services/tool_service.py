import httpx
import time
from typing import Any, Dict
from app.models.tool import Tool
from app.schemas.tool import ToolExecuteResult


class ToolService:
    """Service for executing tools (functions, webhooks, APIs, MCP)"""
    
    async def execute_tool(self, tool: Tool, parameters: Dict[str, Any]) -> ToolExecuteResult:
        """Execute a tool based on its type"""
        start_time = time.time()
        
        try:
            if tool.type == "function":
                return await self._execute_function(tool, parameters, start_time)
            elif tool.type == "webhook":
                return await self._execute_webhook(tool, parameters, start_time)
            elif tool.type == "api":
                return await self._execute_api(tool, parameters, start_time)
            elif tool.type == "mcp":
                return await self._execute_mcp(tool, parameters, start_time)
            else:
                return ToolExecuteResult(
                    success=False,
                    error=f"Unknown tool type: {tool.type}",
                    execution_time=time.time() - start_time
                )
        except Exception as e:
            return ToolExecuteResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    async def _execute_function(self, tool: Tool, parameters: Dict[str, Any], start_time: float) -> ToolExecuteResult:
        """Execute a custom function tool"""
        # Custom function logic can be added here
        # For now, return a placeholder response
        return ToolExecuteResult(
            success=True,
            result={"message": f"Function {tool.name} executed", "parameters": parameters},
            execution_time=time.time() - start_time
        )
    
    async def _execute_webhook(self, tool: Tool, parameters: Dict[str, Any], start_time: float) -> ToolExecuteResult:
        """Execute a webhook tool"""
        config = tool.config or {}
        url = config.get("url")
        method = config.get("method", "POST")
        headers = config.get("headers", {})
        
        if not url:
            return ToolExecuteResult(
                success=False,
                error="Webhook URL not configured",
                execution_time=time.time() - start_time
            )
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "POST":
                response = await client.post(url, json=parameters, headers=headers, timeout=30)
            elif method.upper() == "GET":
                response = await client.get(url, params=parameters, headers=headers, timeout=30)
            else:
                return ToolExecuteResult(
                    success=False,
                    error=f"Unsupported HTTP method: {method}",
                    execution_time=time.time() - start_time
                )
            
            try:
                result = response.json()
            except:
                result = {"status_code": response.status_code, "body": response.text}
            
            return ToolExecuteResult(
                success=response.status_code < 400,
                result=result,
                execution_time=time.time() - start_time
            )
    
    async def _execute_api(self, tool: Tool, parameters: Dict[str, Any], start_time: float) -> ToolExecuteResult:
        """Execute an API call tool"""
        config = tool.config or {}
        url = config.get("url")
        method = config.get("method", "GET")
        auth = config.get("auth")  # {type: "bearer", token: "..."} or {type: "api_key", key: "..."}
        
        if not url:
            return ToolExecuteResult(
                success=False,
                error="API URL not configured",
                execution_time=time.time() - start_time
            )
        
        headers = {}
        if auth:
            if auth.get("type") == "bearer":
                headers["Authorization"] = f"Bearer {auth.get('token')}"
            elif auth.get("type") == "api_key":
                headers["X-API-Key"] = auth.get("key")
        
        # Add custom headers from config
        headers.update(config.get("headers", {}))
        
        async with httpx.AsyncClient() as client:
            if method.upper() == "POST":
                response = await client.post(url, json=parameters, headers=headers, timeout=30)
            elif method.upper() == "GET":
                response = await client.get(url, params=parameters, headers=headers, timeout=30)
            elif method.upper() == "PUT":
                response = await client.put(url, json=parameters, headers=headers, timeout=30)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=headers, timeout=30)
            else:
                return ToolExecuteResult(
                    success=False,
                    error=f"Unsupported HTTP method: {method}",
                    execution_time=time.time() - start_time
                )
            
            try:
                result = response.json()
            except:
                result = {"status_code": response.status_code, "body": response.text}
            
            return ToolExecuteResult(
                success=response.status_code < 400,
                result=result,
                execution_time=time.time() - start_time
            )
    
    async def _execute_mcp(self, tool: Tool, parameters: Dict[str, Any], start_time: float) -> ToolExecuteResult:
        """Execute an MCP tool"""
        config = tool.config or {}
        mcp_server = tool.mcp_server or config.get("server_url")
        
        if not mcp_server:
            return ToolExecuteResult(
                success=False,
                error="MCP server URL not configured",
                execution_time=time.time() - start_time
            )
        
        # MCP protocol implementation
        # This would connect to an MCP server and call the specified tool
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool.name,
                "arguments": parameters
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                mcp_server,
                json=mcp_request,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return ToolExecuteResult(
                    success=True,
                    result=data.get("result"),
                    execution_time=time.time() - start_time
                )
            else:
                return ToolExecuteResult(
                    success=False,
                    error=f"MCP server error: {response.status_code}",
                    execution_time=time.time() - start_time
                )
