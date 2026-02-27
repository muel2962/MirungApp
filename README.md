# 미렁 (Mirung) - iPad Screen Mirroring App for Windows

미렁(Mirung)은 파이썬과 오픈소스 AirPlay 수신기(UxPlay)를 활용하여 아이패드 화면을 윈도우 PC로 미러링하고 제어할 수 있는 GUI 애플리케이션입니다. 

## 📌 주요 기능
* **화면 미러링**: 아이패드 화면과 소리를 윈도우 PC로 실시간 스트리밍 (60FPS 지원)
* **세련된 UI**: `customtkinter`를 활용한 모던하고 직관적인 다크 모드 인터페이스
* **화면 캡처**: 미러링 중인 창만 정확히 인식하여 스크린샷(.png) 저장
* **화면 녹화**: 미러링 중인 창의 화면을 동영상(.mp4)으로 녹화
* **경로 설정**: 스크린샷 및 동영상 저장 폴더 커스텀 지정 (설정 자동 저장)

## 🗂 폴더 구조
프로젝트가 정상적으로 작동하기 위해서는 아래와 같은 폴더 및 파일 구조를 유지해야 합니다.

```text
Mirung/
├── main.py
├── icon.ico
├── settings.json
└── uxplay_win/
    ├── uxplay.exe
    ├── dnssd.dll
    ├── libgstreamer-1.0-0.dll
    └── (기타 UxPlay 및 GStreamer 종속성 dll 파일들)
