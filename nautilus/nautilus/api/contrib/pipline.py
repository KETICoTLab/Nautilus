# contribution evaluation pipline
import logging
from .call_function import nt_contrib_evaluation

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
