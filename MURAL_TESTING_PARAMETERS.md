# Mural API Testing Parameters
## Comprehensive Test Matrix & Auto-Adjustment Rules

## Test Matrix Dimensions

### 5-Dimensional Test Coverage Matrix

```
┌──────────────────────────────────────────────────────┐
│                  TEST MATRIX DIMENSIONS               │
├────────────────┬──────────────────────────────────────┤
│ 1. Operations  │ Auth, Create, Read, Update, Delete   │
│ 2. Widget Types│ Shapes, Sticky Notes, Connectors     │
│ 3. Batch Sizes │ 1, 10, 25, 50, 100                  │
│ 4. Failure Modes│ Network, Auth, Rate Limit, Malformed│
│ 5. Recovery    │ Retry, Reduce, Fallback, Skip       │
└────────────────┴──────────────────────────────────────┘
```

## 1. Complete Test Parameter Matrix

```python
TEST_MATRIX = {
    "operations": {
        "auth": {
            "methods": ["oauth", "api_key", "refresh_token"],
            "timeout": 30,
            "retry_count": 3,
            "fallback_sequence": ["oauth", "api_key", "refresh_token", "cached"]
        },
        "create": {
            "widgets": ["circle", "rectangle", "sticky_note", "connector"],
            "batch_enabled": True,
            "max_batch_size": 25,
            "timeout": 10,
            "retry_count": 5
        },
        "read": {
            "pagination": True,
            "page_size": 100,
            "timeout": 5,
            "cache_ttl": 300
        },
        "update": {
            "batch_enabled": True,
            "max_batch_size": 10,
            "timeout": 10,
            "retry_count": 3
        },
        "delete": {
            "batch_enabled": False,
            "requires_confirmation": True,
            "timeout": 5,
            "retry_count": 1
        }
    },
    
    "widget_types": {
        "circle": {
            "required_params": ["x", "y", "radius"],
            "optional_params": ["color", "border"],
            "fallback": "rectangle",
            "complexity": 2
        },
        "rectangle": {
            "required_params": ["x", "y", "width", "height"],
            "optional_params": ["color", "border"],
            "fallback": "sticky_note",
            "complexity": 1
        },
        "sticky_note": {
            "required_params": ["x", "y", "text"],
            "optional_params": ["color", "width", "height"],
            "fallback": None,
            "complexity": 0
        },
        "connector": {
            "required_params": ["start_widget", "end_widget"],
            "optional_params": ["label", "style"],
            "fallback": None,
            "complexity": 3
        }
    },
    
    "batch_sizes": {
        "micro": {
            "size": 1,
            "delay_ms": 0,
            "priority": 1
        },
        "small": {
            "size": 10,
            "delay_ms": 100,
            "priority": 2
        },
        "optimal": {
            "size": 25,
            "delay_ms": 500,
            "priority": 3
        },
        "large": {
            "size": 50,
            "delay_ms": 1000,
            "priority": 4
        },
        "stress": {
            "size": 100,
            "delay_ms": 2000,
            "priority": 5
        }
    },
    
    "failure_modes": {
        "network_timeout": {
            "error_codes": ["ETIMEDOUT", "ECONNRESET"],
            "recovery": "retry_with_backoff",
            "max_retries": 5
        },
        "auth_failure": {
            "error_codes": [401, 403],
            "recovery": "refresh_credentials",
            "max_retries": 3
        },
        "rate_limit": {
            "error_codes": [429],
            "recovery": "exponential_backoff",
            "max_retries": 10
        },
        "malformed_request": {
            "error_codes": [400],
            "recovery": "validate_and_retry",
            "max_retries": 2
        },
        "server_error": {
            "error_codes": [500, 502, 503],
            "recovery": "wait_and_retry",
            "max_retries": 5
        }
    },
    
    "recovery_strategies": {
        "retry_with_backoff": {
            "delays": [1, 2, 4, 8, 16],
            "jitter": True,
            "max_delay": 30
        },
        "reduce_batch_size": {
            "reduction_factor": 0.5,
            "min_size": 1
        },
        "fallback_widget": {
            "sequence": ["circle", "rectangle", "sticky_note"],
            "preserve_position": True
        },
        "skip_and_log": {
            "log_level": "error",
            "notify_user": True
        }
    }
}
```

## 2. Success Criteria and Metrics

```python
SUCCESS_CRITERIA = {
    "api_health": {
        "auth_success_rate": 95,  # %
        "api_response_time": 500,  # ms
        "rate_limit_headroom": 10  # requests
    },
    
    "visual_validation": {
        "body_template_visible": True,
        "sticky_notes_in_regions": 90,  # %
        "color_accuracy": 95,  # %
        "connection_visibility": 80  # %
    },
    
    "performance": {
        "batch_25_duration": 5000,  # ms
        "items_per_second": 5,
        "memory_usage": 500,  # MB
        "cpu_usage": 50  # %
    },
    
    "auto_healing": {
        "recovery_success_rate": 90,  # %
        "pattern_detection_accuracy": 85,  # %
        "fallback_effectiveness": 80,  # %
        "parameter_adjustment_accuracy": 75  # %
    },
    
    "reliability": {
        "test_completion_rate": 95,  # %
        "critical_test_pass_rate": 100,  # %
        "non_critical_test_pass_rate": 80,  # %
        "auto_heal_activation_rate": 30  # % (lower is better)
    }
}
```

## 3. Auto-Adjustment Rules

```python
class AutoAdjustmentEngine:
    """
    Learns from test results and automatically adjusts parameters
    """
    
    def __init__(self):
        self.pattern_history = []
        self.adjustment_rules = self._init_rules()
        self.confidence_threshold = 0.75
        
    def _init_rules(self):
        return {
            "batch_size_optimization": {
                "trigger": "batch_failure_pattern",
                "condition": lambda history: self._detect_batch_failures(history) > 3,
                "action": self._reduce_batch_size,
                "confidence_required": 0.8
            },
            
            "auth_method_selection": {
                "trigger": "auth_failure_pattern",
                "condition": lambda history: self._detect_auth_failures(history) > 2,
                "action": self._switch_auth_method,
                "confidence_required": 0.7
            },
            
            "rate_limit_adjustment": {
                "trigger": "rate_limit_pattern",
                "condition": lambda history: self._detect_rate_limits(history) > 1,
                "action": self._increase_delays,
                "confidence_required": 0.9
            },
            
            "widget_fallback_optimization": {
                "trigger": "widget_creation_failure",
                "condition": lambda history: self._detect_widget_failures(history) > 2,
                "action": self._optimize_fallbacks,
                "confidence_required": 0.75
            },
            
            "performance_tuning": {
                "trigger": "slow_performance",
                "condition": lambda history: self._detect_slow_operations(history),
                "action": self._tune_performance,
                "confidence_required": 0.6
            }
        }
    
    def analyze_and_adjust(self, test_results):
        """Analyze test results and make adjustments"""
        self.pattern_history.append(test_results)
        
        adjustments = []
        for rule_name, rule in self.adjustment_rules.items():
            if rule["condition"](self.pattern_history):
                confidence = self._calculate_confidence(rule_name)
                if confidence >= rule["confidence_required"]:
                    adjustment = rule["action"]()
                    adjustments.append({
                        "rule": rule_name,
                        "adjustment": adjustment,
                        "confidence": confidence
                    })
        
        return adjustments
    
    def _detect_batch_failures(self, history):
        """Detect pattern of batch processing failures"""
        if len(history) < 3:
            return 0
        
        recent = history[-5:]
        failures = [
            r for r in recent 
            if "batch" in r.get("operation", "") and not r.get("success", True)
        ]
        return len(failures)
    
    def _detect_auth_failures(self, history):
        """Detect pattern of authentication failures"""
        recent = history[-3:]
        return sum(1 for r in recent if r.get("state") == "AUTH" and not r.get("success"))
    
    def _detect_rate_limits(self, history):
        """Detect rate limiting patterns"""
        recent = history[-10:]
        return sum(1 for r in recent if r.get("error") == "rate_limit")
    
    def _detect_widget_failures(self, history):
        """Detect widget creation failures"""
        recent = history[-5:]
        widget_failures = {}
        for r in recent:
            if "create" in r.get("operation", "") and not r.get("success"):
                widget_type = r.get("metadata", {}).get("type")
                widget_failures[widget_type] = widget_failures.get(widget_type, 0) + 1
        return max(widget_failures.values()) if widget_failures else 0
    
    def _detect_slow_operations(self, history):
        """Detect performance degradation"""
        if len(history) < 5:
            return False
        
        recent = history[-5:]
        avg_duration = sum(r.get("duration", 0) for r in recent) / len(recent)
        return avg_duration > SUCCESS_CRITERIA["performance"]["batch_25_duration"] / 1000
    
    def _calculate_confidence(self, rule_name):
        """Calculate confidence score for an adjustment"""
        # Base confidence on pattern frequency and consistency
        relevant_data = [
            r for r in self.pattern_history[-10:]
            if self._is_relevant_to_rule(r, rule_name)
        ]
        
        if len(relevant_data) < 3:
            return 0.0
        
        # Calculate consistency of pattern
        success_rate = sum(1 for r in relevant_data if not r.get("success")) / len(relevant_data)
        recency_weight = 1.0 if len(self.pattern_history) > 10 else len(self.pattern_history) / 10
        
        return success_rate * recency_weight
    
    def _is_relevant_to_rule(self, result, rule_name):
        """Check if a result is relevant to a specific rule"""
        relevance_map = {
            "batch_size_optimization": lambda r: "batch" in r.get("operation", ""),
            "auth_method_selection": lambda r: r.get("state") == "AUTH",
            "rate_limit_adjustment": lambda r: r.get("error") == "rate_limit",
            "widget_fallback_optimization": lambda r: "create" in r.get("operation", ""),
            "performance_tuning": lambda r: r.get("duration", 0) > 0
        }
        
        check = relevance_map.get(rule_name)
        return check(result) if check else False
    
    def _reduce_batch_size(self):
        """Reduce batch size based on failures"""
        current = TEST_MATRIX["batch_sizes"]["optimal"]["size"]
        new_size = max(1, int(current * 0.5))
        
        return {
            "parameter": "batch_size",
            "old_value": current,
            "new_value": new_size,
            "reason": "Multiple batch failures detected"
        }
    
    def _switch_auth_method(self):
        """Switch to different authentication method"""
        current = TEST_MATRIX["operations"]["auth"]["methods"][0]
        methods = TEST_MATRIX["operations"]["auth"]["methods"]
        current_idx = methods.index(current)
        new_idx = (current_idx + 1) % len(methods)
        
        return {
            "parameter": "primary_auth_method",
            "old_value": current,
            "new_value": methods[new_idx],
            "reason": "Auth failures with current method"
        }
    
    def _increase_delays(self):
        """Increase delays to avoid rate limiting"""
        for size_config in TEST_MATRIX["batch_sizes"].values():
            size_config["delay_ms"] = int(size_config["delay_ms"] * 1.5)
        
        return {
            "parameter": "batch_delays",
            "old_value": "standard",
            "new_value": "increased_150%",
            "reason": "Rate limiting detected"
        }
    
    def _optimize_fallbacks(self):
        """Optimize widget fallback strategy"""
        # Analyze which widgets fail most
        widget_stats = {}
        for r in self.pattern_history[-20:]:
            if "create" in r.get("operation", ""):
                widget = r.get("metadata", {}).get("type")
                if widget:
                    if widget not in widget_stats:
                        widget_stats[widget] = {"success": 0, "failure": 0}
                    if r.get("success"):
                        widget_stats[widget]["success"] += 1
                    else:
                        widget_stats[widget]["failure"] += 1
        
        # Skip widgets with high failure rates
        skip_widgets = []
        for widget, stats in widget_stats.items():
            total = stats["success"] + stats["failure"]
            if total > 0 and stats["failure"] / total > 0.5:
                skip_widgets.append(widget)
        
        return {
            "parameter": "skip_widgets",
            "old_value": [],
            "new_value": skip_widgets,
            "reason": f"High failure rate for {skip_widgets}"
        }
    
    def _tune_performance(self):
        """Tune performance parameters"""
        return {
            "parameter": "parallel_agents",
            "old_value": 4,
            "new_value": 2,
            "reason": "Reduce parallel operations to improve stability"
        }
```

## 4. Real-Time Monitoring Dashboard

```python
class TestMonitoringDashboard:
    """
    Real-time monitoring of test execution
    """
    
    def __init__(self):
        self.metrics = {
            "current_state": "INIT",
            "tests_completed": 0,
            "tests_failed": 0,
            "auto_heals": 0,
            "current_batch_size": 25,
            "api_health": "unknown",
            "performance": {}
        }
        self.start_time = None
        
    def update(self, test_result):
        """Update dashboard with latest test result"""
        if test_result.success:
            self.metrics["tests_completed"] += 1
        else:
            self.metrics["tests_failed"] += 1
        
        if test_result.auto_healed:
            self.metrics["auto_heals"] += 1
        
        self.metrics["current_state"] = test_result.state.value
        
        # Update performance metrics
        if "batch" in test_result.operation:
            size = test_result.metadata.get("size", 0)
            duration = test_result.duration
            if size > 0 and duration > 0:
                self.metrics["performance"]["items_per_second"] = size / duration
    
    def get_dashboard(self):
        """Generate dashboard output"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        success_rate = (
            self.metrics["tests_completed"] / 
            (self.metrics["tests_completed"] + self.metrics["tests_failed"])
            if (self.metrics["tests_completed"] + self.metrics["tests_failed"]) > 0
            else 0
        )
        
        return f"""
╔══════════════════════════════════════════════════════════╗
║             MURAL API TEST MONITORING DASHBOARD           ║
╠══════════════════════════════════════════════════════════╣
║ Current State: {self.metrics['current_state']:20}                   ║
║ Elapsed Time:  {elapsed:6.1f}s                                ║
╠══════════════════════════════════════════════════════════╣
║ Tests Completed: {self.metrics['tests_completed']:4}  │ Failed: {self.metrics['tests_failed']:4}  │ Rate: {success_rate*100:5.1f}% ║
║ Auto-Heals:      {self.metrics['auto_heals']:4}  │ Batch Size: {self.metrics['current_batch_size']:3}           ║
╠══════════════════════════════════════════════════════════╣
║ Performance:                                              ║
║   Items/Second: {self.metrics['performance'].get('items_per_second', 0):6.2f}                              ║
║   API Health:   {self.metrics['api_health']:20}                  ║
╚══════════════════════════════════════════════════════════╝
        """
```

## 5. Test Scenario Definitions

```json
{
  "test_scenarios": [
    {
      "name": "basic_authentication",
      "description": "Test all authentication methods",
      "priority": 1,
      "critical": true,
      "steps": [
        {"action": "test_oauth", "expected": "token_received"},
        {"action": "test_api_key", "expected": "authenticated"},
        {"action": "test_refresh", "expected": "token_refreshed"}
      ]
    },
    {
      "name": "body_template_creation",
      "description": "Create complete body visualization",
      "priority": 1,
      "critical": true,
      "steps": [
        {"action": "create_head_circle", "fallback": "create_head_rectangle"},
        {"action": "create_torso_rectangle", "fallback": "create_torso_sticky"},
        {"action": "create_arms_rectangles", "fallback": "create_arm_stickies"},
        {"action": "create_legs_rectangles", "fallback": "create_leg_stickies"},
        {"action": "create_heart_circle", "fallback": "create_heart_sticky"}
      ]
    },
    {
      "name": "batch_optimization",
      "description": "Find optimal batch size",
      "priority": 2,
      "critical": false,
      "steps": [
        {"action": "test_batch_1", "measure": "duration"},
        {"action": "test_batch_10", "measure": "duration"},
        {"action": "test_batch_25", "measure": "duration"},
        {"action": "test_batch_50", "measure": "duration"},
        {"action": "test_batch_100", "measure": "duration"}
      ]
    },
    {
      "name": "somatic_mapping",
      "description": "Test sticky note placement in body regions",
      "priority": 2,
      "critical": false,
      "steps": [
        {"action": "place_head_note", "themes": ["thoughts", "awareness"]},
        {"action": "place_heart_note", "themes": ["emotions", "love"]},
        {"action": "place_torso_note", "themes": ["breathing", "core"]},
        {"action": "place_limb_notes", "themes": ["movement", "action"]}
      ]
    },
    {
      "name": "visual_validation",
      "description": "Validate visual output",
      "priority": 3,
      "critical": false,
      "steps": [
        {"action": "capture_screenshot", "expected": "image_data"},
        {"action": "verify_body_template", "expected": "shapes_visible"},
        {"action": "verify_sticky_placement", "expected": "correct_regions"},
        {"action": "verify_color_coding", "expected": "tdai_colors"}
      ]
    },
    {
      "name": "stress_test",
      "description": "Test system limits",
      "priority": 4,
      "critical": false,
      "steps": [
        {"action": "rapid_fire_creation", "count": 100, "delay": 0},
        {"action": "concurrent_operations", "threads": 5},
        {"action": "large_text_content", "size": "10KB"},
        {"action": "maximum_widgets", "count": 1000}
      ]
    }
  ]
}
```

## 6. Success Metrics Summary

```yaml
minimum_viable_success:
  authentication: One method succeeds
  body_template: 5 of 7 body parts created
  sticky_notes: Can create and place notes
  batch_processing: Works with any batch size
  visual_output: Body visualization recognizable

optimal_success:
  authentication: OAuth works smoothly
  body_template: All shapes created as designed
  sticky_notes: Correctly mapped to regions with TDAI colors
  batch_processing: 25-30 items processed efficiently
  visual_output: Professional, editorial-ready visualization

excellence_criteria:
  authentication: All methods work with fallback
  body_template: Complex shapes with connections
  sticky_notes: Dynamic clustering and organization
  batch_processing: Adaptive optimization in real-time
  visual_output: Interactive, animated visualization
```

## Key Features

### Comprehensive Coverage
- **5 Dimensions**: Operations × Widget Types × Batch Sizes × Failures × Recovery
- **Auto-Learning**: Patterns detected and parameters adjusted
- **Real-Time Monitoring**: Live dashboard during testing
- **Scenario-Based**: Predefined test scenarios with priorities

### Intelligent Adjustment
- **Pattern Recognition**: Identifies failure patterns
- **Confidence Scoring**: Adjustments made with confidence thresholds
- **Progressive Optimization**: Continuous improvement during testing
- **Fallback Strategies**: Multiple layers of recovery options

### Production Ready
- **Success Criteria**: Clear metrics for go/no-go decisions
- **Performance Baselines**: Expected performance parameters
- **Stress Testing**: Identifies system limits
- **Documentation**: All learnings captured for future reference

This comprehensive testing parameter system ensures thorough validation with minimal manual intervention while continuously improving based on observed patterns.
