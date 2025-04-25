from api import APIManager, APIClient
from src.agent import Agent
from src.utils import (
    get_location, 
    get_run_info,
    make_move
)

from dotenv import load_dotenv
import logging, os

EPISODES : int = 1000
STEPS : int = 100

def main():
    world_id = 1
    
    # region API Initializer
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

    # api_manager = APIManager()
    # api_manager.add_client("gw", client=api_gw)
    # api_manager.add_client("scr", client=api_scr)
    #endregion

    # region Agent Initializer
    agent = Agent()
    # endregion

    # region Game Loop
    for episode in range(1, EPISODES + 1):
        run_info = get_run_info(
            client = api_gw
        )

        state = get_location(
            client = api_gw,
            world_id = world_id
        )
        score = run_info["runs"][0]["score"]

        for step in range(1, STEPS + 1):
            action = agent.choose_action(state)
            make_move()

            new_state = get_location(
                client = api_gw,
                world_id = world_id
            )

            new_run_info = get_run_info(
                client = api_gw
            )
            new_score = new_run_info["runs"][0]["score"]

            reward = new_score - score
            agent.update(state, action, reward, new_state)

            state = new_state
            score = new_score
            

    # endregion


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    main()