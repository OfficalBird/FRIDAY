"""F.R.I.D.A.Y. — a local terminal assistant powered by Ollama."""

import argparse
from collections import deque
from datetime import datetime
import json
import shutil
import subprocess
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MODEL = "gemma3:1b"
CHAT_URL = "http://127.0.0.1:11434/api/chat"
PERSONA = {
    "role": "system",
    "content": (
        "You are F.R.I.D.A.Y., a composed, resourceful personal assistant "
        "with dry wit. Give concise, practical answers. Ask for missing "
        "details when needed. Be clear about uncertainty. You can only "
        "reply in this chat. Never claim you accessed files, ran commands, "
        "browsed the web, or performed actions outside the chat."
    ),
}
HELP = "/help commands · /status configuration · /time local time · /reset clear chat · /exit quit"


def chat(model, history, prompt):
    messages = [PERSONA, *history, {"role": "user", "content": prompt}]
    request = Request(
        CHAT_URL,
        data=json.dumps({"model": model, "messages": messages, "stream": False,
                         "options": {"num_predict": 512}}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=120) as response:
            answer = json.load(response)["message"]["content"].strip()
    except HTTPError as error:
        if error.code == 404:
            raise RuntimeError(f"Model unavailable. Try: ollama pull {model}") from error
        raise RuntimeError(f"Ollama returned HTTP {error.code}.") from error
    except (URLError, OSError) as error:
        raise RuntimeError("Could not reach Ollama. Check that the app or ollama serve is running.") from error
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        raise RuntimeError("Ollama returned an unexpected response.") from error

    if not answer:
        raise RuntimeError("The model returned an empty reply. Try rephrasing your prompt.")
    history.extend([
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": answer},
    ])
    return answer


def main():
    parser = argparse.ArgumentParser(description="F.R.I.D.A.Y. local assistant")
    parser.add_argument("--model", default=MODEL, help="Ollama model tag")
    parser.add_argument("--speak", action="store_true", help="Read replies aloud on macOS")
    args = parser.parse_args()
    speaker = shutil.which("say") if args.speak else None
    if args.speak and not speaker:
        print("Speech unavailable. Continuing in text mode.")

    history = deque(maxlen=12)
    print(f"F.R.I.D.A.Y. | {args.model}")
    print("Standing by. Type /help for commands.")
    while True:
        try:
            prompt = input("\nYou > ").strip()
            if not prompt:
                continue
            if prompt == "/exit":
                break
            if prompt == "/reset":
                history.clear()
                print("Conversation cleared.")
            elif prompt == "/help":
                print(HELP)
            elif prompt == "/status":
                print(f"Model: {args.model} | Retained turns: {len(history) // 2} | Voice: {'on' if speaker else 'off'}")
            elif prompt == "/time":
                print(datetime.now().astimezone().strftime("%Y-%m-%d %I:%M %p %Z"))
            elif prompt.startswith("/"):
                print("Unknown command. Type /help for available commands.")
            else:
                answer = chat(args.model, history, prompt)
                print(f"F.R.I.D.A.Y. > {answer}")
                if speaker:
                    # Send speech text through stdin so it cannot be parsed as options.
                    subprocess.run([speaker, "-f", "-"], input=answer, text=True, check=False)
        except RuntimeError as error:
            print(f"F.R.I.D.A.Y. > {error}")
        except (EOFError, KeyboardInterrupt):
            break
    print("\nF.R.I.D.A.Y. > Signing off.")


if __name__ == "__main__":
    main()
