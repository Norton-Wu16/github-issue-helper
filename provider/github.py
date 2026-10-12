from typing import Any

import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GitHubProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """Validate the GitHub token by making a lightweight test API call."""
        try:
            token = credentials.get("github_token")
            if not token:
                raise ToolProviderCredentialValidationError(
                    "GitHub token is required."
                )

            resp = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
                timeout=10,
            )

            if resp.status_code == 401:
                raise ToolProviderCredentialValidationError(
                    "Invalid or expired GitHub token. Please check your token."
                )
            if resp.status_code == 403:
                raise ToolProviderCredentialValidationError(
                    "Token is valid but rate-limited or lacks permissions. "
                    "Please ensure the token has 'repo' scope."
                )

            resp.raise_for_status()

        except ToolProviderCredentialValidationError:
            raise
        except requests.exceptions.Timeout:
            raise ToolProviderCredentialValidationError(
                "Connection to GitHub timed out. Please try again."
            )
        except requests.exceptions.ConnectionError:
            raise ToolProviderCredentialValidationError(
                "Failed to connect to GitHub API. Check your network."
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to validate credentials: {str(e)}"
            )
