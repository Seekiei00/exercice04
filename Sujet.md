# Exercice 04 — Observatoire de fréquentation des médiathèques

## Contexte

Une collectivité souhaite publier les chiffres de fréquentation de ses médiathèques et réserver un **bilan analytique** aux personnels habilités. Votre mission est de réaliser une API FastAPI, une interface Streamlit et des tests automatisés.

Cet exercice reprend les notions de la **démo 04**, mais avec un contexte et des données métier différents. Vous devez réaliser le projet vous-mêmes : **aucune arborescence ni fichier Python à trous n'est fourni**.

## Technologies

FastAPI, SQLAlchemy, PostgreSQL, bcrypt, JWT, Streamlit, `requests`, pytest et `TestClient`, Playwright avec Chromium. Configurer les secrets et la connexion BDD par `.env` et fournir `.env.example` / `.gitignore`.

## Données et utilisateurs

Créer deux tables, au minimum :

| Entité | Champs |
|---|---|
| `users` | `id`, `username` unique, `password_hash`, `role` (`reader` ou `analyst`) |
| `frequentations` | `id`, `mediatheque`, `mois` (format AAAA-MM), `visiteurs` (entier positif ou nul) |

Fournir une initialisation avec **24 observations**, un compte `reader` et un compte `analyst`. Les mots de passe sont stockés **hachés**. Le jeu de données peut être fictif mais doit être cohérent et stable pour les tests.

## API à réaliser

| Méthode et endpoint | Accès | Attendu |
|---|---|---|
| `POST /auth/login` | Public | Vérifie les identifiants et retourne un JWT (`sub`, `role`, `iat`, `exp`) |
| `GET /frequentations` | Public | Retourne une page d'observations |
| `GET /analytics/bilan` | `analyst` | Retourne un bilan global de fréquentation |

**Pagination** : `GET /frequentations?page=1&page_size=5`, avec `page >= 1` et `1 <= page_size <= 50`. La réponse doit contenir `items`, `page`, `page_size`, `total` et `pages`. Un ordre stable des résultats est obligatoire. Une page au-delà des résultats retourne `items: []`, sans erreur.

**Bilan privé** : la réponse contiendra au minimum `nb_observations`, `total_visiteurs` et `moyenne_visiteurs` (moyenne par observation). Ces valeurs doivent être calculées sur les observations en base et non écrites en dur.

**Sécurité** : `401` en cas de token absent, invalide ou expiré ; `403` lorsqu'un utilisateur `reader` appelle le bilan. Le JWT n'est pas chiffré et les contrôles d'accès doivent être effectués par l'API, pas uniquement dans Streamlit.

## Front Streamlit

Réaliser un front **organisé en plusieurs modules**, avec une séparation claire entre interface, communication HTTP et gestion de session.

Il doit proposer :

1. une page de connexion (`reader` ou `analyst`) ;
2. une page publique affichant la fréquentation **paginée**, utilisable sans connexion, avec les boutons **Précédent** et **Suivant** ;
3. une page privée affichant le bilan renvoyé par l'API après connexion ;
4. une déconnexion et une gestion compréhensible des réponses `401` et `403`.

Le token doit être conservé dans `st.session_state`. Les appels API doivent être centralisés et ajouter automatiquement `Authorization: Bearer <token>` lorsque le token existe. **Ne conservez pas le mot de passe en session.**

## Tests à réaliser

**Tests API publics (`pytest` + `TestClient`)** : vérifier la consultation sans token, la première/deuxième page, le total et une pagination invalide (`422`).

**Tests d'intégration API sécurisée** : un vrai login permet de récupérer le JWT dans une fixture ; vérifier accès autorisé (`200`), sans token (`401`), token invalide (`401`) et rôle `reader` (`403`).

**Test E2E (`pytest` + Playwright/Chromium)** : lancer FastAPI et Streamlit, ouvrir Streamlit dans un vrai navigateur, se connecter comme `analyst`, accéder à la page privée et vérifier qu'une valeur du bilan obtenue via FastAPI est visible. Le test E2E doit traverser navigateur → Streamlit → FastAPI → PostgreSQL.

## Livraison

Fournir un projet complet avec `README.md` contenant les **commandes Windows PowerShell** (utiliser `python -m` pour lancer les outils), l'initialisation PostgreSQL, les comptes pédagogiques, les commandes pour les tests API et E2E et un court scénario de vérification. Les fichiers de tests doivent être commentés succinctement pour expliquer ce qu'ils vérifient.

### Critères de réussite

- API publique consultable anonymement, pagination correcte et vérifiable.
- Authentification réelle en base avec bcrypt + JWT et refus `401`/`403` appropriés.
- Front Streamlit organisé, login, pages publique et privée, déconnexion.
- Tests API et E2E exécutables avec le README.
 