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
      in {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            python
            pkgs.ffmpeg
            pkgs.yt-dlp
          ];
          shellHook = ''
            if [ ! -d ".venv" ]; then
              echo "Creating Python venv in ./.venv"
              ${python}/bin/python -m venv .venv
            fi
            . .venv/bin/activate
            python -m pip install --upgrade pip
            if [ -f requirements.txt ]; then
              echo "Installing Python deps from requirements.txt"
              pip install -r requirements.txt
            fi
            export PYTHONPATH=$PWD/src:$PYTHONPATH
            echo "Dev shell ready."
            python -V || true
            ffmpeg -version | head -n1 || true
            yt-dlp --version || true
          '';
        };
      });
}
