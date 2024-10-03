import pytest

import models
import schemas


@pytest.mark.usefixtures("client", "db_session")
class TestCatsRoutes:

    def test_successfully_response_when_get_breeds(self, client):
        response = client.get("/api/breeds")

        assert len(response.json()["breeds"]) == 3
        assert response.status_code == 200

    def test_successfully_response_when_get_cats(self, client):
        response = client.get("/api/cats")

        assert len(response.json()) == 3
        assert response.status_code == 200

    def test_successfully_response_when_get_cats_by_filter(self, client):
        breed = "Британец"
        response = client.get("/api/cats?breed=" + breed)

        assert len(response.json()) == 1
        assert response.json()[0]["breed"] == breed
        assert response.status_code == 200

    def test_successfully_response_when_get_cat(self, client):
        cat_id = 1
        response = client.get("/api/cats/" + str(cat_id))

        assert len(response.json()) == 5
        assert response.json()["id"] == cat_id
        assert response.status_code == 200

    def test_wrong_response_when_get_cat_with_non_exist_id(self, client):
        cat_id = 4
        response = client.get("/api/cats/" + str(cat_id))

        assert response.status_code == 404

    async def test_successfully_response_when_post_cat(self, client, db_session):
        test_cat = {
                "color": "Черный-Белый",
                "age": 1,
                "description": "Черный-белый котенок",
                "breed": "Британец",
            }
        response = client.post(
            "/api/cats",
            json=test_cat,
        )
        async_db_session = db_session()
        await models.Cat.delete_cat(async_db_session, cat_id=response.json()["id"])
        assert len(response.json()) == 5
        assert response.status_code == 201

    def test_successfully_response_when_patch_cat(self, client):
        description = "Test description"
        response = client.patch(
            "/api/cats/1",
            json={
                "description": description,
            }
        )
        assert len(response.json()) == 5
        assert response.json()["description"] == description
        assert response.status_code == 200

    async def test_successfully_response_when_delete_cat(self, client, db_session):
        async_db_session = db_session()
        test_cat = {
            "color": "Черный-Белый",
            "age": 1,
            "description": "Черный-белый котенок",
            "breed": "Британец",
        }
        cat = await models.Cat.add_cat(async_db_session, schemas.CatForm(**test_cat))
        cats_before = await models.Cat.get_cats(async_db_session)

        response = client.delete(f"/api/cats/{cat.id}")

        cats_after = await models.Cat.get_cats(async_db_session)
        await async_db_session.aclose()
        assert len(cats_before) == len(cats_after) + 1
        assert response.status_code == 204

