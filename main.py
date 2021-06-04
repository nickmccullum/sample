import requests
import datetime
import secrets
import test_data
import json

BASE_URL = "https://delivery.chalk247.com/"


class APIResponseException(Exception):
    pass


class InvalidInputException(Exception):
    pass


def get_scoreboard(start_date, end_date):
    if type(start_date) != type(datetime.date(2021, 1, 1)) or type(start_date) != type(
        datetime.date(2021, 1, 1)
    ):
        raise InvalidInputException

    endpoint = f"scoreboard/NFL/{str(start_date)}/{str(end_date)}.json"

    response = requests.get(
        f"{BASE_URL}{endpoint}", params={"api_key": secrets.api_key}
    )

    if response.status_code != 200:
        raise APIResponseException("The scoreboard endpoint request failed")

    return response.json()


def get_team_rankings():
    endpoint = "team_rankings/NFL.json"

    response = requests.get(BASE_URL + endpoint, params={"api_key": secrets.api_key})

    if response.status_code != 200:
        raise APIResponseException("The team_rankings endpoint request failed")

    rankings = response.json().get("results").get("data")

    return rankings


def generate_combined_dataset(start_date, end_date):
    rankings = get_team_rankings()
    event_summaries = []

    events = get_scoreboard(start_date, end_date).get("results")

    for date, events in events.items():

        if not events:  # This skips the loop if there were no NFL events that day
            continue

        for event_id, event_data in events.get("data").items():
            home_team_id = event_data.get("home_team_id")
            away_team_id = event_data.get("away_team_id")

            for ranking_object in rankings:
                if ranking_object.get("team_id") == home_team_id:
                    home_team_ranking_object = ranking_object
                elif ranking_object.get("team_id") == away_team_id:
                    away_team_ranking_object = ranking_object

            event_summary = {
                "event_id": event_id,
                "event_date": event_data.get("event_date").split(" ")[0],
                "event_time": event_data.get("event_date").split(" ")[1],
                "away_team_id": away_team_id,
                "away_nick_name": event_data.get("away_nick_name"),
                "away_city": event_data.get("away_city"),
                "away_rank": away_team_ranking_object.get("rank"),
                "away_rank_points": round(
                    float(away_team_ranking_object.get("adjusted_points")), 2
                ),
                "home_team_id": home_team_id,
                "home_nick_name": event_data.get("home_nick_name"),
                "home_city": event_data.get("home_city"),
                "home_rank": home_team_ranking_object.get("rank"),
                "home_rank_points": round(
                    float(home_team_ranking_object.get("adjusted_points")), 2
                ),
            }

            event_summaries.append(event_summary)

    return event_summaries


rankings = get_team_rankings()
for ranking in rankings:
    print(rankings)

start_date = datetime.date(2020, 1, 12)
end_date = datetime.date(2020, 1, 19)

final_dataset = generate_combined_dataset(start_date, end_date)
print(final_dataset == test_data.test_data)
with open(f"exported_data.json", "w") as f:
    json.dump(final_dataset, f)
