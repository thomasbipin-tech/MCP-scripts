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


# Microsoft's free Malayalam neural voices (Edge TTS): a solid male narrator
# and a female one. No gated model, no GPU, no login — just internet.
EDGE_MALE = "ml-IN-MidhunNeural"
EDGE_FEMALE = "ml-IN-SobhanaNeural"


class EdgeTTSEngine:
    """Microsoft Edge neural TTS (free, online, no GPU, no gated model).

    A strong, natural Malayalam narrator that works where the AI4Bharat
    models can't be run — no local GPU, or a locked-down box that can't
    download the (multi-GB, sometimes gated) Hugging Face weights. Pick the
    male (default) or female voice; `rate`/`pitch` shape the delivery (e.g.
    rate="-10%", pitch="-15Hz" for a slower, deeper storytelling tone).

    `proxy` is passed through to edge-tts for environments behind an
    HTTPS proxy.
    """
    sample_rate = 24000

    def __init__(self, voice: str = EDGE_MALE, rate: str = "-6%",
                 pitch: str = "+0Hz", proxy: str | None = None):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.proxy = proxy

    def synth(self, text: str) -> np.ndarray:
        import io, asyncio
        import edge_tts
        from pydub import AudioSegment

        async def _stream() -> bytes:
            comm = edge_tts.Communicate(text, voice=self.voice, rate=self.rate,
                                        pitch=self.pitch, proxy=self.proxy)
            buf = io.BytesIO()
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
            return buf.getvalue()

        mp3 = asyncio.run(_stream())
        seg = (AudioSegment.from_file(io.BytesIO(mp3), format="mp3")
               .set_channels(1).set_frame_rate(self.sample_rate))
        samples = np.array(seg.get_array_of_samples()).astype(np.float32)
        return samples / (2 ** (8 * seg.sample_width - 1))


class VoiceMatchEngine:
    """Token-free voice *matching* (timbre transfer) — NOT true cloning.

    Renders text with a base neural voice (Edge TTS by default), then applies
    OpenVoice v2 tone-color conversion toward a reference clip. The OpenVoice
    converter is a small, ungated Hugging Face model, so this runs on CPU with
    no login — useful when IndicF5 (the real cloning engine) is out of reach.

    Honest limits: it matches the reference's *timbre and pitch*, but NOT its
    accent, rhythm or pronunciation — those come from the base voice. For an
    accent-faithful clone use `IndicF5Engine` (needs its gated model + a GPU).

    `ref_audio_path` may be a single clip or a list of clean segments (the
    speaker embedding is averaged over them, which is more robust).
    """

    def __init__(self, ref_audio_path, base_engine=None, tau: float = 0.9,
                 device: str | None = None, edge_proxy: str | None = None):
        if not ref_audio_path:
            raise ValueError("VoiceMatch needs a reference WAV (or list of WAVs).")
        self.ref = [ref_audio_path] if isinstance(ref_audio_path, str) else list(ref_audio_path)
        self.base = base_engine or EdgeTTSEngine(proxy=edge_proxy)
        self.tau = tau
        self.device = device
        self._model = None
        self._tgt_se = None
        self.sample_rate = 22050  # OpenVoice v2 converter output rate

    def _load(self):
        import os
        os.environ.setdefault("COQUI_TOS_AGREED", "1")
        from TTS.api import TTS
        api = TTS(
            model_name="voice_conversion_models/multilingual/multi-dataset/openvoice_v2",
            progress_bar=False,
        )
        self._model = api.voice_converter.vc_model
        self._model.tau = self.tau
        # Cache the target speaker embedding once (not per chunk).
        self._tgt_se = self._model.clone_voice(self.ref)["speaker_embedding"]

    def synth(self, text: str) -> np.ndarray:
        import tempfile, os
        import soundfile as sf
        import torch
        if self._model is None:
            self._load()
        base_audio = self.base.synth(text)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            src_path = tf.name
        try:
            sf.write(src_path, base_audio, self.base.sample_rate)
            with torch.inference_mode():
                src_se, src_spec = self._model.extract_se(src_path)
                out = self._model.inference(src_spec, {"g_src": src_se, "g_tgt": self._tgt_se})
            return out["model_outputs"][0, 0].data.cpu().float().numpy()
        finally:
            try:
                os.remove(src_path)
            except OSError:
                pass


def build_engine(name: str, **kwargs):
    name = name.lower()
    if name in ("parler", "indic-parler", "a"):
        return IndicParlerEngine(**{k: v for k, v in kwargs.items() if k in ("description", "device")})
    if name in ("indicf5", "f5", "clone", "own", "b"):
        return IndicF5Engine(**{k: v for k, v in kwargs.items() if k in ("ref_audio_path", "ref_text", "device")})
    if name in ("edge", "edge-tts", "neural"):
        return EdgeTTSEngine(**{k: v for k, v in kwargs.items()
                                if k in ("voice", "rate", "pitch", "proxy")})
    if name in ("voicematch", "match", "openvoice"):
        return VoiceMatchEngine(**{k: v for k, v in kwargs.items()
                                   if k in ("ref_audio_path", "base_engine", "tau",
                                            "device", "edge_proxy")})
    if name in ("gtts", "fallback"):
        return GTTSEngine()
    if name in ("stub", "test"):
        return StubEngine()
    raise ValueError(f"Unknown engine: {name}")
