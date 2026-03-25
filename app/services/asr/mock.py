from app.services.asr.base import AsrBackendStatus, AsrResult, StreamingAsr


class MockStreamingAsr(StreamingAsr):
    def __init__(self) -> None:
        self.chunk_index = 0

    def status(self) -> AsrBackendStatus:
        return AsrBackendStatus(
            engine="mock",
            ready=True,
            details={"mode": "simulated"},
        )

    async def transcribe_chunk(
        self,
        pcm_chunk: bytes,
        sample_rate: int,
        language: str,
        is_final: bool,
    ) -> AsrResult:
        self.chunk_index += 1
        effective_language = language if language != "auto" else "ko"
        seconds = len(pcm_chunk) / 2 / max(sample_rate, 1)
        state = "final" if is_final else "partial"
        text = f"[{state} chunk {self.chunk_index}] received {seconds:.2f}s of audio"

        return AsrResult(
            text=text,
            language=effective_language,
            is_final=is_final,
        )
