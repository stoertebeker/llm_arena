# LLM Arena (Python 3.12 + venv)

Dieses Projekt ist für **Python 3.12** ausgelegt und bringt Bootstrap-Skripte für eine **virtuelle Umgebung (venv)** mit.

## Schnellstart (Linux/macOS)

```bash
# im Projektordner
bash setup_venv.sh
source .venv/bin/activate
llm-arena --prompt "Erkläre TCP in drei Sätzen" --reveal-provenance false
```

Oder bequem per Wrapper, der die venv bei Bedarf automatisch anlegt:
```bash
bash run.sh --prompt "Erkläre TCP in drei Sätzen" --reveal-provenance false
```

## Schnellstart (Windows PowerShell)

```powershell
# im Projektordner
.\setup_venv.ps1
.\.venv\Scripts\Activate.ps1
llm-arena --prompt "Erkläre TCP in drei Sätzen" --reveal-provenance false
```

## Konfiguration

> **Wichtig:** Kopiere zuerst die `config.toml.example` zu `config.toml` und trage deine eigenen API-Keys und Endpunkte ein.

Alle zentralen Variablen liegen in **`config.toml`**:
- LiteLLM-Endpoint/Key (`[providers]`)
- Kandidaten- und Jury-Modelle (`[[candidates]]`, `[[judges]]`)
- Einstellungen (`[settings]`): `reveal_provenance`, `elo_*`, `temperature`, `top_p`, `max_tokens`, `request_timeout_seconds`, `retries`

API-Keys können per `ENV:NAME` referenziert werden (z. B. `ENV:LITELLM_API_KEY`).

## Alternativ: requirements.txt

Falls du kein `pip install -e .` nutzen willst, kannst du die Abhängigkeiten auch so installieren (innerhalb der venv):

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .   # optional, für CLI-Einstiegspunkt
```

## Ausführen

```bash
# innerhalb der venv
llm-arena --prompt "Vergleiche UDP und TCP in 5 Sätzen." --reveal-provenance false
```

Ergebnisse:
- Konsolen-JSON (Sieger, Votes, Scores, Gewinnertext)
- Vollständige Rohdaten: `runs/<run_id>.json`
- Events/Logs (JSONL): `logs/events.jsonl`
