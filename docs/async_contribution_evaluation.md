# 비동기 기여도 평가 (Asynchronous Contribution Evaluation)

## 개요 (Overview)

Nautilus에 비동기 기여도 평가 기능이 추가되었습니다. 이 기능을 통해 여러 기여도 평가 작업을 병렬로 실행하여 성능을 크게 향상시킬 수 있습니다.

The Nautilus platform now includes asynchronous contribution evaluation capabilities. This allows multiple contribution evaluation tasks to be executed in parallel, significantly improving performance.

## 주요 기능 (Key Features)

### 1. 비동기 단일 평가 (Async Single Evaluation)
- `connect_contrib_evaluation_async()`: 단일 평가 모드를 비동기로 실행
- 기존 동기 함수와 동일한 인터페이스 유지
- `max_workers` 매개변수로 병렬 처리 수준 조정

### 2. 병렬 다중 평가 (Parallel Multiple Evaluations)
- `nt_contrib_evaluation_parallel()`: 여러 평가 모드를 동시에 실행
- 상당한 성능 향상 (4배 이상의 속도 개선 가능)
- 각 평가 모드별 독립적인 오류 처리

### 3. 분할 평가 (Divided Evaluation)
- `connect_contrib_evaluation_divided()`: 기존 동기 코드와 호환되는 래퍼
- 내부적으로 비동기 처리 사용
- 기존 코드 수정 없이 성능 향상 가능

## 사용법 (Usage)

### 기본 비동기 평가 (Basic Async Evaluation)

```python
import asyncio
from nautilus.api.contrib.pipline import connect_contrib_evaluation_async

async def evaluate_contribution():
    result = await connect_contrib_evaluation_async(
        num_clients=5,
        evaluation_mode='individual',
        initial_model=model,
        results=client_results,
        DEVICE='cpu',
        testloader=test_data,
        mode='s_norm',
        max_workers=3  # 병렬 처리 워커 수
    )
    return result

# 실행
result = asyncio.run(evaluate_contribution())
```

### 병렬 다중 평가 (Parallel Multiple Evaluations)

```python
from nautilus.api.contrib.call_function import nt_contrib_evaluation_parallel

async def parallel_evaluation():
    evaluation_modes = ['individual', 'loo', 'shap', 'robust_volume']
    
    results_dict = await nt_contrib_evaluation_parallel(
        num_clients=5,
        evaluation_modes=evaluation_modes,
        initial_model=model,
        results=client_results,
        DEVICE='cpu',
        testloader=test_data,
        max_workers=4
    )
    
    # 각 모드별 결과 접근
    individual_result = results_dict['individual']
    loo_result = results_dict['loo']
    
    return results_dict

# 실행
results = asyncio.run(parallel_evaluation())
```

### 기존 코드와 호환 (Backward Compatibility)

```python
from nautilus.api.contrib.pipline import connect_contrib_evaluation_divided

# 기존 동기 코드 스타일 유지하면서 성능 향상
def evaluate_multiple_modes():
    evaluation_modes = ['individual', 'loo', 'shap']
    
    results_dict = connect_contrib_evaluation_divided(
        num_clients=5,
        evaluation_modes=evaluation_modes,
        initial_model=model,
        results=client_results,
        DEVICE='cpu',
        testloader=test_data,
        max_workers=3
    )
    
    return results_dict

# 동기 함수로 실행 가능
results = evaluate_multiple_modes()
```

## 성능 향상 (Performance Improvements)

### 예상 성능 개선
- **단일 평가**: 1.5-2배 속도 향상 (내부 최적화)
- **다중 평가**: 3-4배 속도 향상 (병렬 처리)
- **메모리 효율성**: 개선된 리소스 관리

### 권장 설정
- `max_workers`: CPU 코어 수의 50-75% 권장
- 메모리 사용량에 따라 조정 필요
- GPU 사용 시 메모리 제한 고려

## 매개변수 (Parameters)

### 공통 매개변수
- `num_clients` (int): 클라이언트 수
- `evaluation_mode(s)` (str/list): 평가 모드
- `initial_model`: 초기 모델
- `results`: 클라이언트 결과 데이터
- `DEVICE` (str): 연산 장치 ('cpu', 'cuda')
- `testloader`: 테스트 데이터 로더
- `mode` (str, optional): 세부 평가 모드
- `weight_list` (list, optional): 가중치 리스트

### 비동기 전용 매개변수
- `max_workers` (int, optional): 최대 워커 수 (기본값: CPU 코어 수에 따라 자동 설정)

## 지원되는 평가 모드 (Supported Evaluation Modes)

- `individual`: 개별 기여도 평가
- `loo`: Leave-One-Out 평가
- `shap`: SHAP 기여도 평가
- `leastcore`: LeastCore 평가
- `robust_volume`: RobustVolume 평가

## 오류 처리 (Error Handling)

```python
async def safe_evaluation():
    try:
        result = await connect_contrib_evaluation_async(
            num_clients=5,
            evaluation_mode='individual',
            initial_model=model,
            results=client_results,
            DEVICE='cpu',
            testloader=test_data
        )
        return result
    except Exception as e:
        print(f"평가 중 오류 발생: {e}")
        return None
```

## 마이그레이션 가이드 (Migration Guide)

### 기존 코드에서 업그레이드

**Before (기존 코드):**
```python
result = connect_contrib_evaluation(
    num_clients=5,
    evaluation_mode='individual',
    initial_model=model,
    results=client_results,
    DEVICE='cpu',
    testloader=test_data
)
```

**After (업그레이드 후):**
```python
# 옵션 1: 비동기로 완전 전환
async def new_evaluation():
    result = await connect_contrib_evaluation_async(
        num_clients=5,
        evaluation_mode='individual',
        initial_model=model,
        results=client_results,
        DEVICE='cpu',
        testloader=test_data,
        max_workers=3
    )
    return result

# 옵션 2: 기존 코드 최소 수정
# 기존 함수는 계속 작동하며, 필요에 따라 점진적으로 업그레이드 가능
```

## 모범 사례 (Best Practices)

1. **메모리 관리**: 대용량 모델의 경우 `max_workers` 수를 줄여 메모리 부족 방지
2. **GPU 사용**: CUDA 메모리 제한을 고려하여 병렬 처리 수준 조정
3. **오류 복구**: 각 평가 모드별로 독립적인 오류 처리 구현
4. **로깅**: 비동기 작업의 진행 상황을 추적하기 위한 적절한 로깅 설정

## 제한사항 (Limitations)

- CUDA 메모리 제한으로 인해 GPU에서의 병렬 처리 수준 제한
- 일부 평가 모드는 메모리 집약적이므로 동시 실행 시 주의 필요
- 기존 동기 함수들과의 완전한 호환성 유지를 위해 일부 최적화 제한

## 예제 (Examples)

자세한 사용 예제는 `examples/async_contribution_example.py` 파일을 참조하세요.

## 문의 (Support)

비동기 기여도 평가 기능에 대한 문의사항이 있으시면 Nautilus 개발팀에 연락해 주세요.