#!/usr/bin/env python3
"""
TTKi System Status Report
========================

Quick system status check and summary report.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n🔹 {title}")
    print("-" * 40)

def check_file_exists(filepath, description):
    if os.path.exists(filepath):
        print(f"✅ {description}: EXISTS")
        return True
    else:
        print(f"❌ {description}: MISSING")
        return False

def check_validation_results():
    """Check validation test results"""
    print_section("Validation Test Results")
    
    if os.path.exists("validation_report_sqlite.json"):
        with open("validation_report_sqlite.json", 'r') as f:
            report = json.load(f)
        
        print(f"✅ Test Report: AVAILABLE")
        print(f"   Total Tests: {report['total_tests']}")
        print(f"   Passed: {report['passed']}")
        print(f"   Failed: {report['failed']}")
        print(f"   Success Rate: {report['success_rate']:.1f}%")
        print(f"   Overall Status: {report['overall_status']}")
        print(f"   Backend: {report['database_backend']}")
        print(f"   Duration: {report['duration']:.2f}s")
        
        print(f"\n   Test Details:")
        for test in report['test_results']:
            status_icon = "✅" if test['status'] == 'PASSED' else "❌"
            print(f"   {status_icon} {test['name']}")
        
        return report['overall_status'] == 'PASSED'
    else:
        print("❌ Test Report: NOT FOUND")
        return False

def main():
    print_header("TTKi Advanced AI System - Status Report")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check core system files
    print_section("Core System Components")
    
    core_files = [
        ("src/application/services/ttki_application_service.py", "TTKi Application Service"),
        ("src/application/services/system_dashboard_service.py", "System Dashboard Service"),
        ("src/infrastructure/database_manager.py", "Database Manager"),
        ("src/infrastructure/repositories/", "Repository Layer"),
        ("src/domain/entities/", "Domain Entities"),
        ("main.py", "Main Application"),
        ("start_system.sh", "Startup Script"),
        ("stop_system.sh", "Shutdown Script"),
    ]
    
    core_exists = 0
    for filepath, description in core_files:
        if check_file_exists(filepath, description):
            core_exists += 1
    
    # Check validation and testing
    print_section("Testing & Validation")
    
    test_files = [
        ("validate_system_sqlite.py", "SQLite Validation Script"),
        ("validate_system.py", "PostgreSQL Validation Script"),
        ("test_complete.py", "Complete Test Suite"),
        ("TESTING_README.md", "Testing Documentation"),
    ]
    
    test_exists = 0
    for filepath, description in test_files:
        if check_file_exists(filepath, description):
            test_exists += 1
    
    # Check validation results
    validation_passed = check_validation_results()
    
    # Check documentation
    print_section("Documentation")
    
    doc_files = [
        ("README_ADVANCED.md", "Advanced README"),
        ("DEPLOYMENT_REPORT.md", "Deployment Report"),
        ("system_architecture_design.md", "Architecture Design"),
        ("bolt_system_analysis.md", "System Analysis"),
    ]
    
    doc_exists = 0
    for filepath, description in doc_files:
        if check_file_exists(filepath, description):
            doc_exists += 1
    
    # Check configuration files
    print_section("Configuration & Dependencies")
    
    config_files = [
        ("requirements.txt", "Python Requirements"),
        ("Dockerfile", "Docker Configuration"),
        ("app.log", "Application Log"),
    ]
    
    config_exists = 0
    for filepath, description in config_files:
        if check_file_exists(filepath, description):
            config_exists += 1
    
    # Overall system status
    print_header("Overall System Status")
    
    total_components = len(core_files) + len(test_files) + len(doc_files) + len(config_files)
    total_existing = core_exists + test_exists + doc_exists + config_exists
    completion_rate = (total_existing / total_components) * 100
    
    print(f"📊 Component Completion: {total_existing}/{total_components} ({completion_rate:.1f}%)")
    print(f"🧪 Validation Status: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
    print(f"🏗️  Core System: {core_exists}/{len(core_files)} components")
    print(f"🔬 Testing Suite: {test_exists}/{len(test_files)} components")
    print(f"📚 Documentation: {doc_exists}/{len(doc_files)} files")
    print(f"⚙️  Configuration: {config_exists}/{len(config_files)} files")
    
    # Final assessment
    print_section("Final Assessment")
    
    if completion_rate >= 90 and validation_passed:
        print("🎉 SYSTEM STATUS: ✅ PRODUCTION READY")
        print("   All major components are in place and validated.")
        print("   The TTKi Advanced AI System is ready for deployment.")
    elif completion_rate >= 75:
        print("⚠️  SYSTEM STATUS: 🟡 MOSTLY COMPLETE")
        print("   Most components are in place, minor items may be missing.")
        print("   System should be functional but review missing items.")
    else:
        print("❌ SYSTEM STATUS: 🔴 INCOMPLETE")
        print("   Critical components are missing.")
        print("   System requires additional development before deployment.")
    
    # Quick start instructions
    print_section("Quick Start Commands")
    print("🚀 Start System:")
    print("   ./start_system.sh")
    print("")
    print("🔍 Validate System:")
    print("   python validate_system_sqlite.py")
    print("")
    print("🛑 Stop System:")
    print("   ./stop_system.sh")
    print("")
    print("📊 System Dashboard:")
    print("   python -c \"from src.application.services.system_dashboard_service import SystemDashboardService; import asyncio; asyncio.run(SystemDashboardService().get_system_health())\"")
    
    print(f"\n{'='*60}")
    print("TTKi System Status Report Complete")
    print(f"{'='*60}\n")
    
    return 0 if (completion_rate >= 90 and validation_passed) else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
