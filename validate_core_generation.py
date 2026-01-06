#!/usr/bin/env python3
"""
SIMPLE TEST - Grammy Engine Music Generation Validation
Tests ONLY the core music generation - the heart of the system
"""
import os
import sys

print("=" * 70)
print("GRAMMY ENGINE - CORE MUSIC GENERATION VALIDATION")
print("=" * 70)
print()

# Test 1: Can we import the AI models?
print("TEST 1: Checking AI Model Dependencies")
print("-" * 70)

try:
    import torch
    print(f"✓ PyTorch: {torch.__version__}")
    print(f"  CUDA available: {torch.cuda.is_available()}")
    print(f"  Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
except ImportError as e:
    print(f"✗ FAILED: PyTorch not installed: {e}")
    sys.exit(1)

try:
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    print(f"✓ Transformers installed (HuggingFace)")
except ImportError as e:
    print(f"✗ FAILED: Transformers not installed: {e}")
    sys.exit(1)

try:
    from scipy.io import wavfile
    import numpy as np
    print(f"✓ Audio processing libraries (scipy.io.wavfile, numpy {np.__version__})")
except ImportError as e:
    print(f"✗ FAILED: Audio libraries not installed: {e}")
    sys.exit(1)

print("\n✓ TEST 1 PASSED - All required AI libraries available\n")

# Test 2: Can we load the MusicGen model?
print("TEST 2: Loading MusicGen Model")
print("-" * 70)

try:
    print("Loading facebook/musicgen-small model...")
    print("(This will download ~1.5GB on first run - please be patient)")
    
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    
    print(f"✓ Model loaded successfully on {device}")
    print(f"  Model size: {sum(p.numel() for p in model.parameters())/1e6:.1f}M parameters")
    
except Exception as e:
    print(f"✗ FAILED: Could not load MusicGen model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ TEST 2 PASSED - MusicGen model loaded and ready\n")

# Test 3: Can we actually generate music?
print("TEST 3: Generating Music (5 seconds)")
print("-" * 70)

try:
    # Create a simple prompt
    prompt = "upbeat electronic dance music with drums, 120 BPM"
    print(f"Prompt: '{prompt}'")
    print(f"Duration: 5 seconds")
    print()
    print("Generating... (this takes ~10-30 seconds)")
    
    # Process prompt
    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt",
    ).to(device)
    
    # Generate audio
    # MusicGen generates ~50 tokens per second at 32kHz
    max_new_tokens = int(5 * 50)  # 5 seconds
    
    with torch.no_grad():
        audio_values = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=1.0
        )
    
    # Convert to numpy
    audio_array = audio_values[0, 0].cpu().numpy()
    sample_rate = model.config.audio_encoder.sampling_rate
    
    print(f"✓ Audio generated successfully!")
    print(f"  Shape: {audio_array.shape}")
    print(f"  Sample rate: {sample_rate} Hz")
    print(f"  Duration: {len(audio_array) / sample_rate:.2f} seconds")
    print(f"  Min value: {audio_array.min():.4f}")
    print(f"  Max value: {audio_array.max():.4f}")
    
    # Normalize audio
    audio_array = audio_array / max(abs(audio_array.min()), abs(audio_array.max()))
    
    print(f"  Normalized: min={audio_array.min():.4f}, max={audio_array.max():.4f}")
    
except Exception as e:
    print(f"✗ FAILED: Could not generate music: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ TEST 3 PASSED - Music generation successful!\n")

# Test 4: Can we save the audio file?
print("TEST 4: Saving Audio to File")
print("-" * 70)

try:
    
    output_file = "/tmp/grammy_test_output.wav"
    
    # Convert to int16 for WAV file
    audio_int16 = (audio_array * 32767).astype(np.int16)
    
    # Save WAV file
    wavfile.write(output_file, sample_rate, audio_int16)
    
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✓ Audio file saved: {output_file}")
        print(f"  File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Verify we can read it back
        rate, data = wavfile.read(output_file)
        print(f"  Verified: {rate} Hz, {len(data)} samples")
        
    else:
        print(f"✗ FAILED: File not created")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ FAILED: Could not save audio file: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✓ TEST 4 PASSED - Audio file saved successfully\n")

# Final Summary
print("=" * 70)
print("VALIDATION COMPLETE - ALL TESTS PASSED! ✓")
print("=" * 70)
print()
print("The Grammy Engine CORE MUSIC GENERATION is working!")
print()
print("What this proves:")
print("  ✓ MusicGen AI model loads correctly")
print("  ✓ Text prompts are processed")
print("  ✓ Music is generated from prompts")
print("  ✓ Audio files are created successfully")
print()
print(f"Test output file: {output_file}")
print()
print("Next steps:")
print("  1. Test with longer durations (30-60 seconds)")
print("  2. Test different music styles/genres")
print("  3. Integrate with backend API")
print("  4. Add vocal generation")
print("  5. Add mastering pipeline")
print()
print("=" * 70)
