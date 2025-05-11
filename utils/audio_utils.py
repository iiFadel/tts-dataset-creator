import pyaudio

def get_input_devices():
    """
    Get list of available audio input devices.
    
    Returns:
        list: A list of tuples (device_index, device_name) for input devices
    """
    devices = []
    p = pyaudio.PyAudio()
    
    try:
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0:  # If it's an input device
                device_name = device_info.get('name')
                devices.append((i, device_name))
    finally:
        p.terminate()
        
    return devices

def get_device_info(device_index):
    """
    Get information about a specific audio device.
    
    Args:
        device_index (int): The index of the audio device
    
    Returns:
        dict: Device information dictionary
    """
    p = pyaudio.PyAudio()
    try:
        return p.get_device_info_by_index(device_index)
    finally:
        p.terminate()

def list_all_devices():
    """
    Print information about all available audio devices.
    Useful for debugging device selection issues.
    """
    p = pyaudio.PyAudio()
    
    info = "\nAudio Devices:\n"
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        info += f"Device {i}: {dev['name']}\n"
        info += f"  Input channels: {dev['maxInputChannels']}\n"
        info += f"  Output channels: {dev['maxOutputChannels']}\n"
        info += f"  Default Sample Rate: {dev['defaultSampleRate']}\n"
    
    p.terminate()
    
    return info