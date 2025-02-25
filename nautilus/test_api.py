from flask import Flask, request, jsonify
from threading import Thread
import time
import uuid

app = Flask(__name__)

# 작업 상태를 저장할 딕셔너리
tasks = {}

# 모델 훈련을 시뮬레이션하는 함수
def train_model(task_id, data):
    # 작업 상태를 업데이트
    tasks[task_id] = {"status": "running"}
    print(f"Training started for task {task_id}...")
    
    # 훈련 시뮬레이션 (3초 소요)
    time.sleep(3)
    
    # 훈련 완료 후 결과 저장
    tasks[task_id] = {
        "status": "completed",
        "result": {
            "accuracy": 0.95,
            "loss": 0.1,
            "model_url": f"/models/{task_id}/model.zip"
        }
    }
    print(f"Training completed for task {task_id}.")

@app.route('/train-model', methods=['POST'])
def start_training():
    """
    모델 훈련을 시작하는 엔드포인트.
    """
    # 요청 데이터 확인
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request, JSON data is required"}), 400

    # 고유 작업 ID 생성
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "submitted"}

    # 별도의 스레드에서 훈련 실행
    thread = Thread(target=train_model, args=(task_id, data))
    thread.start()

    return jsonify({"status": "submitted", "task_id": task_id}), 202

@app.route('/train-model/<task_id>/status', methods=['GET'])
def get_status(task_id):
    """
    특정 작업의 상태를 반환하는 엔드포인트.
    """
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({"status": task["status"]})

@app.route('/train-model/<task_id>/result', methods=['GET'])
def get_result(task_id):
    """
    훈련 결과를 반환하는 엔드포인트.
    """
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task["status"] != "completed":
        return jsonify({"error": "Task not completed yet"}), 400

    return jsonify({"status": "completed", "result": task["result"]})

# 모델 파일 다운로드 시뮬레이션
@app.route('/models/<task_id>/model.zip', methods=['GET'])
def download_model(task_id):
    """
    모델 파일 다운로드를 시뮬레이션하는 엔드포인트.
    """
    # 실제로는 모델 파일을 서빙해야 함
    return f"Model file for task {task_id} (this is a placeholder).", 200

if __name__ == '__main__':
    app.run(debug=True)
