# Signing mode: ad-hoc
cask "obey-voice-app" do
  version "0.3.2"
  sha256 "03b4aa9fc5b4de804a4e27b2315cd41398fb45819a98c50ded2b4ca0d1da84f7"

  url "https://github.com/Obedience-Corp/obey-voice/releases/download/v#{version}/obey-voice-app-v#{version}-macos-arm64.zip"
  name "Obey Voice Agent"
  desc "Native desktop interface for Obey Voice"
  homepage "https://github.com/Obedience-Corp/obey-voice"

  depends_on arch: :arm64
  depends_on macos: :sequoia

  app "Obey Voice Agent.app"

  uninstall quit: "com.obedience.voice-agent"

  caveats <<~EOS
    This app is ad-hoc signed and is not notarized by Apple.
    After attempting to open it, macOS may require approval in
    System Settings > Privacy & Security > Open Anyway.
    Choose providers and download speech models during first-launch setup.
    The app includes its own engine and native libraries; the CLI formula is separate.
    Settings, personas, sessions, and model caches are retained on uninstall.
  EOS
end
