#!/usr/bin/env python3
"""
Test script to verify Grammy Engine music generation works
This tests the core music generation functionality without full backend infrastructure
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all required imports work"""
    print("Testing imports...")
    
    try:
        import torch
        print(f"✓ PyTorch installed: {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
    except ImportError as e:
        print(f"✗ PyTorch import failed: {e}")
        return False
    
    try:
        from transformers import AutoProcessor, MusicgenForConditionalGeneration
        print("✓ Transformers installed")
    except ImportError as e:
        print(f"✗ Transformers import failed: {e}")
        return False
    
    try:
        import librosa
        print(f"✓ Librosa installed: {librosa.__version__}")
    except ImportError as e:
        print(f"✗ Librosa import failed: {e}")
        return False
    
    try:
        from pydub import AudioSegment
        print("✓ Pydub installed")
    except ImportError as e:
        print(f"✗ Pydub import failed: {e}")
        return False
    
    try:
        import scipy
        print(f"✓ Scipy installed: {scipy.__version__}")
    except ImportError as e:
        print(f"✗ Scipy import failed: {e}")
        return False
    
    print("\n✓ All core dependencies available\n")
    return True


def test_musicgen_basic():
    """Test basic MusicGen functionality"""
    print("Testing MusicGen basic functionality...")
    
    try:
        from services.musicgen_service import get_model_name, get_model
        
        # Test model name selection
        model_name = get_model_name('small')
        print(f"✓ Model name: {model_name}")
        
        # Try to load model (this will download if needed)
        print("  Loading model (this may take a while on first run)...")
        model_data = get_model(model_name)
        
        if model_data:
            print("✓ Model loaded successfully")
            print(f"  Device: {model_data['device']}")
            return True
        else:
            print("✗ Model loading failed")
            return False
            
    except Exception as e:
        print(f"✗ MusicGen test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_music_generation():
    """Test actual music generation"""
    print("\nTesting music generation...")
    
    try:
        from services.musicgen_service import generate_music
        import tempfile
        
        # Generate a short test track
        prompt = "upbeat electronic dance music, 120 BPM"
        duration = 5  # Short duration for testing
        
        print(f"  Generating 5-second test track...")
        print(f"  Prompt: '{prompt}'")
        
        output_path = generate_music(
            prompt=prompt,
            duration=duration,
            model='small',  # Use small model for faster testing
            temperature=1.0
        )
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✓ Audio file generated: {output_path}")
            print(f"  File size: {file_size:,} bytes")
            
            # Verify it's a valid audio file
            import wave
            try:
                with wave.open(output_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    duration_actual = frames / float(rate)
                    print(f"  Duration: {duration_actual:.2f}s")
                    print(f"  Sample rate: {rate} Hz")
                    print(f"  Channels: {wav_file.getnchannels()}")
                
                # Clean up
                os.remove(output_path)
                print("\n✓ Music generation test PASSED!\n")
                return True
                
            except Exception as e:
                print(f"✗ Generated file is not valid WAV: {e}")
                return False
        else:
            print("✗ Audio file not generated")
            return False
            
    except Exception as e:
        print(f"✗ Music generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration system"""
    print("Testing configuration...")
    
    try:
        from utils.config import (
            is_lightweight_mode,
            get_model_size,
            get_model_precision,
            log_configuration
        )
        
        print(f"  Lightweight mode: {is_lightweight_mode()}")
        print(f"  Model size: {get_model_size()}")
        print(f"  Model precision: {get_model_precision()}")
        
        print("\n✓ Configuration loaded\n")
        log_configuration()
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Grammy Engine - Music Generation Test")
    print("=" * 60)
    print()
    
    # Run tests in order
    tests = [
        ("Configuration", test_config),
        ("Imports", test_imports),
        ("MusicGen Basic", test_musicgen_basic),
        ("Music Generation", test_music_generation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"Test: {test_name}")
        print(f"{'=' * 60}\n")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "=" * 60)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("✓ ALL TESTS PASSED - Music generation is working!")
        print("\nThe Grammy Engine core music generation pipeline is functional.")
        print("You can now:")
        print("  1. Start the backend server")
        print("  2. Test the API endpoints")
        print("  3. Generate full tracks")
        return 0
    else:
        print("✗ SOME TESTS FAILED - Music generation needs fixing")
        failed_tests = [name for name, passed in results.items() if not passed]
        print(f"\nFailed tests: {', '.join(failed_tests)}")
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
