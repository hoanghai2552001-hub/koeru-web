/* ════════════════════════════════
   KANA SPEED — Audio
   MP3 local → Web Speech API fallback
════════════════════════════════ */

let audioEnabled = true;
const audioCache = {};

function toggleAudio() {
  audioEnabled = !audioEnabled;
  const btn = document.getElementById('audio-toggle');
  btn.textContent = audioEnabled ? '🔊' : '🔇';
  btn.classList.toggle('muted', !audioEnabled);
  if (!audioEnabled) speechSynthesis.cancel();
}

function playKanaAudio(kana) {
  if (!audioEnabled) return;

  if (selectedLevel === 3) {
    // Thử MP3 local (Google TTS) trước, fallback Web Speech API
    const a = new Audio(`audio/vocab/${encodeURIComponent(kana)}.mp3`);
    a.oncanplaythrough = () => a.play().catch(() => speakWithAPI(kana));
    a.onerror          = () => speakWithAPI(kana);
    a.load();
    return;
  }

  // Level 1 & 2: phát từng ký tự qua MP3
  playCharsSequence([...kana], 0);
}

function speakWithAPI(kana) {
  if (!window.speechSynthesis || !audioEnabled) return;
  speechSynthesis.cancel();

  const utter = new SpeechSynthesisUtterance(kana);
  utter.lang   = 'ja-JP';
  utter.rate   = 0.78;
  utter.pitch  = 1.0;
  utter.volume = 1.0;

  const PREFERRED = ['Haruka', 'Sayaka', 'Ayumi', 'Ichiro'];
  const speak = () => {
    const voices = speechSynthesis.getVoices().filter(v => v.lang === 'ja-JP' && v.localService);
    let picked = null;
    for (const name of PREFERRED) { picked = voices.find(v => v.name.includes(name)); if (picked) break; }
    if (!picked && voices.length) picked = voices[0];
    if (picked) utter.voice = picked;
    setTimeout(() => speechSynthesis.speak(utter), 80);
  };

  if (speechSynthesis.getVoices().length) speak();
  else speechSynthesis.addEventListener('voiceschanged', speak, { once: true });
}

function playCharsSequence(chars, idx) {
  if (idx >= chars.length) return;
  const c = chars[idx];

  const onNext = () => playCharsSequence(chars, idx + 1);

  if (!audioCache[c]) {
    const a = new Audio(`audio/kana/${c}.mp3`);
    a.onerror = onNext;
    a.onended = onNext;
    audioCache[c] = a;
    a.play().catch(onNext);
  } else {
    const a = audioCache[c];
    a.currentTime = 0;
    a.onended = onNext;
    a.play().catch(onNext);
  }
}
