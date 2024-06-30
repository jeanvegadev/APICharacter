from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from pydantic import ValidationError
from database import engine, SessionLocal, Base
import models
import schemas
from flasgger import Swagger, swag_from

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = Flask(__name__)

# Swagger configuration
app.config['SWAGGER'] = {
    'specs_route': '/'
}
swagger_config = {
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "swagger": "2.0",
    "info": {
        "title": "Character API",
        "description": "API for managing characters",
        "version": "1.0.0"
    }
}
swagger = Swagger(app, template=swagger_config)


# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.route("/character/getAll", methods=["GET"])
@swag_from('swagger/get_all_characters.yml')
def read_characters():
    """
    Retrieve all characters from the database.

    Parameters:
    None

    Returns:
    JSON: A list of dictionaries, each representing a character with the following keys:
        - id: The unique identifier of the character.
        - name: The name of the character.
        - height: The height of the character.
        - mass: The mass of the character.
        - birth_year: The birth year of the character.
        - eye_color: The eye color of the character.

    Raises:
    None
    """
    db: Session = next(get_db())
    characters = db.query(
                        models.Character.id,
                        models.Character.name,
                        models.Character.height,
                        models.Character.mass,
                        models.Character.birth_year,
                        models.Character.eye_color).all()
    return jsonify(
        [schemas.GetAll.model_validate(
            character).model_dump() for character in characters])


@app.route("/character/get/<int:character_id>", methods=["GET"])
@swag_from('swagger/get_character.yml')
def read_character(character_id: int):
    """
    Retrieve a specific character from the database based on the given character ID.

    Parameters:
    character_id (int): The unique identifier of the character to retrieve.

    Returns:
    JSON: A dictionary representing the character with the following keys:
        - id: The unique identifier of the character.
        - name: The name of the character.
        - height: The height of the character.
        - mass: The mass of the character.
        - hair_color: The hair color of the character.
        - skin_color: The skin color of the character.
        - birth_year: The birth year of the character.
        - eye_color: The eye color of the character.

    Raises:
    HTTP 400: If the character with the given ID is not found in the database.
    """
    db: Session = next(get_db())
    character = db.query(models.Character).filter(
                    models.Character.id == character_id).first()
    if character is None:
        return jsonify({"error": "Character not found"}), 400
    return jsonify(schemas.Character.model_validate(character).model_dump())


@app.route("/character/add", methods=["POST"])
@swag_from('swagger/create_character.yml')
def create_character():
    """
    Create a new character in the database.

    Parameters:
    - request: The incoming request object containing the character data in JSON format.

    Returns:
    - JSON: A dictionary representing the created character with the following keys:
        - id: The unique identifier of the character.
        - name: The name of the character.
        - height: The height of the character.
        - mass: The mass of the character.
        - hair_color: The hair color of the character.
        - skin_color: The skin color of the character.
        - birth_year: The birth year of the character.
        - eye_color: The eye color of the character.
    - HTTP 201: If the character is successfully created.
    - HTTP 400: If the character with the given ID already exists or if the input data is invalid.

    Raises:
    - ValidationError: If the input data is invalid according to the Pydantic schema.
    """
    db: Session = next(get_db())
    character_data = request.get_json()
    try:
        character_schema = schemas.CharacterBase(**character_data)

        # Check if the character already exists
        existing_character = db.query(
            models.Character).filter_by(id=character_schema.id).first()
        if existing_character:
            return jsonify(
                {"error": "Character with this ID already exists"}), 400

        db_character = models.Character(**character_schema.model_dump())
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        return jsonify(
            schemas.Character.model_validate(db_character).model_dump()), 201
    except ValidationError as e:
        # Handle Pydantic validation errors
        errors = []
        for error in e.errors():
            errors.append({
                "field": error['loc'][0],
                "message": error['msg']
            })
        return jsonify({"errors": errors}), 400

    finally:
        db.close()


@app.route("/character/delete/<int:character_id>", methods=["DELETE"])
@swag_from('swagger/delete_character.yml')
def delete_character(character_id: int):
    """
    Delete a character from the database based on the given character ID.

    Parameters:
    character_id (int): The unique identifier of the character to delete.

    Returns:
    JSON: A dictionary containing an information message.
        - info: A message indicating the successful deletion of the character.

    Raises:
    HTTP 400: If the character with the given ID is not found in the database.

    """
    db: Session = next(get_db())
    character = db.query(models.Character).filter(
                    models.Character.id == character_id).first()
    if character is None:
        return jsonify({"error": "Character not found"}), 400
    db.delete(character)
    db.commit()
    return jsonify(
        {"info": f"Character with id '{character_id}' was deleted"}), 200


if __name__ == '__main__':
    app.run(debug=True)