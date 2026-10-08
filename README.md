# Exercice 04 / Observatoire de fréquentation des médiathèques

API FastAPI (PostgreSQL, bcrypt, JWT), front Streamlit et tests automatisés (pytest, TestClient, Playwright).

## Arborescence

```
backend/            API FastAPI
  config.py         lecture du .env
  database.py       engine et session SQLAlchemy
  models.py         tables users et frequentations
  schemas.py        schémas Pydantic
  security.py       bcrypt + JWT
  dependencies.py   utilisateur courant (401) et contrôle de rôle (403)
  init_db.py        création des tables, comptes et 24 observations
  routers/          auth, frequentations, analytics
frontend/           Streamlit
  app.py            navigation + déconnexion
  services/         api_client.py (HTTP + Bearer), session.py (st.session_state)
  views/            login.py, public.py, private.py
tests/              tests API publics, sécurisés et E2E
```

## Installation (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env   # puis adapter DATABASE_URL et JWT_SECRET
```

## Initialisation PostgreSQL

Autoriser VSCode les éxecutions de la commande psql :

```powershell
$env:Path += ";C:\Program Files\PostgreSQL\18\bin"
```

Créer la base (une seule fois) et la base de test :

```powershell
psql -U postgres -c "CREATE DATABASE exercice04;"
```
```powershell
psql -U postgres -c "CREATE DATABASE exercice04_test;"
```

Créer les tables, les comptes et les 24 observations :

```powershell
python -m backend.init_db
```

Le script est idempotent : il ne réinsère pas les données si elles existent déjà.

## Comptes pédagogiques

| Identifiant | Mot de passe   | Rôle      |
|-------------|----------------|-----------|
| analyst01   | Analyst2026!   | `analyst` |
| reader01    | Reader2026!    | `reader`  |

Les mots de passe sont stockés hachés avec bcrypt.

## Lancement

Dans deux terminaux (venv activé) :

```powershell
python -m uvicorn backend.main:app --reload
```

```powershell
python -m streamlit run frontend/app.py
```

- API et documentation : http://127.0.0.1:8000/docs
- Front : http://localhost:8501

## Endpoints

| Méthode et endpoint | Accès | Réponse |
|---|---|---|
| `POST /auth/login` | Public | JWT (`sub`, `role`, `iat`, `exp`) |
| `GET /frequentations?page=1&page_size=5` | Public | `items`, `page`, `page_size`, `total`, `pages` |
| `GET /analytics/bilan` | `analyst` | `nb_observations`, `total_visiteurs`, `moyenne_visiteurs`, `par_mediatheque` |

`page >= 1` et `1 <= page_size <= 50`, sinon `422`. Une page au-delà des résultats renvoie `items: []`.
Le bilan renvoie `401` sans token, avec un token invalide ou expiré, et `403` pour un `reader`.

## Tests

PostgreSQL doit être démarré. Les tests appellent eux-mêmes `init_db()`.

```powershell
# Tests API publics + sécurisés (TestClient)
python -m pytest tests/test_api_public.py tests/test_api_secure.py -v

# Test E2E (lance FastAPI sur 8765 et Streamlit sur 8766, puis Chromium)
python -m playwright install chromium
python -m pytest tests/test_e2e.py -v

# Pour voir le navigateur
python -m pytest tests/test_e2e.py -v --headed

# Tout
python -m pytest -v
```

## Scénario de vérification manuelle

1. Ouvrir le front sans se connecter : la page **Fréquentation** affiche 5 observations, « Page 1 / 5 — 24 observations ». **Suivant** et **Précédent** changent de page.
2. Ouvrir **Bilan analytique** sans être connecté : un message invite à se connecter.
3. Se connecter avec `reader01` puis ouvrir **Bilan analytique** : message « Accès refusé (403) ».
4. Cliquer **Se déconnecter**, puis se connecter avec `analyst01` : le bilan affiche 24 observations, 53 395 visiteurs et une moyenne de 2 224,79.
5. Dans `/docs`, appeler `GET /analytics/bilan` sans token : `401`.
