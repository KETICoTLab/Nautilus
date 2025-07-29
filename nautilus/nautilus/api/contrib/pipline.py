# contribution evaluation pipline
import asyncio
import concurrent.futures
import logging
from .call_function import nt_contrib_evaluation, nt_contrib_evaluation_async

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_contrib_evaluation(num_clients, evaluation_mode, initial_model, results, DEVICE, testloader, mode=None, weight_list=None):
    """
    클라이언트 기여도 평가를 수행하는 함수

    Args:
        num_clients (int): The number of clients involved in the training
        evaluation_mode (str): 평가 모드. 'individual', 'loo', 'shap' 등.
        initial_model: 초기 모델 객체.
        results (dict): 클라이언트별 결과 데이터.
        DEVICE (str): 연산에 사용할 장치. 예: 'cpu' 또는 'cuda'.
        testloader: 테스트 데이터 로더.
        mode (str, optional): 평가 세부 모드. 기본값은 None.
        weight_list (list, optional): 가중치 리스트. 기본값은 None.

    Returns:
        dict: 평가 결과를 담은 딕셔너리. 예외 발생 시 None을 반환합니다.
    """
    try:
        logger.info(f"평가 모드 '{evaluation_mode}'로 기여도 평가를 시작합니다.")
        result = nt_contrib_evaluation(num_clients, evaluation_mode, initial_model, results, DEVICE, testloader, mode=mode, weight_list=weight_list)
        logger.info(f"평가 모드 '{evaluation_mode}'로 기여도 평가를 완료했습니다.")
        return result
    except Exception as e:
        logger.error(f"'{evaluation_mode}' 모드의 기여도 평가 중 오류 발생: {e}", exc_info=True)
        return None

async def connect_contrib_evaluation_async(num_clients, evaluation_mode, initial_model, results, DEVICE, testloader, mode=None, weight_list=None, max_workers=None):
    """
    비동기 클라이언트 기여도 평가를 수행하는 함수

    Args:
        num_clients (int): The number of clients involved in the training
        evaluation_mode (str): 평가 모드. 'individual', 'loo', 'shap' 등.
        initial_model: 초기 모델 객체.
        results (dict): 클라이언트별 결과 데이터.
        DEVICE (str): 연산에 사용할 장치. 예: 'cpu' 또는 'cuda'.
        testloader: 테스트 데이터 로더.
        mode (str, optional): 평가 세부 모드. 기본값은 None.
        weight_list (list, optional): 가중치 리스트. 기본값은 None.
        max_workers (int, optional): 최대 워커 수. 기본값은 None (CPU 코어 수에 따라 자동 설정).

    Returns:
        dict: 평가 결과를 담은 딕셔너리. 예외 발생 시 None을 반환합니다.
    """
    try:
        logger.info(f"비동기 평가 모드 '{evaluation_mode}'로 기여도 평가를 시작합니다.")
        result = await nt_contrib_evaluation_async(num_clients, evaluation_mode, initial_model, results, DEVICE, testloader, mode=mode, weight_list=weight_list, max_workers=max_workers)
        logger.info(f"비동기 평가 모드 '{evaluation_mode}'로 기여도 평가를 완료했습니다.")
        return result
    except Exception as e:
        logger.error(f"비동기 '{evaluation_mode}' 모드의 기여도 평가 중 오류 발생: {e}", exc_info=True)
        return None

def connect_contrib_evaluation_divided(num_clients, evaluation_modes, initial_model, results, DEVICE, testloader, mode=None, weight_list=None, max_workers=None):
    """
    여러 평가 모드를 분할하여 비동기적으로 기여도 평가를 수행하는 함수

    Args:
        num_clients (int): The number of clients involved in the training
        evaluation_modes (list): 평가 모드 리스트. ['individual', 'loo', 'shap'] 등.
        initial_model: 초기 모델 객체.
        results (dict): 클라이언트별 결과 데이터.
        DEVICE (str): 연산에 사용할 장치. 예: 'cpu' 또는 'cuda'.
        testloader: 테스트 데이터 로더.
        mode (str, optional): 평가 세부 모드. 기본값은 None.
        weight_list (list, optional): 가중치 리스트. 기본값은 None.
        max_workers (int, optional): 최대 워커 수. 기본값은 None.

    Returns:
        dict: 평가 모드별 결과를 담은 딕셔너리. 예외 발생 시 None을 반환합니다.
    """
    try:
        logger.info(f"분할된 기여도 평가를 시작합니다. 모드: {evaluation_modes}")
        
        # Run the async function in the current thread's event loop or create one
        async def run_evaluations():
            tasks = []
            for eval_mode in evaluation_modes:
                task = connect_contrib_evaluation_async(
                    num_clients, eval_mode, initial_model, results, 
                    DEVICE, testloader, mode=mode, weight_list=weight_list, max_workers=max_workers
                )
                tasks.append((eval_mode, task))
            
            results_dict = {}
            for eval_mode, task in tasks:
                try:
                    result = await task
                    results_dict[eval_mode] = result
                except Exception as e:
                    logger.error(f"평가 모드 '{eval_mode}' 실행 중 오류: {e}")
                    results_dict[eval_mode] = None
            
            return results_dict
        
        # Try to get the current event loop, if not available create new one
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, we need to run in thread pool
                import threading
                import queue
                
                result_queue = queue.Queue()
                exception_queue = queue.Queue()
                
                def run_in_thread():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result = new_loop.run_until_complete(run_evaluations())
                        result_queue.put(result)
                    except Exception as e:
                        exception_queue.put(e)
                    finally:
                        new_loop.close()
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                
                if not exception_queue.empty():
                    raise exception_queue.get()
                
                return result_queue.get()
            else:
                return loop.run_until_complete(run_evaluations())
        except RuntimeError:
            # No event loop in current thread, create new one
            return asyncio.run(run_evaluations())
            
    except Exception as e:
        logger.error(f"분할된 기여도 평가 중 오류 발생: {e}", exc_info=True)
        return None
