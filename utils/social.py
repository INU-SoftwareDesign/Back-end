import requests
from django.conf import settings

def get_user_info(provider, access_token):
    if provider == "kakao":
        url = "https://kapi.kakao.com/v2/user/me"
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(url, headers=headers)

    elif provider == "google":
        url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(url, headers=headers)

    elif provider == "naver":
        url = "https://openapi.naver.com/v1/nid/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Naver-Client-Id": settings.NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": settings.NAVER_CLIENT_SECRET,
        }
        res = requests.get(url, headers=headers)

    else:
        raise ValueError("지원하지 않는 provider입니다.")

    if not res.ok:
        raise Exception(f"{provider} 사용자 정보 요청 실패: {res.status_code} {res.text}")

    data = res.json()
    
    if provider == "kakao":
        return {
            "id": str(data["id"]),
            "email": data.get("kakao_account", {}).get("email", ""),
            "name": data.get("properties", {}).get("nickname", "Kakao 사용자")
        }

    elif provider == "google":
        return {
            "id": str(data["id"]),
            "email": data.get("email", ""),
            "name": data.get("name", "Google 사용자")
        }

    elif provider == "naver":
        response_data = data.get("response", {})
        return {
            "id": str(response_data.get("id", "")),
            "email": response_data.get("email", ""),
            "name": response_data.get("name", "Naver 사용자")
        }
