# Games

A pile of vibe-coded browser games. Each game is a single self-contained `.html` file.

### 🎮 [Play → aeskildsen.github.io/games](https://aeskildsen.github.io/games/)

## How it works

- Drop a new `.html` file in the repo root.
- `build.py` generates `index.html` with a card for every game, and injects a floating "← Home" button into each game (idempotently).
- GitHub Actions runs the build on every push to `main` and deploys to Pages.

## Local build

```sh
python3 build.py
```

Then open `index.html`.
