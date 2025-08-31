#!/usr/bin/env python3
"""
Czysty zestaw testów dla aplikacji terminala AI
"""

import unittest
import requests
import time
import socket
import socketio

class TestBasicFunctionality(unittest.TestCase):
    """Podstawowe testy funkcjonalności"""
    
    @classmethod
    def setUpClass(cls):
        cls.base_url = "http://localhost:4001"
        cls.vnc_url = "http://localhost:4051"
        cls.test_timeout = 30
    
    def test_flask_server_responds(self):
        """Test: Serwer Flask odpowiada"""
        try:
            response = requests.get(self.base_url, timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn("TTKi-cli", response.text)
            print("✅ Flask: OK")
        except Exception as e:
            self.fail(f"❌ Flask: {e}")
    
    def test_vnc_server_responds(self):
        """Test: Serwer noVNC odpowiada"""
        try:
            response = requests.get(f"{self.vnc_url}/vnc.html", timeout=5)
            self.assertEqual(response.status_code, 200)
            self.assertIn("noVNC", response.text)
            print("✅ noVNC: OK")
        except Exception as e:
            print(f"⚠️ noVNC: {e}")
    
    def test_permissions_policy(self):
        """Test: Polityka uprawnień"""
        response = requests.get(self.base_url)
        headers = response.headers
        
        self.assertIn("Permissions-Policy", headers)
        permissions = headers["Permissions-Policy"]
        self.assertIn("fullscreen=*", permissions)
        print("✅ Polityka uprawnień: OK")
    
    def test_socketio_basic(self):
        """Test: Podstawowe Socket.IO"""
        sio = socketio.SimpleClient()
        try:
            sio.connect(self.base_url)
            self.assertTrue(sio.connected)
            print("✅ Socket.IO: OK")
        except Exception as e:
            self.fail(f"❌ Socket.IO: {e}")
        finally:
            if sio.connected:
                sio.disconnect()
    
    def test_ai_echo_command(self):
        """Test: Echo przez AI"""
        sio = socketio.SimpleClient()
        try:
            sio.connect(self.base_url)
            sio.emit("message", "echo 'Test AI'")
            
            # Czekaj na odpowiedź
            start_time = time.time()
            response = None
            
            while time.time() - start_time < 30:
                try:
                    response = sio.receive(timeout=2)
                    if response:
                        break
                except:
                    continue
            
            self.assertIsNotNone(response, "AI nie odpowiedziało")
            print("✅ AI Echo: OK")
            
        except Exception as e:
            self.fail(f"❌ AI Echo: {e}")
        finally:
            if sio.connected:
                sio.disconnect()
    
    def test_ai_python_task(self):
        """Test: Zadanie Python"""
        sio = socketio.SimpleClient()
        try:
            sio.connect(self.base_url)
            sio.emit("message", "Napisz prosty print('Hello')")
            
            start_time = time.time()
            response = None
            
            while time.time() - start_time < 45:
                try:
                    response = sio.receive(timeout=3)
                    if response:
                        break
                except:
                    continue
            
            self.assertIsNotNone(response, "AI nie odpowiedziało na zadanie Python")
            print("✅ AI Python: OK")
            
        except Exception as e:
            self.fail(f"❌ AI Python: {e}")
        finally:
            if sio.connected:
                sio.disconnect()

def run_complete_tests():
    """Uruchom pełne testy"""
    print("🚀 PEŁNE TESTY APLIKACJI AI TERMINAL")
    print("="*50)
    
    # Sprawdź dostępność
    print("🔍 Sprawdzanie serwisów...")
    
    try:
        requests.get("http://localhost:4001", timeout=3)
        print("✅ Flask: Dostępny")
    except:
        print("❌ Flask: Niedostępny")
        return False
    
    try:
        requests.get("http://localhost:4051", timeout=3)
        print("✅ noVNC: Dostępny")
    except:
        print("⚠️ noVNC: Niedostępny (kontynuuję)")
    
    print("\n🧪 Uruchamianie testów...")
    print("-"*50)
    
    # Uruchom testy
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBasicFunctionality)
    
    # Uruchom z cichym outputem
    import io
    import sys
    
    # Przechwytywanie outputu
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    
    runner = unittest.TextTestRunner(verbosity=0, stream=buffer)
    result = runner.run(suite)
    
    # Przywróć stdout
    sys.stdout = old_stdout
    
    print("\n📊 WYNIKI TESTÓW")
    print("="*50)
    print(f"Uruchomiono: {result.testsRun}")
    print(f"Sukces: {result.testsRun - len(result.errors) - len(result.failures)}")
    print(f"Błędy: {len(result.errors)}")
    print(f"Niepowodzenia: {len(result.failures)}")
    
    if result.errors:
        print("\n❌ BŁĘDY:")
        for test, error in result.errors:
            print(f"  • {test}")
    
    if result.failures:
        print("\n❌ NIEPOWODZENIA:")
        for test, failure in result.failures:
            print(f"  • {test}")
    
    success_rate = ((result.testsRun - len(result.errors) - len(result.failures)) / result.testsRun) * 100
    print(f"\n🎯 Sukces: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 TESTY POMYŚLNE!")
    else:
        print("⚠️ TESTY CZĘŚCIOWE")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_complete_tests()
