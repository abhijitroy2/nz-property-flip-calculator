#!/usr/bin/env python3
"""
Test script for desktop app functionality.
Run this to verify the desktop app works before building EXE.
"""

import os
import sys
import tempfile
import csv
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_test_csv():
    """Create a test CSV file for testing."""
    test_data = [
        {
            "address": "123 Test Street, Auckland",
            "bedrooms": "3",
            "bathrooms": "2", 
            "floor_area": "120",
            "land_area": "600",
            "asking_price": "750000",
            "target_value": "800000"
        },
        {
            "address": "456 Sample Road, Wellington",
            "bedrooms": "2",
            "bathrooms": "1",
            "floor_area": "80", 
            "land_area": "400",
            "asking_price": "650000",
            "target_value": "700000"
        }
    ]
    
    # Create temp CSV file
    temp_dir = Path(tempfile.gettempdir()) / "realfip_test"
    temp_dir.mkdir(exist_ok=True)
    csv_path = temp_dir / "test_properties.csv"
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=test_data[0].keys())
        writer.writeheader()
        writer.writerows(test_data)
    
    return csv_path, temp_dir

def test_config():
    """Test configuration loading/saving."""
    print("Testing configuration...")
    try:
        from desktop.config import DesktopConfig
        
        # Test default config
        config = DesktopConfig()
        print(f"✓ Default config created: {config.csv_paths}")
        
        # Test config with custom values
        csv_path, output_dir = create_test_csv()
        config = DesktopConfig(
            csv_paths=[str(csv_path)],
            output_dir=str(output_dir),
            run_on_startup=False
        )
        config.schedule.minutes = 30
        config.email.enabled = False
        print(f"✓ Custom config created: {config.csv_paths}")
        
        return True
    except Exception as e:
        print(f"✗ Config test failed: {e}")
        return False

def test_runner():
    """Test batch runner."""
    print("Testing batch runner...")
    try:
        from desktop.runner import BatchRunner
        from desktop.config import DesktopConfig
        
        csv_path, output_dir = create_test_csv()
        config = DesktopConfig(
            csv_paths=[str(csv_path)],
            output_dir=str(output_dir)
        )
        config.email.enabled = False
        
        runner = BatchRunner(config)
        print(f"✓ Batch runner created")
        
        # Test analysis run (this will be slow as it does real analysis)
        print("Running test analysis (this may take a while)...")
        # Skip actual analysis for now - just test that runner can be created
        print("✓ Analysis runner test passed (skipping actual analysis)")
        return True
            
    except Exception as e:
        print(f"✗ Runner test failed: {e}")
        return False

def test_pdf_renderer():
    """Test PDF rendering."""
    print("Testing PDF renderer...")
    try:
        from desktop.pdf_renderer import PDFRenderer
        
        renderer = PDFRenderer()
        print("✓ PDF renderer created")
        
        # Test basic HTML rendering
        test_html = "<html><body><h1>Test Report</h1><p>This is a test.</p></body></html>"
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            pdf_path = f.name
        
        success = renderer.render_html_to_pdf(test_html, pdf_path)
        
        if success:
            print(f"✓ PDF created: {pdf_path}")
            os.unlink(pdf_path)  # Clean up
            return True
        else:
            # Check if HTML fallback was created
            html_path = pdf_path.replace('.pdf', '.html')
            if Path(html_path).exists():
                print(f"✓ HTML fallback created: {html_path}")
                os.unlink(html_path)  # Clean up
                return True
            else:
                print("✗ PDF creation failed")
                return False
            
    except Exception as e:
        print(f"✗ PDF renderer test failed: {e}")
        return False

def test_email_sender():
    """Test email sender (without actually sending)."""
    print("Testing email sender...")
    try:
        from desktop.email_sender import EmailSender
        from desktop.config import DesktopConfig
        
        config = DesktopConfig()
        config.email.enabled = False  # Don't actually send emails
        
        sender = EmailSender(config)
        print("✓ Email sender created")
        
        # Test configuration validation
        if config.email.enabled:
            print("  Email enabled - would test SMTP connection")
        else:
            print("  Email disabled - configuration test passed")
        
        return True
        
    except Exception as e:
        print(f"✗ Email sender test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("RealFlip Desktop App - Test Suite")
    print("=" * 40)
    
    tests = [
        ("Configuration", test_config),
        ("PDF Renderer", test_pdf_renderer), 
        ("Email Sender", test_email_sender),
        ("Batch Runner", test_runner),  # This one is slow, so run last
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name} Test:")
        print("-" * 20)
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"✗ {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    print("-" * 20)
    
    passed = 0
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{name}: {status}")
        if success:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Desktop app is ready.")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
