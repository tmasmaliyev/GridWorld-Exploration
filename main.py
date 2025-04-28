from api import APIClient
from src.agent import Agent
from utils import (
    get_location, 
    get_run_info,
    make_move,
    save_q_table,
    load_q_table
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

    #endregion

    # region Agent Initializer
    agent = Agent()
    agent.q_table = load_q_table(f'./q_table_{world_id}.pkl')
    score = 0
    game_ended = False
    # endregion

    # region Game Loop
    for episode in range(1, EPISODES + 1):
        logging.info(f'Episode : {episode}')

        state = get_location(
            client = api_gw,
            world_id = world_id
        )

        # score = float(run_info["runs"][0]["score"])

        for step in range(1, STEPS + 1):
            logging.info(f'Step : {step}')

            run_info = get_run_info(
                client = api_scr,
                run_id = os.getenv('RUN_ID')
            )

            state = get_location(
                client = api_gw,
                world_id = world_id
            )

            action = agent.choose_action(state)

            logging.info(f'Current run info : {run_info}')
            logging.info(f'Location : x -> {state[0]}, y -> {state[1]}')
            logging.info(f'Taken action {action}')

            move_info = make_move(
                client = api_gw,
                action = action,
                world_id = world_id
            )

            if move_info['newState'] is None:
                game_ended = True
                break

            new_score = float(move_info['reward'])
            
            logging.info(f'Move info {move_info}')

            new_state = get_location(
                client = api_gw,
                world_id = world_id
            )

            new_run_info = get_run_info(
                client = api_scr,
                run_id = os.getenv('RUN_ID')
            )

            logging.info(f'Changed run info : {new_run_info}')
            logging.info(f'Changed Location : x -> {new_state[0]}, y -> {new_state[1]}')


            logging.info(f'Old score : {score}')
            logging.info(f'New score : {new_score}')

            reward = new_score - score
            agent.update(state, action, reward, new_state)

            state = new_state
            score = new_score
            
            save_q_table(f'./q_table_{world_id}.pkl', agent.q_table)

        if game_ended:
            logging.info(f'Game is completed !')
            break

    # endregion


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    main()