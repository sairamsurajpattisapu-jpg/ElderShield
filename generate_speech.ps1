Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

# Scenario A: Legitimate bank conversation mentioning OTP
$synth.SetOutputToWaveFile("$PSScriptRoot\legit_speech.wav")
$synth.Speak("Good morning Mr. Rao. This is State Bank of India customer verification. Please note, our branch never asks for your OTP or password over the phone. Please visit our MVP Colony branch at your convenience.")

# Scenario B: Progressive scam conversation
$synth.SetOutputToWaveFile("$PSScriptRoot\scam_speech.wav")
$synth.Speak("This is Officer Sharma from Central Bureau of Investigation New Delhi headquarters. A parcel addressed to you was intercepted with contraband. You are under digital arrest. Do not inform your family or disconnect this call. Transfer eighty five thousand rupees to our RBI verification escrow account immediately.")

# Scenario C: Ambiguous delivery conversation
$synth.SetOutputToWaveFile("$PSScriptRoot\ambiguous_speech.wav")
$synth.Speak("Hello sir, I am calling from the courier service regarding your parcel. Are you available at your address today?")

$synth.Dispose()
Write-Output "All 3 speech audio files generated successfully."
