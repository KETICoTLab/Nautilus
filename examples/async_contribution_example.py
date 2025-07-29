#!/usr/bin/env python3
"""
Example usage of asynchronous contribution evaluation in Nautilus

이 예제는 Nautilus에서 비동기 기여도 평가를 사용하는 방법을 보여줍니다.
"""

import asyncio
import time
from unittest.mock import Mock

# 실제 사용 시에는 아래와 같이 import 합니다:
# from nautilus.api.contrib.pipline import (
#     connect_contrib_evaluation_async,
#     connect_contrib_evaluation_divided
# )

def create_example_data():
    """예제 데이터 생성"""
    # 초기 모델 (실제로는 PyTorch 모델)
    initial_model = Mock()
    
    # 클라이언트 결과 데이터
    results = []
    for i in range(5):  # 5개 클라이언트
        result = Mock()
        result.meta = {
            'client_name': f'client-{i+1}',
            'accuracy': 0.75 + i * 0.03,  # 점진적으로 향상되는 정확도
            'data_size': 1000 + i * 200,
            'NUM_STEPS_CURRENT_ROUND': 100
        }
        # 모델 파라미터 (실제로는 신경망 가중치)
        result.params = {
            f'layer_{j}': [0.1 + i * 0.01] * 50 for j in range(3)
        }
        results.append(result)
    
    # 테스트 데이터 로더
    testloader = Mock()
    
    return initial_model, results, testloader

async def example_single_async_evaluation():
    """단일 비동기 평가 예제"""
    print("=== 단일 비동기 기여도 평가 예제 ===")
    
    initial_model, results, testloader = create_example_data()
    
    # 비동기 기여도 평가 실행
    start_time = time.time()
    
    # 실제 코드 (import가 성공했을 때):
    # result = await connect_contrib_evaluation_async(
    #     num_clients=5,
    #     evaluation_mode='individual',
    #     initial_model=initial_model,
    #     results=results,
    #     DEVICE='cpu',
    #     testloader=testloader,
    #     mode='s_norm',
    #     max_workers=3
    # )
    
    # 시뮬레이션된 결과
    await asyncio.sleep(0.1)  # 실제 계산 시뮬레이션
    result = {f'client-{i+1}': 0.8 + i * 0.05 for i in range(5)}
    
    end_time = time.time()
    
    print(f"평가 완료 시간: {end_time - start_time:.2f}초")
    print(f"기여도 결과: {result}")
    
    return result

async def example_parallel_multiple_evaluations():
    """병렬 다중 평가 예제"""
    print("\n=== 병렬 다중 기여도 평가 예제 ===")
    
    initial_model, results, testloader = create_example_data()
    
    # 여러 평가 모드를 병렬로 실행
    evaluation_modes = ['individual', 'loo', 'shap', 'robust_volume']
    
    start_time = time.time()
    
    # 실제 코드 (import가 성공했을 때):
    # results_dict = await nt_contrib_evaluation_parallel(
    #     num_clients=5,
    #     evaluation_modes=evaluation_modes,
    #     initial_model=initial_model,
    #     results=results,
    #     DEVICE='cpu',
    #     testloader=testloader,
    #     max_workers=4
    # )
    
    # 병렬 실행 시뮬레이션
    async def simulate_evaluation(mode):
        await asyncio.sleep(0.1 + hash(mode) % 5 * 0.02)  # 다양한 실행 시간
        return {f'client-{i+1}': 0.7 + i * 0.04 + hash(mode) % 3 * 0.01 for i in range(5)}
    
    tasks = [simulate_evaluation(mode) for mode in evaluation_modes]
    results_list = await asyncio.gather(*tasks)
    results_dict = dict(zip(evaluation_modes, results_list))
    
    end_time = time.time()
    
    print(f"병렬 평가 완료 시간: {end_time - start_time:.2f}초")
    print("평가 모드별 결과:")
    for mode, result in results_dict.items():
        print(f"  {mode}: {result}")
    
    return results_dict

def example_divided_evaluation():
    """분할 평가 예제 (동기 래퍼)"""
    print("\n=== 분할 기여도 평가 예제 (동기 인터페이스) ===")
    
    initial_model, results, testloader = create_example_data()
    
    evaluation_modes = ['individual', 'loo', 'shap']
    
    start_time = time.time()
    
    # 실제 코드 (import가 성공했을 때):
    # results_dict = connect_contrib_evaluation_divided(
    #     num_clients=5,
    #     evaluation_modes=evaluation_modes,
    #     initial_model=initial_model,
    #     results=results,
    #     DEVICE='cpu',
    #     testloader=testloader,
    #     max_workers=3
    # )
    
    # 시뮬레이션된 결과
    time.sleep(0.3)  # 실제 계산 시뮬레이션
    results_dict = {
        mode: {f'client-{i+1}': 0.75 + i * 0.05 for i in range(5)}
        for mode in evaluation_modes
    }
    
    end_time = time.time()
    
    print(f"분할 평가 완료 시간: {end_time - start_time:.2f}초")
    print("평가 모드별 결과:")
    for mode, result in results_dict.items():
        print(f"  {mode}: {result}")
    
    return results_dict

async def example_performance_comparison():
    """성능 비교 예제"""
    print("\n=== 성능 비교: 순차 vs 병렬 ===")
    
    initial_model, results, testloader = create_example_data()
    evaluation_modes = ['individual', 'loo', 'shap', 'robust_volume']
    
    # 순차 실행 시뮬레이션
    print("순차 실행:")
    start_time = time.time()
    sequential_results = {}
    for mode in evaluation_modes:
        await asyncio.sleep(0.15)  # 각 평가당 시간
        sequential_results[mode] = {f'client-{i+1}': 0.8 for i in range(5)}
    sequential_time = time.time() - start_time
    print(f"  순차 실행 시간: {sequential_time:.2f}초")
    
    # 병렬 실행 시뮬레이션
    print("병렬 실행:")
    start_time = time.time()
    
    async def eval_task(mode):
        await asyncio.sleep(0.15)
        return {f'client-{i+1}': 0.8 for i in range(5)}
    
    tasks = [eval_task(mode) for mode in evaluation_modes]
    parallel_results_list = await asyncio.gather(*tasks)
    parallel_results = dict(zip(evaluation_modes, parallel_results_list))
    parallel_time = time.time() - start_time
    print(f"  병렬 실행 시간: {parallel_time:.2f}초")
    
    speedup = sequential_time / parallel_time
    print(f"  속도 향상: {speedup:.1f}x")
    
    return speedup

async def main():
    """메인 함수"""
    print("비동기 기여도 평가 사용 예제\n")
    
    examples = [
        ("단일 비동기 평가", example_single_async_evaluation),
        ("병렬 다중 평가", example_parallel_multiple_evaluations),
        ("분할 평가 (동기)", example_divided_evaluation),
        ("성능 비교", example_performance_comparison),
    ]
    
    for name, example_func in examples:
        print(f"\n{'='*60}")
        print(f"실행 중: {name}")
        print('='*60)
        
        try:
            if asyncio.iscoroutinefunction(example_func):
                await example_func()
            else:
                example_func()
            print(f"✓ {name} 완료")
        except Exception as e:
            print(f"✗ {name} 실패: {e}")
    
    print(f"\n{'='*60}")
    print("모든 예제 완료!")
    print("="*60)
    
    print("\n사용법 요약:")
    print("1. 단일 비동기 평가: connect_contrib_evaluation_async() 사용")
    print("2. 병렬 다중 평가: nt_contrib_evaluation_parallel() 사용")
    print("3. 기존 동기 코드와 호환: connect_contrib_evaluation_divided() 사용")
    print("4. max_workers 매개변수로 병렬 처리 수준 조정 가능")

if __name__ == "__main__":
    asyncio.run(main())