"""
End-to-end tests for user journeys.
"""

import unittest
import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class TestUserJourneys(unittest.TestCase):
    """End-to-end tests for user journeys."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Set up environment variables for testing
        cls.frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:8080')
        
        # Set up Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        try:
            # Initialize Chrome driver
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
        except WebDriverException:
            # Skip tests if Chrome driver is not available
            raise unittest.SkipTest("Chrome driver is not available")
    
    @classmethod
    def tearDownClass(cls):
        """Tear down test environment."""
        if hasattr(cls, 'driver'):
            cls.driver.quit()
    
    def setUp(self):
        """Set up test case."""
        # Navigate to the frontend
        self.driver.get(self.frontend_url)
        
        # Wait for the page to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
        except TimeoutException:
            self.skipTest("Frontend is not available")
    
    def test_dashboard_navigation(self):
        """Test that the user can navigate to the dashboard."""
        # Check if the dashboard is already loaded
        if 'dashboard' in self.driver.current_url.lower():
            # We're already on the dashboard
            pass
        else:
            # Navigate to the dashboard
            dashboard_link = self.driver.find_element(By.LINK_TEXT, 'Dashboard')
            dashboard_link.click()
            
            # Wait for the dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.url_contains('dashboard')
            )
        
        # Check that the dashboard title is present
        dashboard_title = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertEqual(dashboard_title.text, 'Dashboard')
        
        # Check that the dashboard contains widgets
        widgets = self.driver.find_elements(By.CSS_SELECTOR, '.widget')
        self.assertGreater(len(widgets), 0)
    
    def test_dashboard_tabs(self):
        """Test that the user can switch between dashboard tabs."""
        # Navigate to the dashboard if not already there
        if 'dashboard' not in self.driver.current_url.lower():
            dashboard_link = self.driver.find_element(By.LINK_TEXT, 'Dashboard')
            dashboard_link.click()
            
            # Wait for the dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.url_contains('dashboard')
            )
        
        # Find the tabs
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '[role="tab"]')
        
        # Check that there are at least 2 tabs (Overview and Widgets)
        self.assertGreaterEqual(len(tabs), 2)
        
        # Click on the Widgets tab
        widgets_tab = None
        for tab in tabs:
            if 'Widgets' in tab.text:
                widgets_tab = tab
                break
        
        if widgets_tab:
            widgets_tab.click()
            
            # Wait for the widgets to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.widget'))
            )
            
            # Check that the widgets are displayed
            widgets = self.driver.find_elements(By.CSS_SELECTOR, '.widget')
            self.assertGreater(len(widgets), 0)
            
            # Click on the Overview tab
            overview_tab = None
            for tab in tabs:
                if 'Overview' in tab.text:
                    overview_tab = tab
                    break
            
            if overview_tab:
                overview_tab.click()
                
                # Wait for the overview to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.overview-container'))
                )
                
                # Check that the overview is displayed
                overview = self.driver.find_element(By.CSS_SELECTOR, '.overview-container')
                self.assertTrue(overview.is_displayed())
    
    def test_add_widget(self):
        """Test that the user can add a widget to the dashboard."""
        # Navigate to the dashboard if not already there
        if 'dashboard' not in self.driver.current_url.lower():
            dashboard_link = self.driver.find_element(By.LINK_TEXT, 'Dashboard')
            dashboard_link.click()
            
            # Wait for the dashboard to load
            WebDriverWait(self.driver, 10).until(
                EC.url_contains('dashboard')
            )
        
        # Find the tabs
        tabs = self.driver.find_elements(By.CSS_SELECTOR, '[role="tab"]')
        
        # Click on the Widgets tab
        widgets_tab = None
        for tab in tabs:
            if 'Widgets' in tab.text:
                widgets_tab = tab
                break
        
        if widgets_tab:
            widgets_tab.click()
            
            # Wait for the widgets to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.widget'))
            )
            
            # Count the number of widgets
            initial_widget_count = len(self.driver.find_elements(By.CSS_SELECTOR, '.widget'))
            
            # Click the "Add Widget" button
            add_widget_button = self.driver.find_element(By.XPATH, '//button[contains(text(), "Widget hinzufügen")]')
            add_widget_button.click()
            
            # Wait for the modal to appear
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.modal'))
            )
            
            # Select a widget type
            widget_type_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.modal button')
            if widget_type_buttons:
                widget_type_buttons[0].click()
                
                # Click the "Add" button
                add_button = self.driver.find_element(By.XPATH, '//button[contains(text(), "Hinzufügen")]')
                add_button.click()
                
                # Wait for the modal to close
                WebDriverWait(self.driver, 10).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, '.modal'))
                )
                
                # Check that a new widget was added
                new_widget_count = len(self.driver.find_elements(By.CSS_SELECTOR, '.widget'))
                self.assertEqual(new_widget_count, initial_widget_count + 1)
    
    def test_mcp_server_status(self):
        """Test that the user can view MCP server status."""
        # Navigate to the MCP servers page
        self.driver.get(self.frontend_url + '/mcp-servers')
        
        # Wait for the page to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'h1'))
            )
        except TimeoutException:
            self.skipTest("MCP servers page is not available")
        
        # Check that the page title is correct
        page_title = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertIn('MCP', page_title.text)
        
        # Check that the server list is displayed
        server_list = self.driver.find_elements(By.CSS_SELECTOR, '.server-item')
        self.assertGreater(len(server_list), 0)
        
        # Check that each server has a status indicator
        for server in server_list:
            status = server.find_element(By.CSS_SELECTOR, '.status-indicator')
            self.assertTrue(status.is_displayed())
    
    def test_workflow_list(self):
        """Test that the user can view the workflow list."""
        # Navigate to the workflows page
        self.driver.get(self.frontend_url + '/workflows')
        
        # Wait for the page to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'h1'))
            )
        except TimeoutException:
            self.skipTest("Workflows page is not available")
        
        # Check that the page title is correct
        page_title = self.driver.find_element(By.TAG_NAME, 'h1')
        self.assertIn('Workflow', page_title.text)
        
        # Check that the workflow list is displayed
        workflow_list = self.driver.find_elements(By.CSS_SELECTOR, '.workflow-item')
        
        # There might not be any workflows, so we don't assert on the length
        if workflow_list:
            # Check that each workflow has a name and status
            for workflow in workflow_list:
                name = workflow.find_element(By.CSS_SELECTOR, '.workflow-name')
                status = workflow.find_element(By.CSS_SELECTOR, '.workflow-status')
                self.assertTrue(name.is_displayed())
                self.assertTrue(status.is_displayed())

if __name__ == '__main__':
    unittest.main()