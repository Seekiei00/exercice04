"""Chargement de la configuration du backend."""

import os
from dotenv import load_dotenv

# Charge les variables du fichier .env.
load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]
JWT_SECRET = os.environ["JWT_SECRET"]
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "15"))
