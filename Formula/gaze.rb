# frozen_string_literal: true

class Gaze < Formula
  desc "Give your agents eyes. Native PTZ. No vendor app."
  homepage "https://github.com/Obedience-Corp/gaze"
  url "https://github.com/Obedience-Corp/gaze/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "1d0da709b8a3a543fbb26d3ae326f4a06ba451e7df030a46369201e563b5da60"
  license "Apache-2.0"

  depends_on :macos
  depends_on "just" => :build

  def install
    system "just", "dist"
    bin.install "bin/gaze"
  end

  def caveats
    <<~EOS
      List cameras:  gaze list
      Pin one for MCP (replace vid:pid):

        {
          "mcpServers": {
            "gaze": {
              "command": "#{opt_bin}/gaze",
              "args": ["-d", "2e1a:4c04", "mcp"]
            }
          }
        }
    EOS
  end

  test do
    assert_match "0.2.0", shell_output("#{bin}/gaze --version")
  end
end
