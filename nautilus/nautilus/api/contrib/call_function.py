# contribution call function
import asyncio
import concurrent.futures
from functools import partial
from .client_contribution.individual import nt_contrib_individual
from .client_contribution.loo import nt_contrib_loo
from .client_contribution.shap import nt_contrib_shap
from .client_contribution.LeastCore import nt_contrib_leastcore
from .client_contribution.RobustVolume import nt_contrib_robust_volume

def nt_contrib_evaluation(num_clients, evaluation_mode, initial_model, results, DEVICE, testloader, mode=None, weight_list=None):
    #client contrib evaluation
    #print('here param', evaluation_mode, initial_model, results, DEVICE, testloader, mode, weight_list)
    contrib_mode_list = ['individual','loo','overall_shap','shap','optimized_shap','leastcore','robust_volume','custom']
 
    if num_clients == 1:
        return {'site-1': 1.0}

    if evaluation_mode == None:
        print('[ Nautilus INFO ] contribution evaluation is not defined')
        return
    
    if evaluation_mode not in contrib_mode_list:
        print('[ Nautilus ERROR ] contribution evaluation mode cannot be identified ')
        return
    
    if evaluation_mode == 'individual':
        # individual contribution evaluation
        client_contrib_res = nt_contrib_individual(initial_model, results, DEVICE, testloader ,mode='s_norm')
        return client_contrib_res
    elif evaluation_mode == 'loo':
        # loo contribution evaluation
        client_contrib_res = nt_contrib_loo(initial_model, results, DEVICE, testloader, mode='basic', weight_list=None)
        return client_contrib_res
    elif evaluation_mode == 'overall_shap':
        # over all shap contribution evaluation
        return
    elif evaluation_mode == 'shap':
        # shap contribution evaluation
        client_contrib_res = nt_contrib_shap(initial_model, results, DEVICE, testloader, mode ='basic')
        return client_contrib_res
    elif evaluation_mode == 'optimized_shap':
        # optimized shap  contribution evaluation
        return
    elif evaluation_mode == 'custom':
        # custom  contribution evaluation
        return
    elif evaluation_mode == 'leastcore':
        # leastcore contribution evaluation
        client_contrib_res = nt_contrib_leastcore(initial_model, results, DEVICE, testloader,mode='basic')
        return client_contrib_res
    elif evaluation_mode == 'robust_volume':
        # robust volume contribution evaluation
        client_contrib_res = nt_contrib_robust_volume(results)
        return client_contrib_res
    else:
        print('[ Nautilus Error ] Mode is not defined')
        return

async def nt_contrib_evaluation_async(num_clients, evaluation_mode, initial_model, results, DEVICE, testloader, mode=None, weight_list=None, max_workers=None):
    """
    비동기 클라이언트 기여도 평가 함수
    
    Args:
        num_clients (int): 클라이언트 수
        evaluation_mode (str): 평가 모드
        initial_model: 초기 모델
        results: 결과 데이터
        DEVICE (str): 연산 장치
        testloader: 테스트 데이터 로더
        mode (str, optional): 세부 모드
        weight_list (list, optional): 가중치 리스트
        max_workers (int, optional): 최대 워커 수
        
    Returns:
        dict: 기여도 평가 결과
    """
    contrib_mode_list = ['individual','loo','overall_shap','shap','optimized_shap','leastcore','robust_volume','custom']
 
    if num_clients == 1:
        return {'site-1': 1.0}

    if evaluation_mode == None:
        print('[ Nautilus INFO ] contribution evaluation is not defined')
        return
    
    if evaluation_mode not in contrib_mode_list:
        print('[ Nautilus ERROR ] contribution evaluation mode cannot be identified ')
        return
    
    # Set default max_workers if not provided
    if max_workers is None:
        max_workers = min(4, num_clients)  # Reasonable default
    
    # Use ThreadPoolExecutor for CPU-bound tasks
    loop = asyncio.get_event_loop()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        if evaluation_mode == 'individual':
            # individual contribution evaluation
            func = partial(nt_contrib_individual, initial_model, results, DEVICE, testloader, mode='s_norm')
            client_contrib_res = await loop.run_in_executor(executor, func)
            return client_contrib_res
        elif evaluation_mode == 'loo':
            # loo contribution evaluation
            func = partial(nt_contrib_loo, initial_model, results, DEVICE, testloader, mode='basic', weight_list=None)
            client_contrib_res = await loop.run_in_executor(executor, func)
            return client_contrib_res
        elif evaluation_mode == 'overall_shap':
            # over all shap contribution evaluation
            return
        elif evaluation_mode == 'shap':
            # shap contribution evaluation
            func = partial(nt_contrib_shap, initial_model, results, DEVICE, testloader, mode ='basic')
            client_contrib_res = await loop.run_in_executor(executor, func)
            return client_contrib_res
        elif evaluation_mode == 'optimized_shap':
            # optimized shap  contribution evaluation
            return
        elif evaluation_mode == 'custom':
            # custom  contribution evaluation
            return
        elif evaluation_mode == 'leastcore':
            # leastcore contribution evaluation
            func = partial(nt_contrib_leastcore, initial_model, results, DEVICE, testloader, mode='basic')
            client_contrib_res = await loop.run_in_executor(executor, func)
            return client_contrib_res
        elif evaluation_mode == 'robust_volume':
            # robust volume contribution evaluation
            func = partial(nt_contrib_robust_volume, results)
            client_contrib_res = await loop.run_in_executor(executor, func)
            return client_contrib_res
        else:
            print('[ Nautilus Error ] Mode is not defined')
            return

async def nt_contrib_evaluation_parallel(num_clients, evaluation_modes, initial_model, results, DEVICE, testloader, mode=None, weight_list=None, max_workers=None):
    """
    여러 평가 모드를 병렬로 실행하는 비동기 함수
    
    Args:
        num_clients (int): 클라이언트 수
        evaluation_modes (list): 평가 모드 리스트
        initial_model: 초기 모델
        results: 결과 데이터
        DEVICE (str): 연산 장치
        testloader: 테스트 데이터 로더
        mode (str, optional): 세부 모드
        weight_list (list, optional): 가중치 리스트
        max_workers (int, optional): 최대 워커 수
        
    Returns:
        dict: 평가 모드별 결과를 담은 딕셔너리
    """
    if not evaluation_modes:
        return {}
    
    # Create tasks for each evaluation mode
    tasks = []
    for eval_mode in evaluation_modes:
        task = nt_contrib_evaluation_async(
            num_clients, eval_mode, initial_model, results,
            DEVICE, testloader, mode=mode, weight_list=weight_list, max_workers=max_workers
        )
        tasks.append((eval_mode, task))
    
    # Execute all tasks concurrently
    results_dict = {}
    completed_tasks = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
    
    for i, (eval_mode, _) in enumerate(tasks):
        result = completed_tasks[i]
        if isinstance(result, Exception):
            print(f"[ Nautilus ERROR ] Error in evaluation mode '{eval_mode}': {result}")
            results_dict[eval_mode] = None
        else:
            results_dict[eval_mode] = result
    
    return results_dict
