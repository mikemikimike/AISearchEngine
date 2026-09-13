import threading
import wave

from audio_recorder import AudioRecorder


class FakeStream:
    def __init__(self):
        self.read_started = threading.Event()
        self.stopped = threading.Event()

    def read(self, _chunk):
        self.read_started.set()
        self.stopped.wait()
        raise RuntimeError("stream stopped")

    def stop_stream(self):
        self.stopped.set()

    def close(self):
        pass


class FakeAudio:
    def __init__(self):
        self.stream = FakeStream()

    def open(self, **_kwargs):
        return self.stream

    def get_sample_size(self, _format):
        return 2


def test_recording_runs_off_callback_thread_and_writes_on_stop(tmp_path):
    audio = FakeAudio()
    output = tmp_path / "Audio" / "question.wav"
    recorder = AudioRecorder(audio, str(output), 16, 1, 44100, 1024)

    assert recorder.start() is True
    assert audio.stream.read_started.wait(timeout=1)
    assert recorder.start() is False

    recorder.stop()

    assert output.exists()
    with wave.open(str(output), "rb") as recorded:
        assert recorded.getnchannels() == 1
        assert recorded.getsampwidth() == 2
        assert recorded.getframerate() == 44100


def test_stop_before_worker_opens_stream_is_safe(tmp_path):
    recorder = AudioRecorder(FakeAudio(), str(tmp_path / "question.wav"), 16, 1, 44100, 1024)

    assert recorder.start() is True
    recorder.stop()

    assert recorder.start() is True
    recorder.stop()
