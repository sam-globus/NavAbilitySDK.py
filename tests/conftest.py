import logging
import os
import time
from uuid import uuid4

import pytest

from navability.entities.Client import Client
from navability.entities.NavAbilityClient import (
    NavAbilityClient,
    NavAbilityHttpsClient,
    NavAbilityWebsocketClient,
)
from navability.entities.Variable.Variable import Variable
from navability.services.Status import getStatusLatest
from navability.services.Variable import addVariable

# setup basic logging to stderr
logging.basicConfig(level=logging.INFO)

_env_configs = {
    "local": {
        "navability_client": {
            "url_websocket": "wss://localhost:5000/graphql",
            "url_https": "https://localhost:5000",
        }
    },
    "dev": {
        "navability_client": {
            "url_websocket": "wss://api.d1.navability.io/graphql",
            "url_https": "https://api.d1.navability.io",
        }
    },
    "production": {},
}

SDK_ENV = os.environ.get("NAVABILITY_ENVIRONMENT", "dev")


@pytest.fixture(scope="session")
def env_config():
    return _env_configs[SDK_ENV]


@pytest.fixture(scope="module")
def navability_wss_client(env_config) -> NavAbilityClient:
    return NavAbilityWebsocketClient(
        url=env_config["navability_client"]["url_websocket"]
    )


@pytest.fixture(scope="module")
def navability_https_client(env_config) -> NavAbilityClient:
    return NavAbilityHttpsClient(url=env_config["navability_client"]["url_https"])


@pytest.fixture(scope="module")
def client(env_config) -> Client:
    return Client("Guest", "PySDKAutomation", str(uuid4())[0:8])


@pytest.fixture(scope="module")
def example_graph(navability_wss_client: NavAbilityClient, client: Client):
    v = Variable(label="x0", variableType="Pose2")
    res = addVariable(navability_wss_client, client, v)
    wait_time = 60
    while (
        getStatusLatest(navability_wss_client, res["addVariable"]).state != "Complete"
    ):
        time.sleep(1)
        wait_time -= 1
        if wait_time <= 0:
            raise Exception("Variable wasn't loaded in time")

    return (navability_wss_client, client, [v], [])
