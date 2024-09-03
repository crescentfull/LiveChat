from django.shortcuts import render

def index(request):
    """
    채팅 페이지를 렌더링하는 뷰 함수입니다.
    """
    return render(request, 'myapp/index.html')
