import requests
import json

def http_post(url, payload):
    """
    데이터를 지정된 URL로 POST 요청을 보냄.

    :param url: 데이터를 보낼 엔드포인트
    :param payload: 전송할 데이터 (dict)
    :return: 서버 응답 (Response 객체)
    """
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  # 오류 발생 시 예외 처리
        return response.json()  # JSON 응답 반환
    except requests.exceptions.RequestException as e:
        print(f"> POST 요청 실패: {e}")
        return None

