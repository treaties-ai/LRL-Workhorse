import requests
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from functools import wraps
import os

class AuthMethod(Enum):
    OAUTH = "oauth"
    API_KEY = "api_key"
    REFRESH_TOKEN = "refresh_token"

class MuralAPIError(Exception):
    """Custom exception for Mural API errors"""
    pass

@dataclass
class APIResponse:
    success: bool
    data: Optional[Dict]
    error: Optional[str]
    retry_count: int = 0
    fallback_used: bool = False

class MuralCoreAPI:
    """
    Core API wrapper with comprehensive auto-healing capabilities
    """
    
    def __init__(self, config_path: str = "mural_config.json"):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.auth_method = AuthMethod.OAUTH
        self.retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff
        self.logger = self._setup_logging()
        self.health_status = {"api": "unknown", "auth": "unknown"}
        self._authenticate()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration with fallbacks"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Auto-generate default config
            default_config = {
                "oauth": {
                    "client_id": os.environ.get("MURAL_CLIENT_ID", ""),
                    "client_secret": os.environ.get("MURAL_CLIENT_SECRET", ""),
                    "redirect_uri": "http://localhost:8080/callback"
                },
                "api_key": os.environ.get("MURAL_API_KEY", ""),
                "workspace_id": os.environ.get("MURAL_WORKSPACE_ID", ""),
                "base_url": "https://api.mural.co/api/v0",
                "timeout": 30,
                "max_retries": 5
            }
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger('MuralAPI')
        logger.setLevel(logging.DEBUG)
        
        # File handler for full logs
        fh = logging.FileHandler('mural_api.log')
        fh.setLevel(logging.DEBUG)
        
        # Console handler for important messages
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def auto_heal(func):
        """Decorator for auto-healing API calls"""
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_error = None
            
            for retry_count, delay in enumerate(self.retry_delays):
                try:
                    result = func(self, *args, **kwargs)
                    if retry_count > 0:
                        self.logger.info(f"Success after {retry_count} retries")
                    return result
                    
                except requests.exceptions.Timeout:
                    last_error = "Timeout"
                    self.logger.warning(f"Timeout, retry {retry_count + 1} in {delay}s")
                    time.sleep(delay)
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:  # Rate limit
                        last_error = "Rate limit"
                        wait_time = int(e.response.headers.get('Retry-After', delay * 2))
                        self.logger.warning(f"Rate limited, waiting {wait_time}s")
                        time.sleep(wait_time)
                        
                    elif e.response.status_code == 401:  # Auth failure
                        last_error = "Auth failure"
                        self.logger.warning("Auth failed, attempting refresh")
                        if self._refresh_auth():
                            continue
                        else:
                            self._fallback_auth()
                            
                    elif e.response.status_code >= 500:  # Server error
                        last_error = "Server error"
                        self.logger.warning(f"Server error, retry {retry_count + 1} in {delay}s")
                        time.sleep(delay)
                    else:
                        raise
                        
                except Exception as e:
                    last_error = str(e)
                    self.logger.error(f"Unexpected error: {e}")
                    time.sleep(delay)
            
            # All retries exhausted, attempt fallback
            self.logger.error(f"All retries failed: {last_error}")
            return self._execute_fallback(func.__name__, *args, **kwargs)
            
        return wrapper
    
    def _authenticate(self) -> bool:
        """Multi-method authentication with fallbacks"""
        auth_methods = [
            (self._oauth_authenticate, AuthMethod.OAUTH),
            (self._api_key_authenticate, AuthMethod.API_KEY),
            (self._refresh_token_authenticate, AuthMethod.REFRESH_TOKEN)
        ]
        
        for auth_func, method in auth_methods:
            try:
                if auth_func():
                    self.auth_method = method
                    self.health_status["auth"] = "healthy"
                    self.logger.info(f"Authenticated using {method.value}")
                    return True
            except Exception as e:
                self.logger.warning(f"Auth method {method.value} failed: {e}")
                continue
        
        self.health_status["auth"] = "failed"
        raise MuralAPIError("All authentication methods failed")
    
    def _oauth_authenticate(self) -> bool:
        """OAuth authentication flow"""
        if not self.config["oauth"]["client_id"]:
            return False
            
        # Try multiple OAuth endpoints
        oauth_endpoints = [
            "https://app.mural.co/api/public/v1/authorization/oauth2/token",
            "https://api.mural.co/api/public/v1/authorization/oauth2/token",
            "https://api.mural.co/oauth2/token"
        ]
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.config["oauth"]["client_id"],
            "client_secret": self.config["oauth"]["client_secret"],
            "scope": "murals:read murals:write"
        }
        
        for endpoint in oauth_endpoints:
            try:
                response = requests.post(endpoint, data=data, timeout=10)
                if response.status_code == 200:
                    token_data = response.json()
                    self.session.headers["Authorization"] = f"Bearer {token_data['access_token']}"
                    self.config["refresh_token"] = token_data.get("refresh_token", "")
                    self.logger.info(f"OAuth successful with endpoint: {endpoint}")
                    return True
            except Exception as e:
                self.logger.debug(f"OAuth failed for {endpoint}: {e}")
                continue
        
        return False
    
    def _api_key_authenticate(self) -> bool:
        """API key authentication"""
        if not self.config["api_key"]:
            return False
            
        self.session.headers["Authorization"] = f"Bearer {self.config['api_key']}"
        
        # Test the API key
        test_response = self.session.get(
            f"{self.config['base_url']}/workspaces",
            timeout=10
        )
        return test_response.status_code == 200
    
    def _refresh_token_authenticate(self) -> bool:
        """Refresh token authentication"""
        if not self.config.get("refresh_token"):
            return False
            
        token_endpoint = f"{self.config['base_url']}/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.config["refresh_token"],
            "client_id": self.config["oauth"]["client_id"],
            "client_secret": self.config["oauth"]["client_secret"]
        }
        
        response = requests.post(token_endpoint, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.session.headers["Authorization"] = f"Bearer {token_data['access_token']}"
            self.config["refresh_token"] = token_data.get("refresh_token", "")
            return True
        return False
    
    def _refresh_auth(self) -> bool:
        """Attempt to refresh authentication"""
        return self._refresh_token_authenticate()
    
    def _fallback_auth(self) -> None:
        """Fallback authentication strategy"""
        self.logger.info("Attempting fallback authentication")
        self._authenticate()
    
    def _execute_fallback(self, func_name: str, *args, **kwargs) -> APIResponse:
        """Execute fallback strategy for failed operations"""
        fallback_strategies = {
            "create_shape": self._fallback_create_simple_sticky,
            "create_sticky_note": self._fallback_create_text_widget,
            "batch_create": self._fallback_individual_create,
            "update_widget": self._fallback_skip_update
        }
        
        strategy = fallback_strategies.get(func_name, self._fallback_log_only)
        return strategy(*args, **kwargs)
    
    def _fallback_create_simple_sticky(self, *args, **kwargs) -> APIResponse:
        """Fallback to creating a simple sticky note instead of shape"""
        self.logger.info("Falling back to simple sticky note")
        return self.create_sticky_note(
            text="[Shape placeholder]",
            x=kwargs.get('x', 100),
            y=kwargs.get('y', 100),
            color="#FFFF00"
        )
    
    def _fallback_create_text_widget(self, *args, **kwargs) -> APIResponse:
        """Fallback to creating a text widget"""
        self.logger.info("Falling back to text widget")
        # Implementation for text widget creation
        return APIResponse(
            success=False,
            data=None,
            error="Fallback to text widget not implemented",
            fallback_used=True
        )
    
    def _fallback_individual_create(self, widgets: List[Dict], **kwargs) -> APIResponse:
        """Fallback to creating widgets individually"""
        self.logger.info("Falling back to individual creation")
        created = []
        failed = []
        
        for widget in widgets[:5]:  # Limit to 5 to avoid rate limiting
            try:
                result = self.create_widget(widget)
                if result.success:
                    created.append(result.data)
                else:
                    failed.append(widget)
            except Exception as e:
                failed.append(widget)
                self.logger.error(f"Individual creation failed: {e}")
        
        return APIResponse(
            success=len(created) > 0,
            data={"created": created, "failed": failed},
            error=f"Partial success: {len(created)} created, {len(failed)} failed",
            fallback_used=True
        )
    
    def _fallback_skip_update(self, *args, **kwargs) -> APIResponse:
        """Skip the update operation"""
        self.logger.info("Skipping update operation")
        return APIResponse(
            success=False,
            data=None,
            error="Update skipped",
            fallback_used=True
        )
    
    def _fallback_log_only(self, *args, **kwargs) -> APIResponse:
        """Log the failure and return error"""
        self.logger.error(f"No fallback available for operation")
        return APIResponse(
            success=False,
            data=None,
            error="Operation failed with no fallback",
            fallback_used=True
        )
    
    @auto_heal
    def create_mural(self, title: str, width: int = 9000, height: int = 6000) -> APIResponse:
        """Create a new mural with auto-healing"""
        endpoint = f"{self.config['base_url']}/workspaces/{self.config['workspace_id']}/murals"
        
        data = {
            "title": title,
            "width": width,
            "height": height
        }
        
        response = self.session.post(
            endpoint,
            json=data,
            timeout=self.config["timeout"]
        )
        response.raise_for_status()
        
        return APIResponse(
            success=True,
            data=response.json(),
            error=None
        )
    
    @auto_heal
    def create_shape(self, mural_id: str, shape_type: str, **kwargs) -> APIResponse:
        """Create a shape with auto-healing"""
        endpoint = f"{self.config['base_url']}/murals/{mural_id}/widgets"
        
        widget_data = {
            "type": shape_type,
            **kwargs
        }
        
        response = self.session.post(
            endpoint,
            json=widget_data,
            timeout=self.config["timeout"]
        )
        response.raise_for_status()
        
        return APIResponse(
            success=True,
            data=response.json(),
            error=None
        )
    
    @auto_heal
    def create_sticky_note(self, mural_id: str, text: str, x: int, y: int, 
                          color: str = "#FFFF00", **kwargs) -> APIResponse:
        """Create a sticky note with auto-healing"""
        endpoint = f"{self.config['base_url']}/murals/{mural_id}/widgets"
        
        widget_data = {
            "type": "sticky-note",
            "text": text,
            "x": x,
            "y": y,
            "style": {
                "backgroundColor": color
            },
            **kwargs
        }
        
        response = self.session.post(
            endpoint,
            json=widget_data,
            timeout=self.config["timeout"]
        )
        response.raise_for_status()
        
        return APIResponse(
            success=True,
            data=response.json(),
            error=None
        )
    
    @auto_heal
    def batch_create_widgets(self, mural_id: str, widgets: List[Dict]) -> APIResponse:
        """Batch create widgets with auto-healing and size management"""
        endpoint = f"{self.config['base_url']}/murals/{mural_id}/widgets/batch"
        
        # Respect batch size limit
        batch_size = min(len(widgets), 25)  # Project's proven optimal size
        
        results = []
        for i in range(0, len(widgets), batch_size):
            batch = widgets[i:i + batch_size]
            
            response = self.session.post(
                endpoint,
                json={"widgets": batch},
                timeout=self.config["timeout"]
            )
            response.raise_for_status()
            results.append(response.json())
            
            # Delay between batches to avoid rate limiting
            if i + batch_size < len(widgets):
                time.sleep(0.5)
        
        return APIResponse(
            success=True,
            data={"batches": results, "total_created": len(widgets)},
            error=None
        )
    
    def health_check(self) -> Dict[str, str]:
        """Comprehensive health check"""
        checks = {
            "auth": self._check_auth_health(),
            "api": self._check_api_health(),
            "rate_limit": self._check_rate_limit_health()
        }
        
        self.health_status.update(checks)
        return self.health_status
    
    def _check_auth_health(self) -> str:
        """Check authentication health"""
        try:
            response = self.session.get(
                f"{self.config['base_url']}/users/me",
                timeout=5
            )
            return "healthy" if response.status_code == 200 else "unhealthy"
        except Exception:
            return "unhealthy"
    
    def _check_api_health(self) -> str:
        """Check API health"""
        try:
            response = requests.get(
                f"{self.config['base_url']}/health",
                timeout=5
            )
            return "healthy" if response.status_code == 200 else "unhealthy"
        except Exception:
            return "unhealthy"
    
    def _check_rate_limit_health(self) -> str:
        """Check rate limit status"""
        try:
            response = self.session.get(
                f"{self.config['base_url']}/users/me",
                timeout=5
            )
            remaining = int(response.headers.get('X-RateLimit-Remaining', 100))
            return "healthy" if remaining > 10 else "warning"
        except Exception:
            return "unknown"
    
    def create_widget(self, widget: Dict) -> APIResponse:
        """Create a single widget"""
        widget_type = widget.get("type", "sticky-note")
        
        if widget_type == "sticky-note":
            return self.create_sticky_note(
                mural_id=widget.get("mural_id"),
                text=widget.get("text", ""),
                x=widget.get("x", 100),
                y=widget.get("y", 100),
                color=widget.get("color", "#FFFF00")
            )
        elif widget_type in ["circle", "rectangle"]:
            return self.create_shape(
                mural_id=widget.get("mural_id"),
                shape_type=widget_type,
                **widget.get("params", {})
            )
        else:
            return APIResponse(
                success=False,
                data=None,
                error=f"Unknown widget type: {widget_type}"
            )
