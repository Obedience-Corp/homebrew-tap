# frozen_string_literal: true

class Gaze < Formula
  desc "Give your agents eyes. Native PTZ. No vendor app."
  homepage "https://github.com/Obedience-Corp/gaze"
  url "https://github.com/Obedience-Corp/gaze/archive/refs/tags/v0.3.0.tar.gz"
  sha256 "3aa68a62438cb2f7235d0215113120a2e74bafa944d0af7c8973c147e754021e"
  license "Apache-2.0"
  head "https://github.com/Obedience-Corp/gaze.git", branch: "main"

  depends_on "just" => :build

  on_linux do
    depends_on "jpeg-turbo"
    depends_on "pkgconf" => :build
  end

  def install
    if OS.linux?
      ENV.prepend_path "PKG_CONFIG_PATH", Formula["jpeg-turbo"].opt_lib/"pkgconfig"
    end

    system "just", "dist"
    bin.install "bin/gaze"
  end

  def caveats
    linux_note = OS.linux? ? "\nOn Linux the user must be in group video (/dev/video*).\n" : ""
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
      #{linux_note}
    EOS
  end

  test do
    assert_match "0.3.0", shell_output("#{bin}/gaze --version")
  end
end
