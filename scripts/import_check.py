try:
    import av  # PyAV
    from faster_whisper import WhisperModel  # faster-whisper
    print("ok")
except Exception as e:
    print("import-error:", repr(e))
    raise
