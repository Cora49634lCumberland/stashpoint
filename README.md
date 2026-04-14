# stashpoint

A lightweight CLI for managing and restoring named environment variable snapshots across projects.

---

## Installation

```bash
pip install stashpoint
```

Or install from source:

```bash
git clone https://github.com/yourname/stashpoint.git && cd stashpoint && pip install .
```

---

## Usage

Save the current environment as a named snapshot:

```bash
stashpoint save myproject-dev
```

List all saved snapshots:

```bash
stashpoint list
```

Restore a snapshot into your current shell session:

```bash
eval $(stashpoint load myproject-dev)
```

Delete a snapshot you no longer need:

```bash
stashpoint delete myproject-dev
```

Snapshots are stored locally in `~/.stashpoint/` as simple JSON files, making them easy to inspect or version control manually.

---

## Why stashpoint?

Switching between projects often means juggling different API keys, database URLs, and config flags. `stashpoint` lets you snapshot your environment once and restore it instantly — no `.env` file conflicts, no shell plugin required.

---

## License

MIT © 2024 [Your Name](https://github.com/yourname)