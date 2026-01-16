import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.controllers.return_controller import ReturnController
from app.models.return_status import ReturnStatus
from app.models.errors.app_error import AppError

@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def controller(mock_repo):
    ctrl = ReturnController()
    ctrl.repo = mock_repo
    return ctrl

@pytest.mark.asyncio
async def test_start_return(controller, mock_repo):
    # تنظیم رفتار ماک
    mock_return = MagicMock()
    mock_return.id = 1
    mock_return.status = ReturnStatus.OPEN
    mock_return.lines = []
    mock_repo.create_return.return_value = mock_return

    # اجرای متد
    result = await controller.start_return(sale_id=100)

    # بررسی نتیجه
    assert result.id == 1
    assert result.status == ReturnStatus.OPEN
    mock_repo.create_return.assert_called_once_with(100)

@pytest.mark.asyncio
async def test_close_return_success(controller, mock_repo):
    # مرجوعی باز است
    mock_return = MagicMock()
    mock_return.status = ReturnStatus.OPEN
    mock_return.lines = [MagicMock()] # یک آیتم دارد
    mock_repo.get_return.return_value = mock_return
    
    # اجرا
    result = await controller.close_return(return_id=1)
    
    # بررسی
    assert result is True
    mock_repo.update_status.assert_called_once_with(1, ReturnStatus.CLOSED, None)

@pytest.mark.asyncio
async def test_close_return_fail_if_not_open(controller, mock_repo):
    # مرجوعی قبلا بسته شده
    mock_return = MagicMock()
    mock_return.status = ReturnStatus.CLOSED
    mock_repo.get_return.return_value = mock_return
    
    # باید ارور بده
    with pytest.raises(AppError):
        await controller.close_return(return_id=1)