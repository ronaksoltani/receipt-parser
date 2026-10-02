from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

MONEY = re.compile(r"(?i)(?P<currency>USD|EUR|GBP|CAD|AUD|\$|€|£)\s*(?P<amount>\d[\d,]*(?:\.\d{2})?)|(?P<amount_after>\d[\d,]*(?:\.\d{2})?)\s*(?P<currency_after>USD|EUR|GBP|CAD|AUD)")
DATE_PATTERNS = (re.compile(r"\b(?P<year>20\d{2})-(?P<month>\d{1,2})-(?P<day>\d{1,2})\b"),
                 re.compile(r"\b(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{2,4})\b"))


class Receipt(BaseModel):
    merchant: str | None = None
    receipt_date: date | None = None
    currency: Literal["USD", "EUR", "GBP", "CAD", "AUD"] | None = None
    subtotal: Decimal | None = Field(default=None, ge=0)
    tax: Decimal | None = Field(default=None, ge=0)
    total: Decimal | None = Field(default=None, ge=0)
    source: Literal["text", "ocr"]
    warnings: list[str] = Field(default_factory=list)


def _parse_amount(value: str) -> Decimal | None:
    try:
        return Decimal(value.replace(",", ""))
    except InvalidOperation:
        return None


def parse_receipt(text: str, source: Literal["text", "ocr"] = "text") -> Receipt:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    merchant = lines[0][:120] if lines else None
    receipt_date = None
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            parts = {key: int(value) for key, value in match.groupdict().items()}
            if parts["year"] < 100:
                parts["year"] += 2000
            try:
                receipt_date = date(parts["year"], parts["month"], parts["day"])
            except ValueError:
                pass
            break
    amounts: list[tuple[str, Decimal]] = []
    currency_map = {"$": "USD", "€": "EUR", "£": "GBP"}
    currency = None
    for match in MONEY.finditer(text):
        raw_currency = (match.group("currency") or match.group("currency_after") or "").upper()
        currency = currency_map.get(raw_currency, raw_currency) or currency
        raw_amount = match.group("amount") or match.group("amount_after")
        amount = _parse_amount(raw_amount)
        if amount is not None:
            line = next((value for value in lines if match.group(0) in value), "").casefold()
            label = "total" if re.search(r"\b(total|amount due|balance due)\b", line) else \
                    "tax" if re.search(r"\b(tax|vat|gst)\b", line) else \
                    "subtotal" if "subtotal" in line or "sub total" in line else "other"
            amounts.append((label, amount))
    selected = {label: next((value for item_label, value in amounts if item_label == label), None)
                for label in ("subtotal", "tax", "total")}
    warnings = []
    if selected["total"] is None:
        warnings.append("total was not identified with confidence")
    if currency is None:
        warnings.append("currency was not identified")
    return Receipt(merchant=merchant, receipt_date=receipt_date, currency=currency,
                   subtotal=selected["subtotal"], tax=selected["tax"], total=selected["total"],
                   source=source, warnings=warnings)


def image_to_text(path: Path) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as error:
        raise RuntimeError("install the OCR extra with: pip install receipt-parser[ocr]") from error
    return pytesseract.image_to_string(Image.open(path))
