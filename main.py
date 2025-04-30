from api import APIClient
from src.agent import Agent
from utils import (
    get_location, 
    get_run_info,
    make_move,
    create_world,
    reset_active_world,
    save_q_table,
    load_q_table
)

from dotenv import load_dotenv
import logging, os

EPISODES : int = 75
STEPS : int = 500

def main():
    world_id = 2
    
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

    api_reset = APIClient(
        base_url = os.getenv("RESET_URL"),
        headers = headers
    )

    #endregion

    # region Agent Initializer
    agent = Agent(
        # epsilon = 0
    )
    # agent.q_table = load_q_table(f'./q_table_{world_id}.pkl')
    # endregion

    # region Game Loop
    for episode in range(1, EPISODES + 1):
        logging.info(f'Episode : {episode}')

        # region Initialize Game & Get run_id
        # score = 0
        running_score = 0
        # game_ended = False

        # Reset previous world
        reset_active_world(
            client = api_reset
        )

        # Create new world based on given world_id & get corresponding "runId"
        world_info = create_world(
            client = api_gw,
            world_id = world_id
        )
        run_id = world_info['runId']

        # Get initial state
        state = get_location(
            client = api_gw,
            world_id = world_id
        )

        # endregion

        for step in range(1, STEPS + 1):
            logging.info(f'Step : {step}')

            run_info = get_run_info(
                client = api_scr,
                run_id = run_id
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
                with open(f'./output_{world_id}.txt', 'a') as f:
                    if move_info['reward'] < 0:
                        logging.info(f'You got into trap ! The trap is in x -> {state[0]}, y -> {state[1]}')
                        f.write(f'You got into trap ! The trap is in x -> {state[0]}, y -> {state[1]}\n')

                        agent.q_table[(state, action)] = -10000
                    else:
                        logging.info(f'You won ! The reward is in x -> {state[0]}, y -> {state[1]}')
                        f.write(f'You won ! The reward is in x -> {state[0]}, y -> {state[1]}\n')

                        agent.q_table[(state, action)] = 10000

                # game_ended = True
                break

            # new_score = float(move_info['reward']) # For World 1
            new_score = float(move_info['scoreIncrement'])
            new_running_score = running_score + new_score
            # new_score = round(new_score, 3)

            # if new_score == 0:
            #     new_running_score = running_score + agent.move_penalty
            # else:
            #     new_running_score = running_score + new_score
            
            logging.info(f'Move info {move_info}')

            new_state = get_location(
                client = api_gw,
                world_id = world_id
            )

            new_run_info = get_run_info(
                client = api_scr,
                run_id = run_id
            )

            logging.info(f'Changed run info : {new_run_info}')
            logging.info(f'Changed Location : x -> {new_state[0]}, y -> {new_state[1]}')

            # For World 1
            # logging.info(f'Old score : {score}')
            # logging.info(f'New score : {new_score}')

            # For world 2
            logging.info(f'Old running score : {running_score}')
            logging.info(f'New running score : {new_running_score}')

            # reward = new_score - score # For World 1
            reward = new_running_score
            agent.update(state, action, reward, new_state)

            state = new_state
            running_score = new_running_score
            # score = new_score

            save_q_table(f'./q_table_{world_id}.pkl', agent.q_table)

        # if game_ended:
        #     break

        agent.anneal_epsilon(episode)
        agent.anneal_penalty(episode)
        
        agent.reset_visited_state()

    # endregion


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    load_dotenv()

    main()