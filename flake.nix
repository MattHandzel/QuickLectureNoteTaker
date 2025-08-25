{ description = "QuickLectureNoteTaker dev shell";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python312;
        pythonEnv = python.withPackages (ps: with ps; [
          typer
          rich
          pydantic
          orjson
          tenacity
          rapidfuzz
          yt-dlp
          tiktoken
          pyyaml
          python-dateutil
          openai
          faster-whisper
        ]);
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.ffmpeg
            pkgs.yt-dlp
          ];
          shellHook = ''
            export PYTHONPATH=$PWD/src:$PYTHONPATH
            echo "Dev shell ready. Python: $(python -V)"
            echo "ffmpeg: $(ffmpeg -version | head -n1)"
            echo "yt-dlp: $(yt-dlp --version)"
          '';
        };
      });
}
