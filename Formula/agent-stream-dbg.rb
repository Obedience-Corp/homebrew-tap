# typed: false
# frozen_string_literal: true

class AgentStreamDbg < Formula
  desc "TUI debugger for multi-agent event streams (SSE, gRPC, ACP)"
  homepage "https://github.com/Obedience-Corp/agent-stream-dbg"
  version "0.1.0"
  license "Apache-2.0"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/Obedience-Corp/agent-stream-dbg/releases/download/v0.1.0/agent-stream-dbg_v0.1.0_darwin_arm64.tar.gz"
      sha256 "7816ef166317b17377feb08873f245e9b92faea5a531cce04aec00f1731e48f3"

      def install
        bin.install "agent-stream-dbg"
      end
    end
    if Hardware::CPU.intel?
      url "https://github.com/Obedience-Corp/agent-stream-dbg/releases/download/v0.1.0/agent-stream-dbg_v0.1.0_darwin_amd64.tar.gz"
      sha256 "8647a6941139219b2877553144a9cebaef778cb86a573158a675aabd9bd1a8c8"

      def install
        bin.install "agent-stream-dbg"
      end
    end
  end

  on_linux do
    if Hardware::CPU.arm? && Hardware::CPU.is_64_bit?
      url "https://github.com/Obedience-Corp/agent-stream-dbg/releases/download/v0.1.0/agent-stream-dbg_v0.1.0_linux_arm64.tar.gz"
      sha256 "700d9d531616abd9a7328c430663626c117493165dfd09cc6d1ffe65fb80e621"

      def install
        bin.install "agent-stream-dbg"
      end
    end
    if Hardware::CPU.intel? && Hardware::CPU.is_64_bit?
      url "https://github.com/Obedience-Corp/agent-stream-dbg/releases/download/v0.1.0/agent-stream-dbg_v0.1.0_linux_amd64.tar.gz"
      sha256 "b64d965e59ce151b3b0584b6f98a7a8647616e814b09a1375f97ca8c0e706b10"

      def install
        bin.install "agent-stream-dbg"
      end
    end
  end

  test do
    assert_match "agent-stream-dbg", shell_output("#{bin}/agent-stream-dbg --help")
  end
end
