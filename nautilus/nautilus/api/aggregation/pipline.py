# FL method call pipline
# pipline.py
# 이 파일은 연합학습(Federated Learning) 파이프라인을 실행하는 역할을 합니다.
# call_function.py를 활용하여 다양한 FL_Methods를 호출하고 실행할 수 있도록 구성되어 있습니다.

from nautilus.api.aggregation.call_function import execute_fl_method

def run_federated_learning(method_name: str, initial_model, num_clients: int, num_rounds: int):
    """
    특정 연합학습 방법을 실행하는 함수.
    """
    print(f"{method_name} 방식으로 연합학습을 시작합니다...")
    
    result = execute_fl_method(method_name, initial_model=initial_model, n_clients=num_clients, num_rounds=num_rounds)
    
    print(f"{method_name} 연합학습 완료.")
    return result

def run_fl_pipeline(method_name: str, config: dict):
    """
    설정 파일(config)을 기반으로 연합학습을 실행하는 함수.
    다양한 연합학습 방법을 실행할 수 있도록 구성됩니다.
    """
    print(f"설정 파일을 기반으로 {method_name} 방식으로 연합학습을 시작합니다...")
    
    result = execute_fl_method(method_name, **config)
    
    print(f"{method_name} 연합학습 완료.")
    return result