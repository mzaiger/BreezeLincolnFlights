import os
import sys
import json
import time
import argparse
from datetime import date, timedelta
import serpapi

API_KEY = os.getenv("SERPAPI_KEY")

client = serpapi.Client(api_key=API_KEY)

DEPARTURE_ID = "LNK"
ARRIVAL_ID = "SNA"
STOPS = "2"  # kept same value as original script (Google's "stops" filter code)
OUTPUT_FILE = "lnk_sna_4months.json"
TEST_OUTPUT_FILE = "lnk_sna_test.json"


def to_plain_dict(results):
    """Convert a SerpApi results object to a plain JSON-serializable dict."""
    try:
        return results.as_dict()
    except AttributeError:
        try:
            return dict(results)
        except Exception:
            return json.loads(str(results))


def cheapest_option(results_data):
    """Return the cheapest flight option dict from best_flights/other_flights, or None."""
    options = (results_data.get("best_flights") or []) + (results_data.get("other_flights") or [])
    if not options:
        return None
    return min(options, key=lambda f: f.get("price", float("inf")))


def search_outbound(outbound_date, return_date):
    results = client.search({
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "departure_id": DEPARTURE_ID,
        "arrival_id": ARRIVAL_ID,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": "USD",
        "type": "1",
        "adults": "1",
        "stops": STOPS,
    })
    return to_plain_dict(results)


def search_return(outbound_date, return_date, departure_token):
    results = client.search({
        "engine": "google_flights",
        "hl": "en",
        "gl": "us",
        "departure_id": DEPARTURE_ID,
        "arrival_id": ARRIVAL_ID,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": "USD",
        "type": "1",
        "adults": "1",
        "stops": STOPS,
        "departure_token": departure_token,
    })
    return to_plain_dict(results)


def slim_flight(option):
    """Keep only what the front end needs from a flight option."""
    if option is None:
        return None
    return {
        "price": option.get("price"),
        "total_duration": option.get("total_duration"),
        "flights": option.get("flights", []),
        "layovers": option.get("layovers", []),
    }


def run(test_mode):
    start_date = date.today()
    end_date = start_date + timedelta(days=122)  # ~4 months

    all_results = []
    current = start_date
    found_test_result = False

    while current <= end_date and not (test_mode and found_test_result):

        searches = []

        if current.weekday() == 2:  # Wednesday
            searches.append({
                "trip_type": "Wednesday-Saturday",
                "outbound_date": current.strftime("%Y-%m-%d"),
                "return_date": (current + timedelta(days=3)).strftime("%Y-%m-%d"),
            })
        elif current.weekday() == 5:  # Saturday
            searches.append({
                "trip_type": "Saturday-Wednesday",
                "outbound_date": current.strftime("%Y-%m-%d"),
                "return_date": (current + timedelta(days=4)).strftime("%Y-%m-%d"),
            })

        for search in searches:
            print(f"Searching {search['trip_type']} {search['outbound_date']} -> {search['return_date']}")

            try:
                outbound_data = search_outbound(search["outbound_date"], search["return_date"])
                cheapest_out = cheapest_option(outbound_data)

                if cheapest_out is None or not cheapest_out.get("departure_token"):
                    print("  No outbound flights / no departure_token found, skipping.")
                    continue

                time.sleep(2)  # be nice to the API between the two calls

                return_data = search_return(
                    search["outbound_date"], search["return_date"], cheapest_out["departure_token"]
                )
                cheapest_ret = cheapest_option(return_data)

                if cheapest_ret is None:
                    print("  No return flights found for the selected outbound flight, skipping.")
                    continue

                all_results.append({
                    "trip_type": search["trip_type"],
                    "outbound_date": search["outbound_date"],
                    "return_date": search["return_date"],
                    "price": cheapest_ret.get("price"),
                    "outbound_flight": slim_flight(cheapest_out),
                    "return_flight": slim_flight(cheapest_ret),
                })

                print(f"  Success (total price: ${cheapest_ret.get('price')})")

                if test_mode:
                    found_test_result = True
                    break

                time.sleep(2)

            except Exception as e:
                print(f"  Error: {e}")

        current += timedelta(days=1)

    out_file = TEST_OUTPUT_FILE if test_mode else OUTPUT_FILE
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print()
    print(f"Saved {len(all_results)} searches to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search LNK -> SNA flight prices (4 months out).")
    parser.add_argument(
        "--test", action="store_true",
        help="Only run one date pair, write to a separate test file, and stop.",
    )
    args = parser.parse_args()
    run(test_mode=args.test)
