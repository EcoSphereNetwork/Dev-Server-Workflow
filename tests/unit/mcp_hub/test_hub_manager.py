import pytest
from unittest.mock import MagicMock, patch
from src.mcp_hub.hub_manager import HubManager

class TestHubManager:
    @pytest.fixture
    def hub_manager(self):
        return HubManager()
    
    def test_hub_manager_initialization(self, hub_manager):
        assert hub_manager is not None
        assert hasattr(hub_manager, 'servers')
        assert isinstance(hub_manager.servers, dict)
    
    @patch('src.mcp_hub.hub_manager.HubManager.register_server')
    def test_register_server(self, mock_register, hub_manager):
        server = MagicMock()
        server.id = 'test-server'
        server.name = 'Test Server'
        server.type = 'test'
        
        hub_manager.register_server(server)
        
        mock_register.assert_called_once_with(server)
