from dataclasses import dataclass


@dataclass(frozen=True)
class Stock:
    symbol: str
    company_name: str
