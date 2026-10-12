import json
from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

GITHUB_API_BASE = "https://api.github.com"


class ListIssuesTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        # 1. 读取凭证（用户配置的 GitHub Token）
        credentials = self.runtime.credentials
        token = credentials.get("github_token")
        if not token:
            yield self.create_text_message(
                "Error: GitHub token is not configured. "
                "Please set it in the plugin credentials."
            )
            return

        # 2. 读取参数
        owner = tool_parameters.get("owner", "").strip()
        repo = tool_parameters.get("repo", "").strip()
        state = tool_parameters.get("state", "open")
        per_page = tool_parameters.get("per_page", 10)

        if not owner or not repo:
            yield self.create_text_message(
                "Error: Both 'owner' and 'repo' are required."
            )
            return

        # 3. 构造请求
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        params = {
            "state": state,
            "per_page": per_page,
            "sort": "created",
            "direction": "desc",
        }

        try:
            resp = requests.get(
                f"{GITHUB_API_BASE}/repos/{owner}/{repo}/issues",
                headers=headers,
                params=params,
                timeout=15,
            )

            # 4. 处理各种错误状态码
            if resp.status_code == 404:
                yield self.create_text_message(
                    f"Error: Repository '{owner}/{repo}' not found "
                    "or the token lacks access permission."
                )
                return
            if resp.status_code == 401:
                yield self.create_text_message(
                    "Error: Invalid or expired GitHub token. "
                    "Please update your credentials."
                )
                return
            if resp.status_code == 403:
                reset_time = resp.headers.get("X-RateLimit-Reset")
                yield self.create_text_message(
                    "Error: GitHub API rate limit exceeded. "
                    f"Rate limit resets at Unix timestamp: {reset_time}."
                )
                return

            resp.raise_for_status()
            data = resp.json()

            # 5. 解析并格式化结果（跳过 PR，只保留 issue）
            issues = []
            for item in data:
                # GitHub 的 issues 接口也会返回 PR，需要过滤掉
                if "pull_request" in item:
                    continue
                issues.append(
                    {
                        "number": item.get("number"),
                        "title": item.get("title"),
                        "state": item.get("state"),
                        "html_url": item.get("html_url"),
                        "user": item.get("user", {}).get("login"),
                        "labels": [lbl.get("name") for lbl in item.get("labels", [])],
                        "created_at": item.get("created_at"),
                    }
                )

            result = {
                "repository": f"{owner}/{repo}",
                "state_filter": state,
                "count": len(issues),
                "issues": issues,
            }

            # text 输出：序列化为 JSON 字符串，供下游节点（如 LLM）作为
            # text 变量引用；json 输出：供 Dify 界面做结构化展示
            yield self.create_text_message(
                json.dumps(result, ensure_ascii=False, indent=2)
            )
            yield self.create_json_message(result)

        except requests.exceptions.Timeout:
            yield self.create_text_message(
                "Error: Request to GitHub API timed out. Please try again."
            )
        except requests.exceptions.ConnectionError:
            yield self.create_text_message(
                "Error: Failed to connect to GitHub API. "
                "Check your network connection."
            )
        except Exception as e:
            yield self.create_text_message(
                f"Error: An unexpected error occurred: {str(e)}"
            )
