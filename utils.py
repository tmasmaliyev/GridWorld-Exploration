from api import APIClient
from src.action import Action

from typing import (
    Dict, 
    Tuple, 
    List, 
    Callable, 
    Union,
    Optional, 
    Any
)
import os
import time
import cloudpickle
import logging

def freeze(seconds : Union[int, float] = 0.1):
    def func(f : Callable[..., Any]):
        def wrapper(*args, **kwargs):
            res = f(*args, **kwargs)

            time.sleep(seconds)

            return res
        
        return wrapper
    
    return func

@freeze()
def get_run_info(client : APIClient, run_id : Optional[int] = None) -> List[Dict]:
    run_info = client.get(
        endpoint = "/",
        params = {
            "type" : "runs",
            "teamId" : os.getenv("TEAM_ID"),
            "count" : 100
        }
    )['runs']

    if run_id is None:
        return run_info

    return [run for run in run_info if int(run['runId']) == run_id]

@freeze()
def reset_active_world(client : APIClient) -> None:
    reset_info = client.get(
        endpoint = "/",
        params = {
            "teamId" : os.getenv("TEAM_ID"),
            "otp" : 5712768807
        }
    )

    if reset_info["code"] != "OK":
        logging.error(f"Reset active world request returned {reset_info['code']}\n"
                      f"Output : {reset_info}")
        raise

@freeze()
def create_world(client : APIClient, world_id : int) -> Dict:
    world_info = client.post(
        endpoint = "/",
        data = {
            "type" : "enter",
            "worldId" : world_id,
            "teamId" : os.getenv("TEAM_ID"),
        }
    )

    if world_info["code"] != "OK":
        logging.error(f"Create new world request returned {world_info['code']}\n"
                      f"Output : {world_info}")
        raise

    return world_info

@freeze()
def get_location(client : APIClient, world_id : int) -> Tuple[int, int]:
    state_info = client.get(
        endpoint = "/",
        params = {
            "type" : "location",
            "teamId" : os.getenv("TEAM_ID")
        }
    )

    if state_info["code"] != "OK":
        logging.error(f"Get location request returned {state_info['code']}\n"
                      f"Output : {state_info}")
        raise

    if int(state_info["world"]) != world_id:
        logging.error(f"Picked world location mismatches given world id !\n"
                      f"Given world_id : {world_id}, output world_id : {state_info['world']} !")
        raise

    state = tuple(
        map(int, state_info["state"].split(":"))
    )

    return state

@freeze()
def make_move(client : APIClient, action : Action, world_id : int) -> Optional[Dict]:
    move_info = client.post(
        endpoint = "/",
        data = {
            "type" : "move",
            "worldId" : world_id,
            "teamId" : os.getenv("TEAM_ID"),
            "move" : action.name
        }
    )

    if move_info["code"] != "OK":
        logging.error(f"Make move request returned {move_info['code']}\n"
                      f"Output : {move_info}")
        raise
    

    return move_info


def save_q_table(filepath : str, q_table : Dict) -> None:
    with open(filepath, 'wb') as f:
        cloudpickle.dump(q_table, f)

    logging.info(f'Saved q_table successfully !')

def load_q_table(filepath : str) -> Dict:
    with open(filepath, 'rb') as f:
        logging.info(f'Loaded q_table successfully !')

        return cloudpickle.load(f)
