# F.R.I.D.A.Y.

F.R.I.D.A.Y. is an Iron Man-inspired local AI assistant with a browser dashboard and a terminal mode. Ask it to explain code, break down a task, or brainstorm ideas. It remembers the last six completed exchanges in the current session and can read replies aloud.

The Python app uses an existing small language model through Ollama. The default is Gemma 3 1B, which is about an 806 MB download. After setup, chat runs on your computer and needs no API key.

## Quick start

Install [Python 3.9 or newer](https://www.python.org/downloads/) and [Ollama](https://ollama.com/download). Open Ollama, or run `ollama serve` in a separate terminal if it isn't already running. Then open a terminal in this folder and run:

```sh
ollama pull gemma3:1b
python3 web.py
```

Open [127.0.0.1:8765](http://127.0.0.1:8765) in your browser. Use **Voice on** to hear replies when your browser supports speech synthesis. **New chat** clears the current conversation. The dashboard keeps messages in the current tab and clears them when the page reloads.

## Terminal mode

Run `python3 friday.py` for the command-line interface. On Windows, use `py friday.py` if `python3` isn't available. On macOS, run `python3 friday.py --speak` to hear replies. To switch to another installed Ollama model, pass its tag with `--model` to either entry point.

| Command | Action |
| --- | --- |
| `/help` | Show the available commands |
| `/status` | Show the model, retained turns, and voice setting |
| `/time` | Get the current local time from your computer |
| `/reset` | Clear conversation history |
| `/exit` | Close F.R.I.D.A.Y. |

The app keeps chat history in memory and sends prompts to Ollama on localhost. It has no file access, web browsing, or shell execution interface. Terminal speech uses the macOS system voice.

[Ollama chat API](https://docs.ollama.com/api/chat) · [Gemma 3 model page](https://ollama.com/library/gemma3:1b)
