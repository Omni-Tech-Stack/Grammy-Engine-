"""
Configuration utilities for ARM optimization and lightweight mode
"""
import os
import platform
import logging

logger = logging.getLogger(__name__)


def is_arm_architecture():
    """
    Detect if running on ARM architecture
    
    Checks for common ARM identifiers in platform.machine():
    - arm, armv7l, armv8l (32-bit ARM)
    - aarch64, arm64 (64-bit ARM)
    
    Note: This is a heuristic check. For production use with emulation
    environments, consider additional validation.
    """
    machine = platform.machine().lower()
    arm_identifiers = ['arm', 'aarch64', 'arm64', 'armv7', 'armv8']
    return any(identifier in machine for identifier in arm_identifiers)


def is_lightweight_mode():
    """
    Check if lightweight mode is enabled
    Auto-enables on ARM unless explicitly disabled
    """
    explicit_mode = os.getenv('LIGHTWEIGHT_MODE', '').lower()
    
    if explicit_mode in ('true', '1', 'yes'):
        return True
    elif explicit_mode in ('false', '0', 'no'):
        return False
    
    # Auto-enable on ARM
    return is_arm_architecture()


def get_model_size():
    """
    Get appropriate model size based on architecture and mode
    Returns: 'small', 'medium', or 'large'
    """
    if is_lightweight_mode():
        return os.getenv('MODEL_SIZE', 'small')
    return os.getenv('MODEL_SIZE', 'medium')


def get_audio_buffer_size():
    """
    Get audio processing buffer size optimized for architecture
    """
    if is_lightweight_mode():
        # Smaller buffer for ARM - reduces memory by ~75%
        return int(os.getenv('AUDIO_BUFFER_SIZE', '2048'))
    # Standard buffer size
    return int(os.getenv('AUDIO_BUFFER_SIZE', '8192'))


def get_worker_concurrency():
    """
    Get optimal worker concurrency based on mode
    """
    if is_lightweight_mode():
        # Reduce concurrency on ARM
        return int(os.getenv('WORKER_CONCURRENCY', '1'))
    return int(os.getenv('WORKER_CONCURRENCY', '2'))


def get_model_precision():
    """
    Get model precision (float32, float16, or int8)
    """
    if is_lightweight_mode():
        # Use INT8 quantization on ARM for 3x speed, 75% less memory
        return os.getenv('MODEL_PRECISION', 'int8')
    return os.getenv('MODEL_PRECISION', 'float32')


def get_max_audio_duration():
    """
    Get maximum audio duration based on mode
    """
    if is_lightweight_mode():
        return int(os.getenv('MAX_AUDIO_DURATION', '60'))
    return int(os.getenv('MAX_AUDIO_DURATION', '300'))


def log_configuration():
    """
    Log current configuration
    """
    logger.info("=" * 60)
    logger.info("Grammy Engine Configuration")
    logger.info("=" * 60)
    logger.info(f"Architecture: {platform.machine()}")
    logger.info(f"ARM Architecture: {is_arm_architecture()}")
    logger.info(f"Lightweight Mode: {is_lightweight_mode()}")
    logger.info(f"Model Size: {get_model_size()}")
    logger.info(f"Model Precision: {get_model_precision()}")
    logger.info(f"Audio Buffer Size: {get_audio_buffer_size()}")
    logger.info(f"Worker Concurrency: {get_worker_concurrency()}")
    logger.info(f"Max Audio Duration: {get_max_audio_duration()}s")
    logger.info("=" * 60)
