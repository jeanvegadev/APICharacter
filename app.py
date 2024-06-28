from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models
import schemas

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = Flask(__name__)


# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.route("/characters", methods=["GET"])
def read_characters():
    db: Session = next(get_db())
    characters = db.query(models.Character).all()
    return jsonify([schemas.Character.from_orm(character).dict() for character in characters])


@app.route("/characters/<int:character_id>", methods=["GET"])
def read_character(character_id: int):
    db: Session = next(get_db())
    character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if character is None:
        return jsonify({"error": "Character not found"}), 404
    return jsonify(schemas.Character.from_orm(character).dict())


@app.route("/characters", methods=["POST"])
def create_character():
    db: Session = next(get_db())
    character_data = request.get_json()
    character_schema = schemas.CharacterCreate(**character_data)
    db_character = models.Character(**character_schema.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return jsonify(schemas.Character.from_orm(db_character).dict()), 201


@app.route("/characters/<int:character_id>", methods=["DELETE"])
def delete_character(character_id: int):
    db: Session = next(get_db())
    character = db.query(models.Character).filter(models.Character.id == character_id).first()
    if character is None:
        return jsonify({"error": "Character not found"}), 404
    db.delete(character)
    db.commit()
    return '', 204


if __name__ == '__main__':
    app.run(debug=True)
