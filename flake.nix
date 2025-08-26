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
            VENV=".venv"
            WANT_MAJOR=3
            WANT_MINOR=12

            if [ -d "$VENV" ]; then
              CUR_PY="$VENV/bin/python"
              if ! "$CUR_PY" -c "import sys; exit(0) if sys.version_info[:2]==(${WANT_MAJOR},${WANT_MINOR}) else exit(1)"; then
                echo "Recreating venv with Python ${WANT_MAJOR}.${WANT_MINOR}"
                rm -rf "$VENV"
              fi
            fi

            if [ ! -d "$VENV" ]; then
              echo "Creating Python venv in ./.venv"
              ${python}/bin/python -m venv "$VENV"
            fi

            . "$VENV/bin/activate"
            export PATH="$PWD/$VENV/bin:$PATH"

            python -m pip install --upgrade pip
            if [ -f requirements.txt ]; then
              echo "Installing Python deps from requirements.txt"
              pip install -r requirements.txt
            fi

            if [ -f pyproject.toml ]; then
              echo "Installing package in editable mode to expose 'lecturen' console script"
              pip install -e .
            fi

            export PYTHONPATH=$PWD/src:$PYTHONPATH

            echo "Dev shell ready."
            echo -n "Python: " && python -V || true
            echo -n "ffmpeg: " && ffmpeg -version | head -n1 || true
            echo -n "yt-dlp: " && yt-dlp --version || true
          '';
        };
      });
}
