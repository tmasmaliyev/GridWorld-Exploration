from ..api import APIClient
from .action import Action

from typing import Dict, Tuple
import logging

def get_run_info(client : APIClient) -> Dict:
    run_info = client.get(
        endpoint = "/",
        params = {
            "type" : "runs",
            "teamId" : 1444,
            "count" : 10
        }
    )

    return run_info

def get_location(client : APIClient, world_id : int) -> Tuple[int, int]:
    state_info = client.get(
        endpoint = "/",
        params = {
            "type" : "location",
            "teamId" : 1444
        }
    )

    if state_info["code"] != "OK":
        logging.error(f"Get location request returned {state_info["code"]}\n"
                      f"Output : {state_info}")
        raise

    if int(state_info["world"]) != world_id:
        logging.error(f"Picked world location mismatches given world id !\n"
                      f"Given world_id : {world_id}, output world_id : {state_info["world"]} !")
        raise

    state = list(
        map(int, state_info["state"].split(":"))
    )

    return state

def make_move(client : APIClient, action : Action, world_id : int) -> None:
    move_info = client.post(
        endpoint = "/",
        data = {
            "type" : "move",
            "worldId" : world_id,
            "teamId" : 1444,
            "move" : action.name
        }
    )

    if move_info["code"] != "OK":
        logging.error(f"Make move request returned {move_info["code"]}\n"
                      f"Output : {move_info}")
        raise

    logging.info(move_info)