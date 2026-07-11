import httpx

from app.tools.base import Tool


class ForexTool(Tool):

    name = "forex"

    description = "Forex exchange rates"

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

    def can_handle(self, query: str) -> bool:

        text = query.lower()

        return any(k in text for k in self.SYMBOLS)

    async def run(self, query: str):

        text = query.lower()

        found = []

        for k, v in self.SYMBOLS.items():
            if k in text and v not in found:
                found.append(v)

        if len(found) == 1:
            base = found[0]
            target = "EGP" if base != "EGP" else "USD"
        else:
            base = found[0]
            target = found[1]

        async with httpx.AsyncClient(timeout=20) as client:

            r = await client.get(
                f"https://api.frankfurter.app/latest?from={base}&to={target}"
            )

        if r.status_code != 200:
            return None

        data = r.json()

        rate = data["rates"][target]

        return (
            f"💱 {base}/{target}\n\n"
            f"1 {base} = {rate} {target}"
      )
