"""Test E2E : navigateur -> Streamlit -> FastAPI -> PostgreSQL.

Lance uvicorn et Streamlit sur des ports dédiés, puis pilote Chromium
avec Playwright pour se connecter en analyst et lire le bilan.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests
from playwright.sync_api import Page, expect

from backend.init_db import init_db

ROOT = Path(__file__).resolve().parent.parent
API_PORT = 8765
FRONT_PORT = 8766
API_URL = f"http://127.0.0.1:{API_PORT}"
FRONT_URL = f"http://127.0.0.1:{FRONT_PORT}"


def _wait_for(url: str, timeout: float = 30) -> None:
    """Attend qu'un serveur réponde en HTTP 200."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if requests.get(url, timeout=1).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"Serveur indisponible : {url}")


@pytest.fixture(scope="module")
def servers():
    """Démarre FastAPI puis Streamlit, et les arrête après le test."""

    init_db()
    # Streamlit doit appeler l'API lancée par ce test.
    env = {**os.environ, "API_URL": API_URL}

    api = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app",
         "--port", str(API_PORT)],
        cwd=ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    front = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py",
         "--server.port", str(FRONT_PORT),
         "--server.headless", "true",
         "--browser.gatherUsageStats", "false"],
        cwd=ROOT, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for(f"{API_URL}/")
        _wait_for(f"{FRONT_URL}/_stcore/health")
        yield
    finally:
        front.terminate()
        api.terminate()
        front.wait(timeout=10)
        api.wait(timeout=10)


def test_analyst_voit_le_bilan(servers, page: Page):
    # Valeur de référence obtenue directement auprès de FastAPI.
    token = requests.post(
        f"{API_URL}/auth/login",
        json={"username": "analyst01", "password": "Analyst2026!"},
        timeout=5,
    ).json()["access_token"]
    bilan = requests.get(
        f"{API_URL}/analytics/bilan",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    ).json()

    # Connexion via le formulaire Streamlit dans Chromium.
    page.goto(FRONT_URL)
    page.get_by_role("link", name="Connexion").click()
    page.get_by_label("Identifiant").fill("analyst01")
    page.get_by_label("Mot de passe").fill("Analyst2026!")
    page.get_by_role("button", name="Se connecter").click()
    expect(page.get_by_text("Connecté : analyst01")).to_be_visible(timeout=15_000)

    # La page privée affiche le total renvoyé par l'API.
    page.get_by_role("link", name="Bilan analytique").click()
    metric = page.get_by_test_id("stMetric").filter(has_text="Total visiteurs")
    expect(metric).to_contain_text(str(bilan["total_visiteurs"]), timeout=15_000)
