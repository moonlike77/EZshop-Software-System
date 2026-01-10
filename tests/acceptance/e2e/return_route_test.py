import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from app.models.DTO.return_dto import ReturnDTO
from app.models.return_status import ReturnStatus
from app.models.user_type import UserType

client = TestClient(app)

# ماک کردن پروسه بررسی توکن برای دور زدن احراز هویت واقعی
@pytest.fixture
def mock_auth_process():
    # به جای patch کردن کل authenticate_user، لاجیک داخلی آن را ماک می‌کنیم
    # این تابع در auth_middleware ایمپورت شده، پس باید آنجا پچ شود
    with patch("app.middleware.auth_middleware.process_token") as mock_proc:
        # شبیه‌سازی یک کاربر لاگین شده (مثلاً ادمین)
        mock_user = MagicMock()
        mock_user.username = "admin"
        mock_user.type = UserType.Administrator
        mock_proc.return_value = mock_user
        yield mock_proc

@pytest.fixture
def mock_controller():
    # مسیر دقیق کنترلر در فایل route
    with patch("app.routes.return_route.controller") as mock:
        yield mock

def test_start_return_route(mock_controller, mock_auth_process):
    # تنظیم ماک کنترلر
    mock_response = ReturnDTO(id=1, sale_id=100, status=ReturnStatus.OPEN, lines=[])
    mock_controller.start_return = AsyncMock(return_value=mock_response)

    # فراخوانی API با هدر فیک
    # نکته کلیدی: ارسال هدر Authorization ضروری است تا میدل‌ور ارور 401 ندهد
    response = client.post(
        "/api/v1/returns/?sale_id=100", 
        headers={"Authorization": "Bearer mock_token_ignored"} 
    )

    # بررسی
    assert response.status_code == 201
    assert response.json()["id"] == 1
    mock_controller.start_return.assert_called_once_with(100)

def test_close_return_route(mock_controller, mock_auth_process):
    mock_controller.close_return = AsyncMock(return_value=True)
    
    response = client.patch(
        "/api/v1/returns/1/close",
        headers={"Authorization": "Bearer mock_token_ignored"}
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True