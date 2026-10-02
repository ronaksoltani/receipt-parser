# Receipt Parser

Extract merchant, date, currency, subtotal, tax, and total from receipt text or a receipt image. The text parser is deterministic; the optional image path uses Tesseract OCR installed on the host.

## Quick start

```bash
python -m venv .venv
python -m pip install -e .
receipt-parser --text receipt.txt --json receipt.json
receipt-parser --image receipt.jpg --json receipt.json
```

For image mode, install the Tesseract OCR application separately and make sure it is on `PATH`. The parser returns fields as nullable values when the receipt is ambiguous instead of inventing data. Date formats with slashes are interpreted as month/day/year.

## Privacy and limits

All parsing runs locally. Receipts may contain personal or financial information; review outputs before sharing them. OCR quality, local number formats, and unusual receipt layouts affect accuracy. This tool is not accounting or tax advice.

## Learning notes

Practice regular expressions, `Decimal` for money, typed Pydantic models, optional dependencies, and a clear separation between OCR text extraction and field parsing.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

## License

MIT. See [LICENSE](LICENSE).
