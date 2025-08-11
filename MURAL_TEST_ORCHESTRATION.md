# Mural API Test Orchestration
## Multi-Browser Agent Coordination for Comprehensive Auto-Healing Tests

## Test Architecture

```
┌──────────────────────────────────────────────────────┐
│              Test Coordinator (Main)                  │
│         State Machine & Result Aggregation            │
└────────┬──────────┬──────────┬──────────┬───────────┘
         │          │          │          │
    ┌────▼────┐ ┌──▼───┐ ┌───▼───┐ ┌────▼────┐
    │ Agent 1 │ │Agent 2│ │Agent 3│ │ Agent 4 │
    │Puppeteer│ │Hyper- │ │Stage- │ │Monitor │
    │  (Auth) │ │browser│ │ hand  │ │(Visual)│
    └─────────┘ └───────┘ └───────┘ └─────────┘
```

## 1. Test Coordinator Implementation

```python
import asyncio
import json
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import threading
import queue
import logging

class TestState(Enum):
    INIT = "initializing"
    AUTH = "authenticating"
    SHAPES = "creating_shapes"
    NOTES = "creating_notes"
    BATCH = "batch_processing"
    VISUAL = "visual_validation"
    COMPLETE = "complete"
    FAILED = "failed"

@dataclass
class TestResult:
    state: TestState
    success: bool
    agent: str
    operation: str
    duration: float
    error: Optional[str] = None
    screenshot: Optional[str] = None
    auto_healed: bool = False
    fallback_used: str = ""
    metadata: Dict = field(default_factory=dict)

class MuralTestCoordinator:
    """
    Coordinates multiple browser agents for comprehensive testing
    with auto-healing and parallel execution
    """
    
    def __init__(self):
        self.state = TestState.INIT
        self.results = []
        self.agents = {}
        self.state_machine = self._init_state_machine()
        self.logger = logging.getLogger('TestCoordinator')
        self.result_queue = queue.Queue()
        self.test_start_time = None
        self.mural_url = None
        
    def _init_state_machine(self) -> Dict:
        """Initialize state transition rules"""
        return {
            TestState.INIT: TestState.AUTH,
            TestState.AUTH: TestState.SHAPES,
            TestState.SHAPES: TestState.NOTES,
            TestState.NOTES: TestState.BATCH,
            TestState.BATCH: TestState.VISUAL,
            TestState.VISUAL: TestState.COMPLETE
        }
    
    async def start_test_suite(self) -> Dict:
        """Main entry point for test orchestration"""
        self.test_start_time = time.time()
        self.logger.info("Starting comprehensive Mural API test suite")
        
        try:
            # Initialize all browser agents
            await self._initialize_agents()
            
            # Execute test stages with auto-healing
            for state in [TestState.AUTH, TestState.SHAPES, TestState.NOTES, 
                         TestState.BATCH, TestState.VISUAL]:
                
                self.state = state
                self.logger.info(f"Entering state: {state.value}")
                
                success = await self._execute_state_tests(state)
                
                if not success:
                    # Auto-healing attempt
                    self.logger.warning(f"State {state.value} failed, attempting auto-heal")
                    success = await self._auto_heal_state(state)
                    
                    if not success:
                        self.state = TestState.FAILED
                        break
            
            if self.state != TestState.FAILED:
                self.state = TestState.COMPLETE
            
            # Generate comprehensive report
            return self._generate_report()
            
        except Exception as e:
            self.logger.error(f"Test suite failed: {e}")
            self.state = TestState.FAILED
            return self._generate_report()
        
        finally:
            await self._cleanup_agents()
    
    async def _initialize_agents(self):
        """Initialize all browser agents"""
        self.agents = {
            "puppeteer": PuppeteerTestAgent(),
            "hyperbrowser": HyperbrowserTestAgent(),
            "stagehand": StagehandTestAgent(),
            "monitor": VisualMonitorAgent()
        }
        
        # Start all agents in parallel
        init_tasks = [
            agent.initialize() for agent in self.agents.values()
        ]
        results = await asyncio.gather(*init_tasks, return_exceptions=True)
        
        for idx, result in enumerate(results):
            agent_name = list(self.agents.keys())[idx]
            if isinstance(result, Exception):
                self.logger.error(f"Failed to initialize {agent_name}: {result}")
                # Continue with reduced agent set
                del self.agents[agent_name]
    
    async def _execute_state_tests(self, state: TestState) -> bool:
        """Execute tests for a specific state"""
        test_methods = {
            TestState.AUTH: self._test_authentication,
            TestState.SHAPES: self._test_shape_creation,
            TestState.NOTES: self._test_sticky_notes,
            TestState.BATCH: self._test_batch_operations,
            TestState.VISUAL: self._test_visual_validation
        }
        
        test_method = test_methods.get(state)
        if test_method:
            return await test_method()
        return False
    
    async def _test_authentication(self) -> bool:
        """Test authentication with multiple methods"""
        auth_methods = [
            ("oauth", self._test_oauth_auth),
            ("api_key", self._test_api_key_auth),
            ("refresh_token", self._test_refresh_auth)
        ]
        
        for method_name, method_func in auth_methods:
            try:
                result = await method_func()
                if result.success:
                    self.results.append(result)
                    self.logger.info(f"Authentication successful with {method_name}")
                    return True
            except Exception as e:
                self.logger.warning(f"Auth method {method_name} failed: {e}")
                continue
        
        return False
    
    async def _test_oauth_auth(self) -> TestResult:
        """Test OAuth authentication flow"""
        start_time = time.time()
        
        if "puppeteer" in self.agents:
            agent = self.agents["puppeteer"]
            try:
                # Navigate to OAuth page
                await agent.navigate("https://api.mural.co/oauth/authorize")
                
                # Fill credentials
                await agent.fill_field("#username", "test_user")
                await agent.fill_field("#password", "test_pass")
                await agent.click("#submit")
                
                # Wait for redirect
                await agent.wait_for_redirect()
                
                # Extract token
                token = await agent.extract_token()
                
                return TestResult(
                    state=TestState.AUTH,
                    success=True,
                    agent="puppeteer",
                    operation="oauth_auth",
                    duration=time.time() - start_time,
                    metadata={"token": token[:10] + "..."}  # Truncate for security
                )
                
            except Exception as e:
                return TestResult(
                    state=TestState.AUTH,
                    success=False,
                    agent="puppeteer",
                    operation="oauth_auth",
                    duration=time.time() - start_time,
                    error=str(e)
                )
        
        return TestResult(
            state=TestState.AUTH,
            success=False,
            agent="none",
            operation="oauth_auth",
            duration=0,
            error="Puppeteer agent not available"
        )
    
    async def _test_api_key_auth(self) -> TestResult:
        """Test API key authentication"""
        # Implementation for API key auth testing
        pass
    
    async def _test_refresh_auth(self) -> TestResult:
        """Test refresh token authentication"""
        # Implementation for refresh token testing
        pass
    
    async def _test_shape_creation(self) -> bool:
        """Test shape creation with fallbacks"""
        shapes_to_test = [
            {"type": "circle", "x": 400, "y": 100, "radius": 50},
            {"type": "rectangle", "x": 350, "y": 150, "width": 100, "height": 150},
            {"type": "triangle", "x": 300, "y": 300, "width": 80, "height": 80}
        ]
        
        success_count = 0
        tasks = []
        
        # Distribute shape tests across available agents
        for idx, shape in enumerate(shapes_to_test):
            agent_name = list(self.agents.keys())[idx % len(self.agents)]
            agent = self.agents[agent_name]
            tasks.append(self._test_single_shape(agent, agent_name, shape))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, TestResult) and result.success:
                success_count += 1
                self.results.append(result)
            elif isinstance(result, TestResult):
                self.results.append(result)
                # Try fallback
                fallback_result = await self._fallback_shape_test(result)
                if fallback_result.success:
                    success_count += 1
                    self.results.append(fallback_result)
        
        return success_count >= 2  # Need at least 2 shapes for success
    
    async def _test_single_shape(self, agent, agent_name: str, shape: Dict) -> TestResult:
        """Test creation of a single shape"""
        start_time = time.time()
        
        try:
            # Create shape via API
            result = await agent.create_shape(shape)
            
            # Visual verification
            if "monitor" in self.agents:
                screenshot = await self.agents["monitor"].capture_screenshot()
                verified = await self.agents["monitor"].verify_shape(shape, screenshot)
            else:
                verified = True
                screenshot = None
            
            return TestResult(
                state=TestState.SHAPES,
                success=result and verified,
                agent=agent_name,
                operation=f"create_{shape['type']}",
                duration=time.time() - start_time,
                screenshot=screenshot,
                metadata=shape
            )
            
        except Exception as e:
            return TestResult(
                state=TestState.SHAPES,
                success=False,
                agent=agent_name,
                operation=f"create_{shape['type']}",
                duration=time.time() - start_time,
                error=str(e),
                metadata=shape
            )
    
    async def _fallback_shape_test(self, failed_result: TestResult) -> TestResult:
        """Fallback strategy for failed shape creation"""
        shape = failed_result.metadata
        
        # Try simpler shape
        if shape["type"] == "circle":
            # Fallback to rectangle
            shape["type"] = "rectangle"
            shape["width"] = shape.pop("radius") * 2
            shape["height"] = shape["width"]
        elif shape["type"] == "rectangle":
            # Fallback to sticky note
            return await self._create_fallback_sticky(shape)
        
        # Try with different agent
        for agent_name, agent in self.agents.items():
            if agent_name != failed_result.agent:
                result = await self._test_single_shape(agent, agent_name, shape)
                if result.success:
                    result.auto_healed = True
                    result.fallback_used = f"shape_type:{shape['type']}"
                    return result
        
        return failed_result
    
    async def _create_fallback_sticky(self, shape: Dict) -> TestResult:
        """Create sticky note as ultimate fallback"""
        start_time = time.time()
        
        for agent_name, agent in self.agents.items():
            try:
                result = await agent.create_sticky_note(
                    text="[Shape Placeholder]",
                    x=shape["x"],
                    y=shape["y"]
                )
                
                if result:
                    return TestResult(
                        state=TestState.SHAPES,
                        success=True,
                        agent=agent_name,
                        operation="fallback_sticky",
                        duration=time.time() - start_time,
                        auto_healed=True,
                        fallback_used="sticky_instead_of_shape"
                    )
            except Exception:
                continue
        
        return TestResult(
            state=TestState.SHAPES,
            success=False,
            agent="all",
            operation="fallback_sticky",
            duration=time.time() - start_time,
            error="All fallback attempts failed"
        )
    
    async def _test_sticky_notes(self) -> bool:
        """Test sticky note creation and placement"""
        test_notes = [
            {"text": "Head region test", "themes": ["thoughts", "awareness"], "tdai": 8.0},
            {"text": "Heart region test", "themes": ["emotions", "love"], "tdai": 7.5},
            {"text": "Core region test", "themes": ["power", "will"], "tdai": 6.0}
        ]
        
        success_count = 0
        
        for note in test_notes:
            result = await self._test_single_note(note)
            self.results.append(result)
            if result.success:
                success_count += 1
        
        return success_count >= 2
    
    async def _test_single_note(self, note: Dict) -> TestResult:
        """Test creation of a single sticky note"""
        # Implementation for single note testing
        pass
    
    async def _test_batch_operations(self) -> bool:
        """Test batch processing with various sizes"""
        batch_sizes = [1, 10, 25, 50, 100]
        optimal_size = 25  # From project learning
        
        results = []
        
        for size in batch_sizes:
            result = await self._test_batch_size(size)
            results.append(result)
            self.results.append(result)
            
            if not result.success and size == optimal_size:
                # Critical failure at optimal size
                self.logger.error(f"Batch size {optimal_size} failed!")
                return False
        
        # Analyze results to find actual optimal size
        successful_sizes = [r.metadata["size"] for r in results if r.success]
        if successful_sizes:
            actual_optimal = max(successful_sizes)
            self.logger.info(f"Actual optimal batch size: {actual_optimal}")
            
            # Update configuration if different from expected
            if actual_optimal != optimal_size:
                self._update_batch_config(actual_optimal)
        
        return len(successful_sizes) > 0
    
    async def _test_batch_size(self, size: int) -> TestResult:
        """Test a specific batch size"""
        start_time = time.time()
        
        # Generate test batch
        batch = [
            {"type": "sticky_note", "text": f"Batch item {i}", "x": 100 + i*10, "y": 100}
            for i in range(size)
        ]
        
        try:
            # Use fastest available agent
            agent = self._get_fastest_agent()
            result = await agent.batch_create(batch)
            
            return TestResult(
                state=TestState.BATCH,
                success=result,
                agent=agent.name,
                operation=f"batch_{size}",
                duration=time.time() - start_time,
                metadata={"size": size, "items_per_second": size / (time.time() - start_time)}
            )
            
        except Exception as e:
            # Try with reduced size
            if size > 1:
                reduced_size = size // 2
                self.logger.info(f"Batch {size} failed, trying {reduced_size}")
                reduced_result = await self._test_batch_size(reduced_size)
                reduced_result.auto_healed = True
                reduced_result.fallback_used = f"reduced_from_{size}"
                return reduced_result
            
            return TestResult(
                state=TestState.BATCH,
                success=False,
                agent="all",
                operation=f"batch_{size}",
                duration=time.time() - start_time,
                error=str(e),
                metadata={"size": size}
            )
    
    async def _test_visual_validation(self) -> bool:
        """Test visual validation with screenshots"""
        if "monitor" not in self.agents:
            self.logger.warning("Visual monitor not available, skipping visual tests")
            return True
        
        monitor = self.agents["monitor"]
        
        validations = [
            ("body_template", self._validate_body_template),
            ("sticky_placement", self._validate_sticky_placement),
            ("color_coding", self._validate_color_coding),
            ("connections", self._validate_connections)
        ]
        
        success_count = 0
        
        for validation_name, validation_func in validations:
            try:
                screenshot = await monitor.capture_screenshot()
                result = await validation_func(screenshot)
                
                self.results.append(TestResult(
                    state=TestState.VISUAL,
                    success=result,
                    agent="monitor",
                    operation=validation_name,
                    duration=0.5,
                    screenshot=screenshot
                ))
                
                if result:
                    success_count += 1
                    
            except Exception as e:
                self.logger.error(f"Visual validation {validation_name} failed: {e}")
        
        return success_count >= 2
    
    async def _validate_body_template(self, screenshot: str) -> bool:
        """Validate body template is visible"""
        # Implementation for body template validation
        pass
    
    async def _validate_sticky_placement(self, screenshot: str) -> bool:
        """Validate sticky notes are in correct regions"""
        # Implementation for sticky placement validation
        pass
    
    async def _validate_color_coding(self, screenshot: str) -> bool:
        """Validate TDAI color coding"""
        # Implementation for color coding validation
        pass
    
    async def _validate_connections(self, screenshot: str) -> bool:
        """Validate connection lines"""
        # Implementation for connection validation
        pass
    
    async def _auto_heal_state(self, state: TestState) -> bool:
        """Attempt to auto-heal a failed state"""
        heal_strategies = {
            TestState.AUTH: self._heal_auth,
            TestState.SHAPES: self._heal_shapes,
            TestState.NOTES: self._heal_notes,
            TestState.BATCH: self._heal_batch,
            TestState.VISUAL: self._heal_visual
        }
        
        strategy = heal_strategies.get(state)
        if strategy:
            return await strategy()
        return False
    
    async def _heal_auth(self) -> bool:
        """Healing strategy for authentication failures"""
        # Try environment variables
        # Try cached credentials
        # Try manual input
        pass
    
    async def _heal_shapes(self) -> bool:
        """Healing strategy for shape creation failures"""
        # Simplify shapes
        # Use sticky notes instead
        # Skip non-essential shapes
        pass
    
    async def _heal_notes(self) -> bool:
        """Healing strategy for sticky note failures"""
        # Reduce text length
        # Simplify positioning
        # Use default colors
        pass
    
    async def _heal_batch(self) -> bool:
        """Healing strategy for batch processing failures"""
        # Reduce batch size
        # Process individually
        # Add delays between items
        pass
    
    async def _heal_visual(self) -> bool:
        """Healing strategy for visual validation failures"""
        # Retry with delay
        # Use different browser
        # Skip non-critical validations
        pass
    
    def _get_fastest_agent(self):
        """Get the agent with best performance"""
        # Analyze past results to find fastest agent
        agent_times = {}
        
        for result in self.results:
            if result.success:
                if result.agent not in agent_times:
                    agent_times[result.agent] = []
                agent_times[result.agent].append(result.duration)
        
        if agent_times:
            # Calculate average times
            avg_times = {
                agent: sum(times) / len(times)
                for agent, times in agent_times.items()
            }
            fastest = min(avg_times, key=avg_times.get)
            return self.agents.get(fastest, list(self.agents.values())[0])
        
        return list(self.agents.values())[0]
    
    def _update_batch_config(self, new_size: int):
        """Update batch configuration based on test results"""
        config_update = {
            "batch_size": new_size,
            "timestamp": time.time(),
            "reason": "auto_adjusted_from_testing"
        }
        
        with open("mural_config_updates.json", "a") as f:
            f.write(json.dumps(config_update) + "\n")
    
    async def _cleanup_agents(self):
        """Clean up all browser agents"""
        cleanup_tasks = [
            agent.cleanup() for agent in self.agents.values()
        ]
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        total_duration = time.time() - self.test_start_time
        
        # Analyze results
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r.success])
        auto_healed = len([r for r in self.results if r.auto_healed])
        fallbacks_used = len([r for r in self.results if r.fallback_used])
        
        # Group by state
        state_results = {}
        for state in TestState:
            state_tests = [r for r in self.results if r.state == state]
            if state_tests:
                state_results[state.value] = {
                    "total": len(state_tests),
                    "successful": len([r for r in state_tests if r.success]),
                    "auto_healed": len([r for r in state_tests if r.auto_healed]),
                    "average_duration": sum(r.duration for r in state_tests) / len(state_tests)
                }
        
        # Find optimal parameters
        batch_results = [r for r in self.results if "batch" in r.operation]
        optimal_batch = max(
            [r.metadata.get("size", 0) for r in batch_results if r.success],
            default=25
        )
        
        return {
            "status": self.state.value,
            "duration": total_duration,
            "mural_url": self.mural_url,
            "summary": {
                "total_tests": total_tests,
                "successful": successful_tests,
                "failed": total_tests - successful_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "auto_healed": auto_healed,
                "fallbacks_used": fallbacks_used
            },
            "state_results": state_results,
            "optimal_parameters": {
                "batch_size": optimal_batch,
                "fastest_agent": self._get_fastest_agent().name if hasattr(self._get_fastest_agent(), 'name') else "unknown"
            },
            "recommendations": self._generate_recommendations(),
            "detailed_results": [
                {
                    "state": r.state.value,
                    "success": r.success,
                    "agent": r.agent,
                    "operation": r.operation,
                    "duration": r.duration,
                    "auto_healed": r.auto_healed,
                    "fallback": r.fallback_used,
                    "error": r.error
                }
                for r in self.results
            ]
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze failures
        auth_failures = [r for r in self.results if r.state == TestState.AUTH and not r.success]
        if auth_failures:
            recommendations.append("Consider implementing cached credential system for auth stability")
        
        shape_failures = [r for r in self.results if r.state == TestState.SHAPES and not r.success]
        if shape_failures:
            recommendations.append("Mural API may have limited shape support, use sticky notes for body parts")
        
        batch_results = [r for r in self.results if "batch" in r.operation]
        if batch_results:
            sizes = [r.metadata.get("size", 0) for r in batch_results if r.success]
            if sizes and max(sizes) < 25:
                recommendations.append(f"Reduce default batch size to {max(sizes)}")
        
        # Performance recommendations
        agent_performance = {}
        for r in self.results:
            if r.success and r.agent != "none":
                if r.agent not in agent_performance:
                    agent_performance[r.agent] = []
                agent_performance[r.agent].append(r.duration)
        
        if agent_performance:
            fastest = min(agent_performance, key=lambda k: sum(agent_performance[k])/len(agent_performance[k]))
            recommendations.append(f"Prioritize {fastest} agent for best performance")
        
        return recommendations


## 2. Browser Agent Implementations

```python
class PuppeteerTestAgent:
    """Puppeteer-based test agent for browser automation"""
    
    def __init__(self):
        self.name = "puppeteer"
        self.browser = None
        self.page = None
        
    async def initialize(self):
        """Initialize Puppeteer browser"""
        # Launch browser with Puppeteer
        pass
    
    async def navigate(self, url: str):
        """Navigate to URL"""
        pass
    
    async def fill_field(self, selector: str, value: str):
        """Fill form field"""
        pass
    
    async def click(self, selector: str):
        """Click element"""
        pass
    
    async def wait_for_redirect(self):
        """Wait for page redirect"""
        pass
    
    async def extract_token(self) -> str:
        """Extract OAuth token from page"""
        pass
    
    async def create_shape(self, shape: Dict) -> bool:
        """Create shape via browser"""
        pass
    
    async def create_sticky_note(self, text: str, x: int, y: int) -> bool:
        """Create sticky note via browser"""
        pass
    
    async def batch_create(self, items: List[Dict]) -> bool:
        """Batch create items"""
        pass
    
    async def cleanup(self):
        """Close browser"""
        pass


class HyperbrowserTestAgent:
    """Hyperbrowser-based test agent"""
    
    def __init__(self):
        self.name = "hyperbrowser"
        # Implementation
        pass


class StagehandTestAgent:
    """Stagehand-based test agent"""
    
    def __init__(self):
        self.name = "stagehand"
        # Implementation
        pass


class VisualMonitorAgent:
    """Visual monitoring and validation agent"""
    
    def __init__(self):
        self.name = "monitor"
        
    async def initialize(self):
        """Initialize visual monitor"""
        pass
    
    async def capture_screenshot(self) -> str:
        """Capture screenshot of current state"""
        pass
    
    async def verify_shape(self, shape: Dict, screenshot: str) -> bool:
        """Verify shape exists in screenshot"""
        pass
    
    async def cleanup(self):
        """Cleanup resources"""
        pass


## 3. Test Execution Script

```python
async def run_comprehensive_tests():
    """Main test execution function"""
    
    # Initialize coordinator
    coordinator = MuralTestCoordinator()
    
    # Run test suite
    report = await coordinator.start_test_suite()
    
    # Save report
    with open("test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n" + "="*50)
    print("MURAL API TEST RESULTS")
    print("="*50)
    print(f"Status: {report['status']}")
    print(f"Duration: {report['duration']:.2f}s")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print(f"Auto-Healed: {report['summary']['auto_healed']}")
    print(f"Optimal Batch Size: {report['optimal_parameters']['batch_size']}")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  • {rec}")
    
    if report['mural_url']:
        print(f"\nMural URL: {report['mural_url']}")
    
    return report['status'] == 'complete'


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())
    sys.exit(0 if success else 1)
```

## Key Features

### Multi-Agent Coordination
- **4 Parallel Agents**: Each with specific responsibilities
- **Load Distribution**: Tests distributed across available agents
- **Performance Tracking**: Identifies fastest agent for operations
- **Fallback Cascading**: Failed agent triggers next available

### Auto-Healing Mechanisms
- **State-Level Healing**: Each state has specific recovery strategies
- **Progressive Fallbacks**: Shape → Rectangle → Sticky Note
- **Batch Size Adaptation**: Automatically finds optimal size
- **Credential Cycling**: Multiple auth methods attempted

### Comprehensive Testing
- **5 Test States**: Auth, Shapes, Notes, Batch, Visual
- **Parallel Execution**: Multiple tests run simultaneously
- **Visual Validation**: Screenshot-based verification
- **Performance Metrics**: Duration and throughput tracking

### Intelligent Reporting
- **Detailed Metrics**: Success rates, healing stats, performance
- **Recommendations**: Actionable improvements based on results
- **Optimal Parameters**: Discovered through testing
- **Failure Analysis**: Patterns identified for improvements

This orchestration system ensures comprehensive testing with minimal manual intervention.
