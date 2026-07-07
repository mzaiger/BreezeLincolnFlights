import json
import time
from datetime import date, timedelta
import serpapi

API_KEY = os.getenv("SERPAPI_KEY")

client = serpapi.Client(api_key=API_KEY)

start_date = date.today()
end_date = start_date + timedelta(days=183)

all_results = []

current = start_date

while current <= end_date:

    searches = []

    # Wednesday -> Saturday
    if current.weekday() == 2:  # Wednesday
        searches.append({
            "trip_type": "Wednesday-Saturday",
            "outbound_date": current.strftime("%Y-%m-%d"),
            "return_date": (current + timedelta(days=3)).strftime("%Y-%m-%d")
        })

    # Saturday -> Wednesday
    elif current.weekday() == 5:  # Saturday
        searches.append({
            "trip_type": "Saturday-Wednesday",
            "outbound_date": current.strftime("%Y-%m-%d"),
            "return_date": (current + timedelta(days=4)).strftime("%Y-%m-%d")
        })

    for search in searches:

        print(
            f"Searching {search['trip_type']} "
            f"{search['outbound_date']} -> {search['return_date']}"
        )

        try:
            results = client.search({
                "engine": "google_flights",
                "hl": "en",
                "gl": "us",
                "departure_id": "LNK",
                "arrival_id": "LAS",
                "outbound_date": search["outbound_date"],
                "return_date": search["return_date"],
                "currency": "USD",
                "type": "1",
                "adults": "1",
                "stops": "1"
            })

            # Convert SerpAPI result to plain dict
            try:
                results_data = results.as_dict()
            except AttributeError:
                try:
                    results_data = dict(results)
                except Exception:
                    results_data = json.loads(str(results))

            all_results.append({
                "trip_type": search["trip_type"],
                "outbound_date": search["outbound_date"],
                "return_date": search["return_date"],
                "results": results_data
            })

            print("  Success")

            # Be nice to the API
            time.sleep(2)

        except Exception as e:
            print(f"  Error: {e}")

    current += timedelta(days=1)

with open("lnk_las_6months.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print()
print(f"Saved {len(all_results)} searches to lnk_las_6months.json")