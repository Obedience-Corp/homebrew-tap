# frozen_string_literal: true

class Gaze < Formula
  desc "Give your agents eyes. Native PTZ. No vendor app."
  homepage "https://github.com/Obedience-Corp/gaze"
  url "https://github.com/Obedience-Corp/gaze/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "1d0da709b8a3a543fbb26d3ae326f4a06ba451e7df030a46369201e563b5da60"
  license "Apache-2.0"
  # Linux V4L2 lands in gaze#5 (linux-uvc). Flip this to "main" after that merges.
  head "https://github.com/Obedience-Corp/gaze.git", branch: "linux-uvc"

  depends_on "just" => :build

  on_linux do
    depends_on "jpeg-turbo"
    depends_on "pkgconf" => :build
  end

  def install
    if OS.linux? && !build.head?
      odie <<~EOS
        gaze v#{version} is macOS-only. On Linux (Homebrew):

          brew install --HEAD Obedience-Corp/tap/gaze

        The next tagged release that includes Linux will make `brew install gaze` work.
      EOS
    end

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
    assert_match(/\d+\.\d+\.\d+/, shell_output("#{bin}/gaze --version"))
  end
end
