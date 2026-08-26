import { useEffect, useRef, useState } from 'react'

/**
 * Voice input via the browser's built-in Web Speech API. Worth being honest about
 * what this is: it's free and needs zero new infrastructure, but it isn't open
 * source — Chrome's implementation calls Google's cloud speech recognition under the
 * hood. The genuinely open-source route (self-hosted Whisper) needs real compute
 * (ideally a GPU) that the current free-tier hosting doesn't have; this is the
 * pragmatic zero-cost option until that's worth paying for. Unsupported browsers
 * (Safari has partial support, Firefox effectively none) just don't get a mic button
 * — this must degrade gracefully, not break the page.
 */

type RecognitionResult = { transcript: string; isFinal: boolean }

// Map a subset of the app's Indian-language names to BCP-47 codes Chrome recognizes.
export const SPEECH_LANGUAGES: Record<string, string> = {
  english: 'en-IN',
  hindi: 'hi-IN',
  tamil: 'ta-IN',
  telugu: 'te-IN',
  kannada: 'kn-IN',
  malayalam: 'ml-IN',
  bengali: 'bn-IN',
  gujarati: 'gu-IN',
  marathi: 'mr-IN',
  punjabi: 'pa-IN',
  urdu: 'ur-IN',
}

function getSpeechRecognitionCtor(): any {
  if (typeof window === 'undefined') return null
  return (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition || null
}

export function isSpeechRecognitionSupported(): boolean {
  return getSpeechRecognitionCtor() !== null
}

export function useSpeechRecognition(onResult: (r: RecognitionResult) => void, lang = 'en-IN') {
  const [listening, setListening] = useState(false)
  const recognitionRef = useRef<any>(null)

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop?.()
    }
  }, [])

  function start() {
    const Ctor = getSpeechRecognitionCtor()
    if (!Ctor) return

    const recognition = new Ctor()
    recognition.lang = lang
    recognition.continuous = true
    recognition.interimResults = true

    recognition.onresult = (event: any) => {
      const result = event.results[event.results.length - 1]
      onResult({ transcript: result[0].transcript, isFinal: result.isFinal })
    }
    recognition.onerror = () => setListening(false)
    recognition.onend = () => setListening(false)

    recognitionRef.current = recognition
    recognition.start()
    setListening(true)
  }

  function stop() {
    recognitionRef.current?.stop?.()
    setListening(false)
  }

  return { listening, start, stop, supported: isSpeechRecognitionSupported() }
}
