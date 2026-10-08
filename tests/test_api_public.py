import pytest


def test_consultation_sans_token(client):
    # L'endpoint public répond 200 sans en-tête Authorization.
    response = client.get("/frequentations")
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "page", "page_size", "total", "pages"}


def test_premiere_page(client):
    # Page 1 : 5 éléments et métadonnées cohérentes.
    body = client.get("/frequentations", params={"page": 1, "page_size": 5}).json()
    assert body["page"] == 1
    assert body["page_size"] == 5
    assert len(body["items"]) == 5
    assert body["pages"] == 5  # 24 observations / 5 => 5 pages


def test_deuxieme_page_differente_de_la_premiere(client):
    # Ordre stable : aucune observation commune entre la page 1 et la page 2.
    page1 = client.get("/frequentations", params={"page": 1, "page_size": 5}).json()
    page2 = client.get("/frequentations", params={"page": 2, "page_size": 5}).json()
    ids1 = {item["id"] for item in page1["items"]}
    ids2 = {item["id"] for item in page2["items"]}
    assert len(page2["items"]) == 5
    assert ids1.isdisjoint(ids2)


def test_ordre_stable(client):
    # Deux appels identiques renvoient exactement la même page.
    params = {"page": 3, "page_size": 5}
    assert client.get("/frequentations", params=params).json() == \
        client.get("/frequentations", params=params).json()


def test_total(client):
    # Le jeu initial contient 24 observations.
    body = client.get("/frequentations", params={"page_size": 50}).json()
    assert body["total"] == 24
    assert len(body["items"]) == 24


def test_derniere_page_partielle(client):
    # 24 = 4 x 5 + 4 : la page 5 contient 4 éléments.
    body = client.get("/frequentations", params={"page": 5, "page_size": 5}).json()
    assert len(body["items"]) == 4


def test_page_au_dela_des_resultats(client):
    # Une page trop grande renvoie items: [] sans erreur.
    response = client.get("/frequentations", params={"page": 99, "page_size": 5})
    assert response.status_code == 200
    assert response.json()["items"] == []


@pytest.mark.parametrize(
    "params",
    [
        {"page": 0},
        {"page": -1},
        {"page_size": 0},
        {"page_size": 51},
        {"page": "abc"},
    ],
)
def test_pagination_invalide(client, params):
    # Paramètres hors bornes ou non entiers : 422.
    assert client.get("/frequentations", params=params).status_code == 422
