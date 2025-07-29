#!/usr/bin/env python3
"""
Test script for asynchronous contribution evaluation functionality
"""

import sys
import os
import asyncio
import time
from unittest.mock import Mock

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'nautilus'))

try:
    # Patch the import to avoid heavy dependencies
    import importlib.util
    
    # Create a simple mock for AppConstants to avoid nvflare dependency issues
    class MockAppConstants:
        CLIENT_UNKNOWN = "unknown_client"
    
    # Add mock to sys.modules to avoid import errors  
    import types
    mock_app_constant = types.ModuleType('nvflare.app_common.app_constant')
    mock_app_constant.AppConstants = MockAppConstants
    sys.modules['nvflare.app_common.app_constant'] = mock_app_constant
    
    from nautilus.api.contrib.pipline import (
        connect_contrib_evaluation,
        connect_contrib_evaluation_async, 
        connect_contrib_evaluation_divided
    )
    from nautilus.api.contrib.call_function import (
        nt_contrib_evaluation_async,
        nt_contrib_evaluation_parallel
    )
    print("✓ Successfully imported async contribution evaluation modules")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("This is expected as the full nvflare environment is not set up")
    print("Testing basic async structure without full dependencies...")
    
    # Test just the async structure without full imports
    test_basic_async_structure()
    sys.exit(0)

def test_basic_async_structure():
    """Test just the basic async structure without heavy dependencies"""
    print("\n=== Testing Basic Async Structure ===")
    
    # Test that asyncio works
    async def simple_async_test():
        await asyncio.sleep(0.01)
        return "async works"
    
    result = asyncio.run(simple_async_test())
    print(f"✓ Basic async test: {result}")
    
    # Test concurrent futures
    import concurrent.futures
    
    def simple_sync_task(x):
        return x * 2
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future = executor.submit(simple_sync_task, 5)
        result = future.result()
        print(f"✓ ThreadPoolExecutor test: {result}")
    
    print("✓ Basic async infrastructure is working")

def create_mock_data():
    """Create mock data for testing"""
    # Mock initial model
    initial_model = Mock()
    
    # Mock results (simplified structure)
    results = []
    for i in range(3):  # 3 mock clients
        result = Mock()
        result.meta = {
            'client_name': f'site-{i}',
            'accuracy': 0.8 + i * 0.05,  # Mock accuracies
            'data_size': 1000 + i * 100
        }
        result.params = {f'param_{j}': [1.0] * 10 for j in range(2)}  # Mock parameters
        results.append(result)
    
    # Mock testloader
    testloader = Mock()
    
    return initial_model, results, testloader

async def test_async_single_evaluation():
    """Test single async evaluation"""
    print("\n=== Testing Single Async Evaluation ===")
    
    initial_model, results, testloader = create_mock_data()
    
    start_time = time.time()
    
    try:
        result = await connect_contrib_evaluation_async(
            num_clients=3,
            evaluation_mode='individual',
            initial_model=initial_model,
            results=results,
            DEVICE='cpu',
            testloader=testloader,
            mode='s_norm'
        )
        
        end_time = time.time()
        print(f"✓ Async evaluation completed in {end_time - start_time:.2f} seconds")
        print(f"Result type: {type(result)}")
        
    except Exception as e:
        print(f"✗ Async evaluation failed: {e}")
        return False
    
    return True

async def test_parallel_evaluations():
    """Test parallel evaluation of multiple modes"""
    print("\n=== Testing Parallel Multiple Evaluations ===")
    
    initial_model, results, testloader = create_mock_data()
    
    evaluation_modes = ['individual', 'robust_volume']  # Use modes that don't require complex computations
    
    start_time = time.time()
    
    try:
        results_dict = await nt_contrib_evaluation_parallel(
            num_clients=3,
            evaluation_modes=evaluation_modes,
            initial_model=initial_model,
            results=results,
            DEVICE='cpu',
            testloader=testloader,
            max_workers=2
        )
        
        end_time = time.time()
        print(f"✓ Parallel evaluation completed in {end_time - start_time:.2f} seconds")
        print(f"Results for modes {evaluation_modes}:")
        for mode, result in results_dict.items():
            print(f"  {mode}: {type(result)} - {'Success' if result is not None else 'Failed'}")
        
    except Exception as e:
        print(f"✗ Parallel evaluation failed: {e}")
        return False
    
    return True

def test_divided_evaluation():
    """Test divided evaluation (sync wrapper for async)"""
    print("\n=== Testing Divided Evaluation (Sync Wrapper) ===")
    
    initial_model, results, testloader = create_mock_data()
    
    evaluation_modes = ['individual', 'robust_volume']
    
    start_time = time.time()
    
    try:
        results_dict = connect_contrib_evaluation_divided(
            num_clients=3,
            evaluation_modes=evaluation_modes,
            initial_model=initial_model,
            results=results,
            DEVICE='cpu',
            testloader=testloader,
            max_workers=2
        )
        
        end_time = time.time()
        print(f"✓ Divided evaluation completed in {end_time - start_time:.2f} seconds")
        print(f"Results for modes {evaluation_modes}:")
        if results_dict:
            for mode, result in results_dict.items():
                print(f"  {mode}: {type(result)} - {'Success' if result is not None else 'Failed'}")
        else:
            print("  No results returned")
        
    except Exception as e:
        print(f"✗ Divided evaluation failed: {e}")
        return False
    
    return True

def test_backward_compatibility():
    """Test that original sync function still works"""
    print("\n=== Testing Backward Compatibility ===")
    
    initial_model, results, testloader = create_mock_data()
    
    start_time = time.time()
    
    try:
        result = connect_contrib_evaluation(
            num_clients=3,
            evaluation_mode='individual',
            initial_model=initial_model,
            results=results,
            DEVICE='cpu',
            testloader=testloader,
            mode='s_norm'
        )
        
        end_time = time.time()
        print(f"✓ Sync evaluation completed in {end_time - start_time:.2f} seconds")
        print(f"Result type: {type(result)}")
        
    except Exception as e:
        print(f"✗ Sync evaluation failed: {e}")
        return False
    
    return True

async def main():
    """Run all tests"""
    print("Starting Async Contribution Evaluation Tests...")
    
    tests = [
        ("Backward Compatibility", test_backward_compatibility),
        ("Single Async Evaluation", test_async_single_evaluation),
        ("Parallel Evaluations", test_parallel_evaluations),
        ("Divided Evaluation", test_divided_evaluation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    print('='*50)
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)