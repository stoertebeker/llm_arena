# LLM Arena

Ein Framework, um mehrere LLM-Anbieter in einem "Arena"-Stil gegeneinander antreten zu lassen. Pro Prompt werden Antworten von verschiedenen Modellen erzeugt, anonymisiert und von einer Jury (die ebenfalls aus LLMs besteht) bewertet. Das Ergebnis liefert einen klaren Sieger, detaillierte Bewertungen und ein optionales Elo-Rating.

## Features

- **Multi-Provider-Architektur:** Lässt standardmäßig OpenAI, Anthropic und Google gegeneinander antreten (erweiterbar).
- **Anonymisierte Bewertung:** Antworten werden als A/B/C gemischt und anonymisiert, um Bewertungs-Bias zu minimieren.
- **LLM-basierte Jury:** Nutzt eine Jury aus konfigurierbaren LLMs, um die Antworten anhand fester Kriterien zu bewerten.
- **Elo-Rating-System:** Berechnet optional Elo-Werte, um die relative Stärke der Modelle über mehrere Runden zu verfolgen.
- **Strikte JSON-Ausgabe:** Erzwingt und validiert strikte JSON-Antworten von der Jury für eine zuverlässige Datenauswertung.
- **Self-Preference-Bias-Analyse:** Mit dem Flag `--reveal-provenance` kann offengelegt werden, welches Modell welche Antwort generiert hat, um zu testen, ob Modelle sich selbst bevorzugen.

## 1. Setup & Konfiguration

Das Projekt ist für **Python 3.12** ausgelegt und richtet automatisch eine virtuelle Umgebung (`.venv`) ein.

**Schritt 1: Projekt klonen**

```bash
git clone https://github.com/stoertebeker/llm_arena.git
cd llm_arena
```

**Schritt 2: Umgebung einrichten**

Führe das passende Skript für dein Betriebssystem aus. Es erstellt die `.venv`, installiert alle Abhängigkeiten und macht das `llm-arena` Kommando verfügbar.

*   **macOS / Linux:**
    ```bash
    bash setup_venv.sh
    ```
*   **Windows (PowerShell):**
    ```powershell
    .\setup_venv.ps1
    ```

**Schritt 3: Konfiguration anpassen (Wichtig!)**

Kopiere die Beispiel-Konfiguration und passe sie mit deinen API-Informationen an.

```bash
cp config.toml.example config.toml
```

Öffne die `config.toml` und trage deinen LiteLLM-Endpunkt und API-Key (oder Referenzen zu Umgebungsvariablen) ein.

### Funktionsweise der Konfiguration

- **Nur OpenAI-kompatible APIs:** Das Framework ist darauf ausgelegt, mit Servern zu kommunizieren, die eine OpenAI-kompatible API bereitstellen (z.B. LiteLLM, Ollama, LM Studio).
- **Globale & Lokale Konfiguration:** Der `[providers]`-Block definiert die Standard-`base_url` und den `api_key` für alle Modelle.
- **Individuelle Anpassung:** Innerhalb eines `[[candidates]]`- oder `[[judges]]`-Blocks kannst du die `base_url` und den `api_key` überschreiben. Das ist nützlich, um verschiedene Dienste (z.B. LiteLLM und einen lokalen Ollama-Server) gleichzeitig zu verwenden.
- **Kandidaten & Judges:** Die Struktur für `[[candidates]]` und `[[judges]]` ist identisch. Du kannst jedes Modell sowohl als Antwort-Generator als auch als Bewerter einsetzen.

## 2. Benutzung

**Schritt 1: Virtuelle Umgebung aktivieren**

*   **macOS / Linux:**
    ```bash
    source .venv/bin/activate
    ```
*   **Windows (PowerShell):**
    ```powershell
    .\.venv\Scripts\Activate.ps1
    ```

**Schritt 2: Arena ausführen**

Führe einen Arena-Lauf mit einem beliebigen Prompt aus. Die Ergebnisse werden direkt in der Konsole angezeigt.

```bash
llm-arena --prompt "Erkläre das Prinzip der Gewaltenteilung in drei Sätzen."
```

Um den Self-Preference-Bias zu messen, nutze das `--reveal-provenance` Flag:
```bash
llm-arena --prompt "Was ist der Unterschied zwischen TCP und UDP?" --reveal-provenance
```

## 3. Ergebnisse

Nach jedem Lauf erhältst du:

1.  **Konsolen-Ausgabe:** Eine Zusammenfassung mit dem Gewinner, den Stimmen und der besten Antwort.
2.  **Detaillierte JSON-Datei:** Eine vollständige Aufschlüsselung des Laufs in `runs/<run_id>.json`.
3.  **Logs:** Alle Events, inklusive potenzieller Fehler bei der Bewertung, werden in `logs/events.jsonl` gespeichert.