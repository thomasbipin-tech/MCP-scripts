"""
engines.py — Pluggable Malayalam TTS back-ends.

Every engine exposes the same tiny interface:
    engine.sample_rate -> int
    engine.synth(text: str) -> np.ndarray  (float32, mono, [-1, 1])

Heavy models are loaded lazily on first synth so the rest of the pipeline
(and the test suite) runs without torch installed.

Engines
-------
IndicParlerEngine : ai4bharat/indic-parler-tts  (Apache-2.0)
    Description-controlled voice. Pick a male narrator with a caption; the
    "Narration" emotion is officially supported for Malayalam. No reference
    audio needed. Best default for a clean, consistent audiobook narrator.

IndicF5Engine : ai4bharat/IndicF5
    Reference-audio voice cloning *within Malayalam*. Give it a 5-10s WAV of
    a native male voice (bundled sample) for maximum authenticity, OR your
    OWN recording to narrate the book in your voice.

GTTSEngine : Google Translate TTS (online, free)
    Reliable fallback. Single (female-ish) voice, not audiobook-grade.
    Requires internet at generation time.

StubEngine : silent placeholder for dry-runs / plumbing tests.
"""
from __future__ import annotations
import numpy as np

# --- Recommended male-narrator captions for Indic Parler (Malayalam) --------
# The caption controls gender/pace/tone. "Anjali/Aditi" etc. are the model's
# recommended named speakers; for a male narrator we describe the voice.
MALE_NARRATOR_DESC = (
    "A middle-aged male speaker narrates in Malayalam with a calm, warm and "
    "clear voice. He speaks slowly and expressively at a measured, storytelling "
    "pace. The recording is very clear and close-sounding with no background noise."
)


class StubEngine:
    """Returns silence sized to the text. Used for tests and dry runs."""
    sample_rate = 24000

    def synth(self, text: str) -> np.ndarray:
        seconds = max(0.4, len(text) * 0.06)  # ~natural reading rate
        return np.zeros(int(self.sample_rate * seconds), dtype=np.float32)


class IndicParlerEngine:
    def __init__(self, description: str = MALE_NARRATOR_DESC, device: str | None = None):
        self.description = description
        self.device = device
        self._model = None
        self._tok = None
        self._desc_tok = None
        self.sample_rate = 44100  # overwritten after load

    def _load(self):
        import torch
        from parler_tts import ParlerTTSForConditionalGeneration
        from transformers import AutoTokenizer

        self.device = self.device or ("cuda:0" if torch.cuda.is_available() else "cpu")
        self._model = ParlerTTSForConditionalGeneration.from_pretrained(
            "ai4bharat/indic-parler-tts"
        ).to(self.device)
        self._tok = AutoTokenizer.from_pretrained("ai4bharat/indic-parler-tts")
        self._desc_tok = AutoTokenizer.from_pretrained(
            self._model.config.text_encoder._name_or_path
        )
        self.sample_rate = self._model.config.sampling_rate

    def synth(self, text: str) -> np.ndarray:
        if self._model is None:
            self._load()
        d = self._desc_tok(self.description, return_tensors="pt").to(self.device)
        p = self._tok(text, return_tensors="pt").to(self.device)
        gen = self._model.generate(
            input_ids=d.input_ids, attention_mask=d.attention_mask,
            prompt_input_ids=p.input_ids, prompt_attention_mask=p.attention_mask,
        )
        return gen.cpu().numpy().squeeze().astype(np.float32)


class IndicF5Engine:
    """Voice cloning. Provide ref_audio_path (5-10s WAV) + its ref_text
    (exact Malayalam transcript of that clip)."""
    sample_rate = 24000

    def __init__(self, ref_audio_path: str, ref_text: str, device: str | None = None):
        if not ref_audio_path or not ref_text:
            raise ValueError("IndicF5 needs a reference WAV and its transcript.")
        self.ref_audio_path = ref_audio_path
        self.ref_text = ref_text
        self.device = device
        self._model = None

    def _load(self):
        import torch
        from transformers import AutoModel
        self.device = self.device or ("cuda:0" if torch.cuda.is_available() else "cpu")
        self._model = AutoModel.from_pretrained(
            "ai4bharat/IndicF5", trust_remote_code=True
        ).to(self.device)

    def synth(self, text: str) -> np.ndarray:
        if self._model is None:
            self._load()
        audio = self._model(text, ref_audio_path=self.ref_audio_path, ref_text=self.ref_text)
        audio = np.asarray(audio)
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0
        return audio.astype(np.float32).squeeze()


class GTTSEngine:
    """Online fallback. Female-ish single voice; use only if the neural
    models are unavailable."""
    sample_rate = 24000

    def synth(self, text: str) -> np.ndarray:
        import io
        from gtts import gTTS
        from pydub import AudioSegment
        buf = io.BytesIO()
        gTTS(text, lang="ml").write_to_fp(buf)
        buf.seek(0)
        seg = AudioSegment.from_file(buf, format="mp3").set_channels(1).set_frame_rate(self.sample_rate)
        samples = np.array(seg.get_array_of_samples()).astype(np.float32)
        return samples / (2 ** (8 * seg.sample_width - 1))


def build_engine(name: str, **kwargs):
    name = name.lower()
    if name in ("parler", "indic-parler", "a"):
        return IndicParlerEngine(**{k: v for k, v in kwargs.items() if k in ("description", "device")})
    if name in ("indicf5", "f5", "clone", "own", "b"):
        return IndicF5Engine(**{k: v for k, v in kwargs.items() if k in ("ref_audio_path", "ref_text", "device")})
    if name in ("gtts", "fallback"):
        return GTTSEngine()
    if name in ("stub", "test"):
        return StubEngine()
    raise ValueError(f"Unknown engine: {name}")
