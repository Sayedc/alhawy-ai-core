import httpx

from app.tools.base import Tool


class ForexTool(Tool):

    SYMBOLS = {
        "usd": "USD",
        "دولار": "USD",

        "eur": "EUR",
        "يورو": "EUR",

        "gbp": "GBP",
        "استرليني": "GBP",

        "egp": "EGP",
        "جنيه": "EGP",
        "مصري": "EGP",
    }

    def __init__(self):
        super().__init__(
            name="forex",
            description="عرض أسعار صرف العملات",
            category="Market",
            version="1.0",
            priority=15,
        )

    @classmethod
    def can_handle(cls, query: str) -> bool:
        text = query.lower()
        return any(key in text for key in cls.SYMBOLS)

    async def run(self, query: str, **kwargs) -> str:
        text = query.lower()

        found = []

        for key, value in self.SYMBOLS.items():
            if key in text and value not in found:
                found.append(value)

        if not found:
            return None

        if len(found) == 1:
            base = found[0]
            target = "EGP" if base != "EGP" else "USD"
        else:
            base = found[0]
            target = found[1]

        try:
            async with httpx.AsyncClient(timeout=20) as client:

                response = await client.get(
                    "https://api.frankfurter.app/latest",
                    params={
                        "from": base,
                        "to": target,
                    },
                )

                response.raise_for_status()

        except httpx.HTTPError:
            return None

        data = response.json()

        rates = data.get("rates", {})

        if target not in rates:
            return None

        rate = rates[target]

        return (
            f"💱 {base}/{target}\n\n"
            f"1 {base} = {rate:,.4f} {target}"
        )
