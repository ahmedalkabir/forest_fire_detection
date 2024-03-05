import requests


def send_sms_message(phone: str, message: str):
    response = requests.post('http://128.140.126.167:90/api/v1/smsx', 
                            json={'phone':phone, 'message':message})
    return True if response.status_code == 202 else False

