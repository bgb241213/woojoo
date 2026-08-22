"""사진 입력칸.

장고 기본 위젯은 "현재: options/design/1/0.webp" 처럼 저장소 경로를 그대로
보여준다. 직원에게는 읽을 이유가 없는 글자이고, 그 옆에 미리보기가 따로 있으면
같은 사진을 두 번 말하는 셈이 된다. 여기서는 경로 대신 "등록됨" 한 마디만
남기고 파일 고르는 버튼을 앞세운다.
"""
from django.forms import ClearableFileInput


class PhotoInput(ClearableFileInput):
    template_name = 'admin/widgets/photo_input.html'
