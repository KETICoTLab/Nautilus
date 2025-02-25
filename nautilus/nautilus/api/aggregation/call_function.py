# FL method call function
# call_function.py
# 이 파일은 FL_Methods 하위의 모든 연합학습(Federated Learning) 알고리즘을 동적으로 호출하여 실행하는 역할을 합니다.

import importlib
from typing import Any

def get_fl_method(method_name: str) -> Any:
    """
    주어진 연합학습 방법(FedAVG, FedOPT 등)을 동적으로 로드하여 반환하는 함수.
    """
    module_path = f"nautilus.api.aggregation.FL_Methods.{method_name}"
    try:
        module = importlib.import_module(module_path)
        return module
    except ModuleNotFoundError:
        raise ValueError(f"연합학습 방법 {method_name}을 찾을 수 없습니다.")

def execute_fl_method(method_name: str, *args, **kwargs) -> Any:
    """
    특정 연합학습 방법을 실행하는 함수.
    """
    fl_method = get_fl_method(method_name)
    if hasattr(fl_method, 'run'):
        return fl_method.run(*args, **kwargs)
    elif hasattr(fl_method, 'create_instance'):
        return fl_method.create_instance(*args, **kwargs)
    else:
        raise ValueError(f"{method_name} 모듈에 실행 가능한 함수가 정의되어 있지 않습니다.")
