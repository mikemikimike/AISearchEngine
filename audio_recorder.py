from __future__ import annotations

import threading
import wave
from pathlib import Path
from typing import Any


class AudioRecorder:
    """Record audio on a worker thread without blocking the UI callback."""

    def __init__(
        self,
        audio: Any,
        output_file: str,
        audio_format: int,
        channels: int,
        rate: int,
        chunk: int,
    ) -> None:
        self._audio = audio
        self._output_file = Path(output_file)
        self._audio_format = audio_format
        self._channels = channels
        self._rate = rate
        self._chunk = chunk
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stream: Any = None
        self._frames: list[bytes] = []
        self._error: BaseException | None = None

    def start(self) -> bool:
        """Start recording, returning False when a recording is already active."""
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return False
            self._stop.clear()
            self._frames = []
            self._error = None
            self._thread = threading.Thread(target=self._record, daemon=True)
            self._thread.start()
            return True

    def _record(self) -> None:
        stream = None
        try:
            stream = self._audio.open(
                format=self._audio_format,
                channels=self._channels,
                rate=self._rate,
                input=True,
                frames_per_buffer=self._chunk,
            )
            with self._lock:
                self._stream = stream
            while not self._stop.is_set():
                try:
                    self._frames.append(stream.read(self._chunk))
                except Exception:
                    if not self._stop.is_set():
                        raise
                    break
        except BaseException as error:
            self._error = error
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                finally:
                    stream.close()
            with self._lock:
                self._stream = None
            if self._error is None:
                try:
                    self._write_file()
                except BaseException as error:
                    self._error = error

    def _write_file(self) -> None:
        self._output_file.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(self._output_file), "wb") as output:
            output.setnchannels(self._channels)
            output.setsampwidth(self._audio.get_sample_size(self._audio_format))
            output.setframerate(self._rate)
            output.writeframes(b"".join(self._frames))

    def stop(self) -> None:
        """Stop the worker and surface any recording error to the caller."""
        with self._lock:
            thread = self._thread
            stream = self._stream
        if thread is None:
            return
        self._stop.set()
        if stream is not None:
            stream.stop_stream()
        thread.join()
        with self._lock:
            self._thread = None
        if self._error is not None:
            raise self._error
