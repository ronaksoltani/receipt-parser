import argparse
import json
from pathlib import Path

from .parser import image_to_text, parse_receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract structured fields from a receipt.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", type=Path)
    source.add_argument("--image", type=Path)
    parser.add_argument("--json", type=Path, default=Path("receipt.json"))
    args = parser.parse_args(argv)
    try:
        text = args.text.read_text(encoding="utf-8") if args.text else image_to_text(args.image)
        result = parse_receipt(text, "text" if args.text else "ocr")
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result.model_dump(mode="json"), indent=2), encoding="utf-8")
    except (OSError, RuntimeError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(result.model_dump(mode="json"), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
