from api import APIManager, APIClient

from dotenv import load_dotenv
import logging, os

def main():
    headers = {
        "x-api-key" : os.getenv("API_KEY"),
        "userId" : os.getenv("USER_ID"),
        'User-Agent': 'PostmanRuntime/7.43.3'
    }

    api_gw = APIClient(
        base_url = os.getenv("GW_URL"),
        headers = headers
    )

    api_scr = APIClient(
        base_url = os.getenv("SCR_URL"),
        headers = headers
    )

    api_manager = APIManager()
    api_manager.add_client("gw", client=api_gw)
    api_manager.add_client("scr", client=api_scr)

    json = api_manager.get_client("scr").get(
        endpoint = "/",
        params = {
            "type" : "runs",
            "teamId" : 1444,
            "count" : 10
        }
    )

    logging.info(json)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    main()