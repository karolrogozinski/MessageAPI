import pytest
import sqlite3
from fastapi.testclient import TestClient
from main import app
from login import encrypt


client = TestClient(app)
app.db_connection = sqlite3.connect("messages.db", check_same_thread=False)


def test_messages():
    response = client.get("/messages")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "owner": "message.api.example@gmail.com",
            "title": "Example message 1"
        },
        {
            "id": 2,
            "owner": "message.api.example@gmail.com",
            "title": "Example message 2"
        },
        {
            "id": 3,
            "owner": "message.api.example@gmail.com",
            "title": "Example message 3"
        }
    ]

def test_get_message():
    response = client.get("/messages/1")
    assert response.status_code == 200
    assert response.json() == {
        "owner": "message.api.example@gmail.com",
        "title:": "Example message 1",
        "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque vel condimentum turpis, eu pulvinar enim. Nam vel duis.",
        "counter": 1
    }

def test_get_message_not_found():
    response = client.get("/messages/9")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}

def test_create_message_unauthorized():
    email = "example@gmail.com"
    token = encrypt(email)
    response = client.post("/messages/new",
                            cookies={"session_token":token},
                            json={"owner": "example@gmail.com", "title": "test message", "text": ""})
    assert response.status_code == 403
    assert response.json() == {"detail": "Unauthorized"}

def test_create_message_no_text():
    email = "example@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.post("/messages/new",
                            cookies={"session_token":token},
                            json={"owner": "example@gmail.com", "title": "test message", "text": ""})
    app.session_tokens.remove(token)
    assert response.status_code == 402
    assert response.json() == {"detail": "All parameters have to be specified"}

def test_create_message_too_long_text():
    email = "example@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.post("/messages/new",
                            cookies={"session_token":token},
                            json={"owner": "example@gmail.com", "title": "test message", "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi id odio vitae libero fermentum scelerisque. Mauris scelerisque laoreet purus. Morbi sit amet velit eget elit viverra."})
    app.session_tokens.remove(token)
    assert response.status_code == 402
    assert response.json() == {"detail": "Your message is too long"}

def test_create_message_too_long_text():
    email = "example@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.post("/messages/new",
                            cookies={"session_token":token},
                            json={"owner": "another@gmail.com", "title": "test message", "text": "text"})
    app.session_tokens.remove(token)
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have access to create message as this user"}

def test_create_message():
    email = "example@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.post("/messages/new",
                            cookies={"session_token":token},
                            json={"owner": "example@gmail.com", "title": "test message", "text": "text"})
    app.session_tokens.remove(token)
    assert response.status_code == 201
    assert response.json() == {"created": "test message"}

def test_edit_message():
    email = "example@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.post("/messages/edit",
                            cookies={"session_token":token},
                            json={"message_id": 4, "text": "new text"})
    app.session_tokens.remove(token)
    assert response.status_code == 201
    assert response.json() == {"edited": "test message"}

    response = client.get("/messages/4")
    assert response.status_code == 200
    assert response.json() == {
        "owner": "example@gmail.com",
        "title:": "test message",
        "text": "new text",
        "counter": 1
    }

def test_edit_message_unauthorized():
    email = "example@gmail.com"
    token = encrypt(email)
    response = client.post("/messages/edit",
                            cookies={"session_token":token},
                            json={"message_id": 4, "text": "new text"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Unauthorized"}

def test_edit_message_not_found():
    email = "example@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.post("/messages/edit",
                            cookies={"session_token":token},
                            json={"message_id": 9, "text": "new text"})
    app.session_tokens.remove(token)
    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}

def test_edit_message_not_owner():
    email = "anothere@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.post("/messages/edit",
                            cookies={"session_token":token},
                            json={"message_id": 4, "text": "new text"})
    app.session_tokens.remove(token)
    assert response.status_code == 403
    assert response.json() == {"detail": "You do not have access to edit this message"}

def test_edit_message_too_long():
    email = "example@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.post("/messages/edit",
                            cookies={"session_token":token},
                            json={"message_id": 4, "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi id odio vitae libero fermentum scelerisque. Mauris scelerisque laoreet purus. Morbi sit amet velit eget elit viverra."})
    app.session_tokens.remove(token)
    assert response.status_code == 402
    assert response.json() == {"detail": "Incorrect message text"}

def test_edit_message_no_text():
    email = "example@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.post("/messages/edit",
                            cookies={"session_token":token},
                            json={"message_id": 4, "text": ""})
    app.session_tokens.remove(token)
    assert response.status_code == 402
    assert response.json() == {"detail": "Incorrect message text"}

def test_delete_message_unauthorized():
    email = "example@gmail.com"
    token = encrypt(email)
    response = client.delete("/messages/4/delete", cookies={"session_token":token})
    assert response.status_code == 403
    assert response.json() == {"detail": "Unauthorized"}

def test_delete_message_not_found():
    email = "example@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.delete("/messages/9/delete", cookies={"session_token":token})
    app.session_tokens.remove(token)
    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}

def test_delete_message_not_owner():
    email = "another@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.delete("/messages/4/delete", cookies={"session_token":token})
    app.session_tokens.remove(token)
    assert response.status_code == 403
    assert response.json() == {"detail": "You are not the owner"}

def test_delete_message():
    email = "example@gmail.com"
    token = encrypt(email)
    app.session_tokens.append(token)
    response = client.delete("/messages/4/delete", cookies={"session_token":token})
    app.session_tokens.remove(token)
    assert response.status_code == 200
    assert response.json() == {"deleted": "test message"}
    app.db_connection.close()