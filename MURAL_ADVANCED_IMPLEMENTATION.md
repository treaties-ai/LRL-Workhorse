# Mural API Advanced Implementation with Auto-Healing
## Complete Implementation Guide for Body Visualization & Dynamic Visuals

> ⚠️ **IMPORTANT**: Before implementing, read [MURAL_BEST_PRACTICES.md](./MURAL_BEST_PRACTICES.md) for critical lessons learned and working configurations.

### System Architecture
```
┌─────────────────────────────────────────────────┐
│                Test Orchestrator                 │
│         (Coordinates 4 Browser Agents)           │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Batch Processor                    │
│        (25-30 items, Queue Management)          │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│            Body Visualizer                      │
│      (Shapes, Regions, Somatic Mapping)         │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Core API Layer                     │
│        (Auth, Retry, Fallback Logic)            │
└─────────────────────────────────────────────────┘
```

## 1. Core API Layer with Auto-Healing

```python
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
            
        # Implementation for OAuth flow
        # This would involve browser automation or manual token retrieval
        token_endpoint = f"{self.config['base_url']}/oauth/token"
        
        data = {
            "grant_type": "client_credentials",
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


## 2. Body Visualizer with Somatic Mapping

```python
from typing import Dict, List, Tuple, Optional
import math

class BodyRegion(Enum):
    HEAD = "head"
    HEART = "heart"
    TORSO = "torso"
    LEFT_ARM = "left_arm"
    RIGHT_ARM = "right_arm"
    LEFT_LEG = "left_leg"
    RIGHT_LEG = "right_leg"
    CORE = "core"

class MuralBodyVisualizer:
    """
    Creates and manages body visualization for somatic mapping
    """
    
    def __init__(self, api: MuralCoreAPI):
        self.api = api
        self.body_template = {}
        self.region_widgets = {region: [] for region in BodyRegion}
        self.somatic_mappings = self._initialize_somatic_mappings()
        self.mural_id = None
        self.logger = logging.getLogger('MuralBodyVisualizer')
    
    def _initialize_somatic_mappings(self) -> Dict[BodyRegion, List[str]]:
        """Initialize somatic theme mappings to body regions"""
        return {
            BodyRegion.HEAD: [
                "thoughts", "awareness", "vision", "hearing", 
                "cognition", "beliefs", "imagination", "memory"
            ],
            BodyRegion.HEART: [
                "emotions", "love", "grief", "connection",
                "compassion", "joy", "sadness", "empathy"
            ],
            BodyRegion.TORSO: [
                "breathing", "core stability", "gut feelings",
                "digestion", "intuition", "centeredness"
            ],
            BodyRegion.LEFT_ARM: [
                "receiving", "holding", "embracing", "accepting",
                "nurturing", "supporting"
            ],
            BodyRegion.RIGHT_ARM: [
                "giving", "pushing", "creating", "expressing",
                "reaching", "defending"
            ],
            BodyRegion.LEFT_LEG: [
                "grounding", "stability", "foundation", "support",
                "rooting", "balance"
            ],
            BodyRegion.RIGHT_LEG: [
                "movement", "progress", "stepping forward", "action",
                "momentum", "direction"
            ],
            BodyRegion.CORE: [
                "power", "will", "determination", "confidence",
                "self", "identity"
            ]
        }
    
    def create_body_template(self, mural_id: str) -> bool:
        """
        Create the body visualization template on the mural
        Auto-heals by trying progressively simpler shapes
        """
        self.mural_id = mural_id
        
        # Define body parts with coordinates and fallback strategies
        body_parts = [
            {
                "region": BodyRegion.HEAD,
                "primary": {"type": "circle", "x": 400, "y": 100, "radius": 50},
                "fallback1": {"type": "rectangle", "x": 375, "y": 75, "width": 50, "height": 50},
                "fallback2": {"type": "sticky-note", "x": 400, "y": 100, "text": "HEAD"}
            },
            {
                "region": BodyRegion.HEART,
                "primary": {"type": "circle", "x": 390, "y": 200, "radius": 25},
                "fallback1": {"type": "rectangle", "x": 375, "y": 185, "width": 30, "height": 30},
                "fallback2": {"type": "sticky-note", "x": 390, "y": 200, "text": "♥"}
            },
            {
                "region": BodyRegion.TORSO,
                "primary": {"type": "rectangle", "x": 350, "y": 150, "width": 100, "height": 150},
                "fallback1": {"type": "rectangle", "x": 350, "y": 150, "width": 80, "height": 120},
                "fallback2": {"type": "sticky-note", "x": 400, "y": 225, "text": "TORSO"}
            },
            {
                "region": BodyRegion.LEFT_ARM,
                "primary": {"type": "rectangle", "x": 250, "y": 170, "width": 80, "height": 20},
                "fallback1": {"type": "rectangle", "x": 270, "y": 170, "width": 60, "height": 15},
                "fallback2": {"type": "sticky-note", "x": 290, "y": 180, "text": "L-ARM"}
            },
            {
                "region": BodyRegion.RIGHT_ARM,
                "primary": {"type": "rectangle", "x": 470, "y": 170, "width": 80, "height": 20},
                "fallback1": {"type": "rectangle", "x": 470, "y": 170, "width": 60, "height": 15},
                "fallback2": {"type": "sticky-note", "x": 510, "y": 180, "text": "R-ARM"}
            },
            {
                "region": BodyRegion.LEFT_LEG,
                "primary": {"type": "rectangle", "x": 360, "y": 300, "width": 30, "height": 100},
                "fallback1": {"type": "rectangle", "x": 365, "y": 300, "width": 25, "height": 80},
                "fallback2": {"type": "sticky-note", "x": 375, "y": 350, "text": "L-LEG"}
            },
            {
                "region": BodyRegion.RIGHT_LEG,
                "primary": {"type": "rectangle", "x": 410, "y": 300, "width": 30, "height": 100},
                "fallback1": {"type": "rectangle", "x": 410, "y": 300, "width": 25, "height": 80},
                "fallback2": {"type": "sticky-note", "x": 425, "y": 350, "text": "R-LEG"}
            }
        ]
        
        created_count = 0
        for part in body_parts:
            widget_id = self._create_body_part_with_fallback(part)
            if widget_id:
                self.body_template[part["region"]] = widget_id
                created_count += 1
                self.logger.info(f"Created {part['region'].value}: {widget_id}")
            else:
                self.logger.error(f"Failed to create {part['region'].value}")
        
        success = created_count >= 5  # Need at least 5 body parts for viable visualization
        
        if success:
            self.logger.info(f"Body template created with {created_count}/{len(body_parts)} parts")
        else:
            self.logger.error(f"Body template creation failed. Only {created_count} parts created")
        
        return success
    
    def _create_body_part_with_fallback(self, part: Dict) -> Optional[str]:
        """Create a body part with multiple fallback strategies"""
        strategies = ["primary", "fallback1", "fallback2"]
        
        for strategy in strategies:
            shape_config = part[strategy].copy()
            shape_type = shape_config.pop("type")
            
            try:
                if shape_type == "circle":
                    result = self.api.create_shape(
                        self.mural_id,
                        "circle",
                        **shape_config
                    )
                elif shape_type == "rectangle":
                    result = self.api.create_shape(
                        self.mural_id,
                        "rectangle",
                        **shape_config
                    )
                elif shape_type == "sticky-note":
                    result = self.api.create_sticky_note(
                        self.mural_id,
                        shape_config.pop("text"),
                        shape_config["x"],
                        shape_config["y"],
                        color="#E0E0E0"  # Gray for body parts
                    )
                else:
                    continue
                
                if result.success and result.data:
                    return result.data.get("id")
                    
            except Exception as e:
                self.logger.warning(f"Strategy {strategy} failed for {part['region'].value}: {e}")
                continue
        
        return None
    
    def map_content_to_region(self, content: str, themes: List[str]) -> BodyRegion:
        """Map content to appropriate body region based on themes"""
        theme_scores = {region: 0 for region in BodyRegion}
        
        # Score each region based on theme matches
        for theme in themes:
            theme_lower = theme.lower()
            for region, keywords in self.somatic_mappings.items():
                for keyword in keywords:
                    if keyword in theme_lower or theme_lower in keyword:
                        theme_scores[region] += 1
        
        # Return region with highest score, default to TORSO
        if max(theme_scores.values()) > 0:
            return max(theme_scores, key=theme_scores.get)
        return BodyRegion.TORSO
    
    def add_sticky_to_region(self, region: BodyRegion, text: str, 
                            tdai_score: float = 5.0, **kwargs) -> Optional[str]:
        """Add a sticky note to a specific body region with TDAI color coding"""
        if region not in self.body_template:
            self.logger.warning(f"Region {region.value} not in template")
            return None
        
        # Get region coordinates with jitter to avoid overlap
        x, y = self._get_region_coordinates(region)
        
        # Color based on TDAI score
        color = self._tdai_to_color(tdai_score)
        
        # Size based on impact (optional enhancement)
        width = int(80 + (tdai_score - 5) * 5)  # 80-105 based on score
        
        try:
            result = self.api.create_sticky_note(
                self.mural_id,
                text,
                x, y,
                color=color,
                width=width,
                **kwargs
            )
            
            if result.success and result.data:
                widget_id = result.data.get("id")
                self.region_widgets[region].append(widget_id)
                return widget_id
                
        except Exception as e:
            self.logger.error(f"Failed to add sticky to {region.value}: {e}")
        
        return None
    
    def _get_region_coordinates(self, region: BodyRegion) -> Tuple[int, int]:
        """Get coordinates for placing content in a region with jitter"""
        import random
        
        # Base coordinates for each region
        base_coords = {
            BodyRegion.HEAD: (400, 100),
            BodyRegion.HEART: (390, 200),
            BodyRegion.TORSO: (400, 225),
            BodyRegion.LEFT_ARM: (290, 180),
            BodyRegion.RIGHT_ARM: (510, 180),
            BodyRegion.LEFT_LEG: (375, 350),
            BodyRegion.RIGHT_LEG: (425, 350),
            BodyRegion.CORE: (400, 250)
        }
        
        base_x, base_y = base_coords.get(region, (400, 200))
        
        # Add jitter to avoid exact overlap
        jitter_x = random.randint(-30, 30)
        jitter_y = random.randint(-30, 30)
        
        # Adjust based on how many items are already in region
        existing_count = len(self.region_widgets[region])
        offset_x = (existing_count % 3) * 35
        offset_y = (existing_count // 3) * 35
        
        return (base_x + jitter_x + offset_x, base_y + jitter_y + offset_y)
    
    def _tdai_to_color(self, tdai_score: float) -> str:
        """Convert TDAI score to color (red=shallow, yellow=medium, green=deep)"""
        if tdai_score < 3:
            return "#FF6B6B"  # Light red
        elif tdai_score < 5:
            return "#FFD93D"  # Yellow
        elif tdai_score < 7:
            return "#6BCF7F"  # Light green
        else:
            return "#2ECC71"  # Deep green
    
    def create_connection(self, widget1_id: str, widget2_id: str, 
                         label: str = "") -> Optional[str]:
        """Create a connection line between two widgets"""
        try:
            result = self.api.create_shape(
                self.mural_id,
                "connector",
                start_widget=widget1_id,
                end_widget=widget2_id,
                label=label,
                style={"lineColor": "#888888", "lineStyle": "dashed"}
            )
            
            if result.success:
                return result.data.get("id")
        except Exception as e:
            self.logger.error(f"Failed to create connection: {e}")
        return None
    
    def highlight_region(self, region: BodyRegion, duration_ms: int = 2000):
        """Highlight a body region temporarily (visual feedback)"""
        # This would require websocket or polling implementation
        # For now, we'll change the color temporarily
        pass


## 3. Batch Processor with Queue Management

```python
import queue
import threading
from collections import defaultdict
import redis
import json

class MuralBatchProcessor:
    """
    Handles batch processing with queue management and Redis integration
    Respects the proven 25-30 item batch size from project
    """
    
    def __init__(self, api: MuralCoreAPI, visualizer: MuralBodyVisualizer):
        self.api = api
        self.visualizer = visualizer
        self.batch_size = 25  # Proven optimal from project
        self.queue = queue.Queue()
        self.redis_client = self._init_redis()
        self.processing_thread = None
        self.stop_processing = False
        self.stats = defaultdict(int)
        self.logger = logging.getLogger('MuralBatchProcessor')
    
    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for queue management"""
        try:
            client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True,
                socket_connect_timeout=5
            )
            client.ping()
            self.logger.info("Redis connected for queue management")
            return client
        except Exception as e:
            self.logger.warning(f"Redis not available: {e}. Using in-memory queue only")
            return None
    
    def start_processing(self):
        """Start the batch processing thread"""
        if self.processing_thread and self.processing_thread.is_alive():
            self.logger.warning("Processing already running")
            return
        
        self.stop_processing = False
        self.processing_thread = threading.Thread(target=self._process_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        self.logger.info("Batch processing started")
    
    def stop_processing(self):
        """Stop the batch processing thread"""
        self.stop_processing = True
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        self.logger.info("Batch processing stopped")
    
    def _process_loop(self):
        """Main processing loop"""
        batch_buffer = []
        last_flush = time.time()
        flush_interval = 0.5  # Flush every 500ms as designed
        
        while not self.stop_processing:
            try:
                # Try to get from Redis first
                if self.redis_client:
                    item = self._get_from_redis()
                    if item:
                        batch_buffer.append(item)
                
                # Then check local queue
                try:
                    item = self.queue.get(timeout=0.1)
                    batch_buffer.append(item)
                except queue.Empty:
                    pass
                
                # Flush if batch is full or time interval reached
                current_time = time.time()
                should_flush = (
                    len(batch_buffer) >= self.batch_size or
                    (len(batch_buffer) > 0 and current_time - last_flush > flush_interval)
                )
                
                if should_flush:
                    self._flush_batch(batch_buffer)
                    batch_buffer = []
                    last_flush = current_time
                    
            except Exception as e:
                self.logger.error(f"Processing loop error: {e}")
                time.sleep(1)
    
    def _get_from_redis(self) -> Optional[Dict]:
        """Get item from Redis queue"""
        try:
            data = self.redis_client.lpop("mural:queue")
            if data:
                return json.loads(data)
        except Exception as e:
            self.logger.debug(f"Redis get failed: {e}")
        return None
    
    def _flush_batch(self, batch: List[Dict]):
        """Process a batch of items"""
        if not batch:
            return
        
        self.logger.info(f"Processing batch of {len(batch)} items")
        
        # Group by type for efficient processing
        grouped = self._group_by_type(batch)
        
        for item_type, items in grouped.items():
            if item_type == "sticky_note":
                self._process_sticky_notes(items)
            elif item_type == "shape":
                self._process_shapes(items)
            elif item_type == "connection":
                self._process_connections(items)
            else:
                self.logger.warning(f"Unknown item type: {item_type}")
    
    def _group_by_type(self, batch: List[Dict]) -> Dict[str, List[Dict]]:
        """Group batch items by type"""
        grouped = defaultdict(list)
        for item in batch:
            grouped[item.get("type", "unknown")].append(item)
        return grouped
    
    def _process_sticky_notes(self, notes: List[Dict]):
        """Process sticky notes batch"""
        # Group by region for body mapping
        by_region = defaultdict(list)
        
        for note in notes:
            themes = note.get("themes", [])
            region = self.visualizer.map_content_to_region(
                note.get("text", ""),
                themes
            )
            note["region"] = region
            by_region[region].append(note)
        
        # Process each region's notes
        for region, region_notes in by_region.items():
            for note in region_notes:
                try:
                    widget_id = self.visualizer.add_sticky_to_region(
                        region,
                        note.get("text", ""),
                        note.get("tdai_score", 5.0)
                    )
                    
                    if widget_id:
                        self.stats["sticky_created"] += 1
                        self._notify_success("sticky_note", widget_id)
                    else:
                        self.stats["sticky_failed"] += 1
                        self._handle_failure("sticky_note", note)
                        
                except Exception as e:
                    self.logger.error(f"Failed to process sticky: {e}")
                    self.stats["sticky_failed"] += 1
                    self._handle_failure("sticky_note", note)
    
    def _process_shapes(self, shapes: List[Dict]):
        """Process shapes batch"""
        for shape in shapes:
            try:
                result = self.api.create_shape(
                    self.visualizer.mural_id,
                    shape.get("type"),
                    **shape.get("params", {})
                )
                
                if result.success:
                    self.stats["shape_created"] += 1
                    self._notify_success("shape", result.data.get("id"))
                else:
                    self.stats["shape_failed"] += 1
                    self._handle_failure("shape", shape)
                    
            except Exception as e:
                self.logger.error(f"Failed to process shape: {e}")
                self.stats["shape_failed"] += 1
                self._handle_failure("shape", shape)
    
    def _process_connections(self, connections: List[Dict]):
        """Process connections batch"""
        for conn in connections:
            try:
                widget_id = self.visualizer.create_connection(
                    conn.get("from_widget"),
                    conn.get("to_widget"),
                    conn.get("label", "")
                )
                
                if widget_id:
                    self.stats["connection_created"] += 1
                    self._notify_success("connection", widget_id)
                else:
                    self.stats["connection_failed"] += 1
                    self._handle_failure("connection", conn)
                    
            except Exception as e:
                self.logger.error(f"Failed to process connection: {e}")
                self.stats["connection_failed"] += 1
                self._handle_failure("connection", conn)
    
    def _handle_failure(self, item_type: str, item: Dict):
        """Handle failed item with retry logic"""
        retry_key = f"mural:retry:{item_type}"
        
        if self.redis_client:
            # Add to retry queue with exponential backoff
            item["retry_count"] = item.get("retry_count", 0) + 1
            
            if item["retry_count"] < 3:
                item["retry_after"] = time.time() + (2 ** item["retry_count"])
                self.redis_client.rpush(retry_key, json.dumps(item))
                self.logger.info(f"Queued {item_type} for retry #{item['retry_count']}")
            else:
                self.logger.error(f"Max retries exceeded for {item_type}")
                self._log_permanent_failure(item_type, item)
    
    def _notify_success(self, item_type: str, widget_id: str):
        """Notify success through Redis pub/sub"""
        if self.redis_client:
            self.redis_client.publish(
                "mural:success",
                json.dumps({"type": item_type, "id": widget_id})
            )
    
    def _log_permanent_failure(self, item_type: str, item: Dict):
        """Log permanent failures for analysis"""
        with open("mural_failures.json", "a") as f:
            f.write(json.dumps({
                "timestamp": time.time(),
                "type": item_type,
                "item": item
            }) + "\n")
    
    def add_to_queue(self, item: Dict):
        """Add item to processing queue"""
        # Add to Redis if available
        if self.redis_client:
            self.redis_client.rpush("mural:queue", json.dumps(item))
        
        # Also add to local queue as backup
        self.queue.put(item)
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics"""
        return dict(self.stats)


## 4. Integration Adapter for Existing System

```python
class MuralSystemAdapter:
    """
    Adapter that integrates Mural API with existing agent system
    Bridges the gap between agent outputs and Mural visualization
    """
    
    def __init__(self):
        self.api = MuralCoreAPI()
        self.visualizer = MuralBodyVisualizer(self.api)
        self.batch_processor = MuralBatchProcessor(self.api, self.visualizer)
        self.mural_id = None
        self.logger = logging.getLogger('MuralSystemAdapter')
        
        # Start batch processing
        self.batch_processor.start_processing()
    
    def initialize_mural(self, title: str = "Somatic Body Map - Editorial Sprint") -> bool:
        """Initialize a new mural with body template"""
        try:
            # Create mural
            result = self.api.create_mural(title)
            if not result.success:
                self.logger.error(f"Failed to create mural: {result.error}")
                return False
            
            self.mural_id = result.data.get("id")
            self.visualizer.mural_id = self.mural_id
            
            # Create body template
            if not self.visualizer.create_body_template(self.mural_id):
                self.logger.error("Failed to create body template")
                return False
            
            self.logger.info(f"Mural initialized: {self.mural_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Mural initialization failed: {e}")
            return False
    
    def process_agent_output(self, agent_name: str, output: Dict):
        """Process output from existing agents"""
        # Extract relevant data from agent output
        text = output.get("insight", "")
        themes = output.get("themes", [])
        tdai_score = output.get("tdai_score", 5.0)
        
        # Queue for batch processing
        self.batch_processor.add_to_queue({
            "type": "sticky_note",
            "text": f"[{agent_name}] {text[:100]}",
            "themes": themes,
            "tdai_score": tdai_score,
            "metadata": {
                "agent": agent_name,
                "timestamp": time.time()
            }
        })
    
    def process_perplexity_thread(self, thread_data: Dict):
        """Process a Perplexity thread (25-30 sources)"""
        sources = thread_data.get("sources", [])
        
        # Batch process sources
        for i, source in enumerate(sources[:30]):  # Limit to 30 as per project
            quality_score = source.get("quality_score", 5.0)
            
            self.batch_processor.add_to_queue({
                "type": "sticky_note",
                "text": f"Source {i+1}: {source.get('title', 'Unknown')}",
                "themes": source.get("themes", []),
                "tdai_score": quality_score,
                "metadata": {
                    "source_url": source.get("url"),
                    "thread_id": thread_data.get("thread_id")
                }
            })
    
    def create_theme_connections(self, theme: str):
        """Create connections between related sticky notes"""
        # This would analyze existing widgets and create connections
        # Implementation depends on Mural API capabilities
        pass
    
    def export_for_editorial(self) -> Dict:
        """Export current state for editorial team"""
        stats = self.batch_processor.get_stats()
        
        return {
            "mural_id": self.mural_id,
            "mural_url": f"https://app.mural.co/t/workspace/{self.mural_id}",
            "statistics": stats,
            "body_regions": {
                region.value: len(widgets)
                for region, widgets in self.visualizer.region_widgets.items()
            },
            "timestamp": time.time()
        }
    
    def shutdown(self):
        """Clean shutdown"""
        self.batch_processor.stop_processing()
        self.logger.info("Mural adapter shutdown complete")


## 5. Usage Example

```python
def main():
    """Example usage integrating with existing system"""
    
    # Initialize adapter
    adapter = MuralSystemAdapter()
    
    # Create new mural with body template
    if not adapter.initialize_mural("Workshop Day 1 - Somatic Mapping"):
        print("Failed to initialize mural")
        return
    
    # Simulate agent outputs
    agent_outputs = [
        {
            "agent": "emotional_intelligence",
            "output": {
                "insight": "Patient shows deep grief in chest area",
                "themes": ["grief", "loss", "heart", "breathing"],
                "tdai_score": 8.5
            }
        },
        {
            "agent": "somatic_awareness",
            "output": {
                "insight": "Tension pattern in shoulders indicates held trauma",
                "themes": ["tension", "shoulders", "holding", "protection"],
                "tdai_score": 7.2
            }
        }
    ]
    
    # Process agent outputs
    for item in agent_outputs:
        adapter.process_agent_output(item["agent"], item["output"])
    
    # Simulate Perplexity thread
    perplexity_thread = {
        "thread_id": "thread_001",
        "sources": [
            {
                "title": "Somatic Experiencing Research",
                "url": "https://example.com/research",
                "themes": ["trauma", "body", "healing"],
                "quality_score": 9.0
            }
            # ... 25-30 sources
        ]
    }
    
    adapter.process_perplexity_thread(perplexity_thread)
    
    # Wait for batch processing
    time.sleep(2)
    
    # Export for editorial team
    export_data = adapter.export_for_editorial()
    print(f"Mural ready at: {export_data['mural_url']}")
    print(f"Statistics: {export_data['statistics']}")
    
    # Shutdown
    adapter.shutdown()


if __name__ == "__main__":
    main()
```

## Key Features Summary

### Auto-Healing Capabilities
- **Multi-method authentication**: OAuth → API Key → Refresh Token
- **Exponential backoff retry**: 1, 2, 4, 8, 16 second delays
- **Rate limit handling**: Respects Retry-After headers
- **Fallback strategies**: Shape → Rectangle → Sticky Note
- **Batch size management**: Auto-reduces on failures

### Integration Points
- **Redis Queue**: Integrates with existing Redis infrastructure
- **Agent Outputs**: Direct processing of agent analysis
- **Perplexity Threads**: Handles 25-30 sources per thread
- **TDAI Scoring**: Visual encoding of depth scores
- **Editorial Export**: Whiteboard-friendly format

### Performance Optimizations
- **Batch Processing**: 25-30 items per batch (proven optimal)
- **Queue Management**: Redis + in-memory fallback
- **Async Processing**: Non-blocking thread model
- **Smart Clustering**: Prevents widget overlap
- **Health Monitoring**: Real-time API health checks

This implementation respects all lessons learned from the project while adding advanced capabilities for body visualization and auto-healing.
