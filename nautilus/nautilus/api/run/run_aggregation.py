# run aggregation 
# 이 파일은 create_FedAVG 함수를 실행하는 예제 스크립트임.

import torch.nn as nn
from nautilus.api.aggregation.pipline import run_federated_learning

class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc = nn.Linear(10, 2)
    
    def forward(self, x):
        return self.fc(x)

if __name__ == "__main__":
    # 초기 모델 생성
    initial_model = SimpleModel()
    
    # 연합학습 실행
    method_name = "FedAVG"
    num_clients = 5
    num_rounds = 10
    
    result = run_federated_learning(method_name, initial_model, num_clients, num_rounds)
    print("연합학습 결과:", result)
