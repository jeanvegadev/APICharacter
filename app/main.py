"""Main."""
from flask import Flask, request, jsonify
from sqlalchemy.orm import Session
from pydantic import ValidationError
from .database import engine, SessionLocal, Base
from . import models
from . import schemas
from flasgger import Swagger, swag_from
import os

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)


# Función para cargar rutas de archivos YAML de Swagger
def load_swagger_paths():
    swagger_folder = os.path.join(os.getcwd(), 'swagger')
    paths = {
        'get_all': os.path.join(swagger_folder, 'get_all_characters.yml'),
        'get': os.path.join(swagger_folder, 'get_character.yml'),
        'create': os.path.join(swagger_folder, 'create_character.yml'),
        'delete': os.path.join(swagger_folder, 'delete_character.yml')
    }
    return paths


path_swagger = load_swagger_paths()


# Clase para definir la API de personajes
class CharacterAPI:
    def __init__(self, app):
        self.app = app
        self.setup_routes()
        self.setup_swagger()


    def setup_routes(self):
        self.app.add_url_rule('/character/getAll',
                              view_func=self.read_characters,
                              methods=['GET'])
        self.app.add_url_rule('/character/get/<int:character_id>',
                              view_func=self.read_character,
                              methods=['GET'])
        self.app.add_url_rule('/character/add',
                              view_func=self.create_character,
                              methods=['POST'])
        self.app.add_url_rule('/character/delete/<int:character_id>',
                              view_func=self.delete_character,
                              methods=['DELETE'])

    def setup_swagger(self):
        app.config['SWAGGER'] = {
            'specs_route': '/'
        }
        swagger_config = {
            "swagger_ui": True,
            "swagger": "2.0",
            "info": {
                "title": "Character API",
                "description": "API for managing characters",
                "version": "1.0.0"
            }
        }
        Swagger(self.app, template=swagger_config)

    @swag_from(path_swagger['get_all'])
    def read_characters(self):
        """
        Retrieve all characters from the database.
        """
        db: Session = next(self.get_db())
        characters = db.query(
            models.Character.id,
            models.Character.name,
            models.Character.height,
            models.Character.mass,
            models.Character.birth_year,
            models.Character.eye_color).all()
        return jsonify([schemas.GetAll.model_validate(character).model_dump() for character in characters])

    @swag_from(path_swagger['get'])
    def read_character(self, character_id: int):
        """
        Retrieve a specific character from the database based on the given character ID.
        """
        db: Session = next(self.get_db())
        character = db.query(models.Character).filter(
            models.Character.id == character_id).first()
        if character is None:
            return jsonify({"error": "Character not found"}), 400
        return jsonify(schemas.Character.model_validate(character).model_dump())

    @swag_from(path_swagger['create'])
    def create_character(self):
        """
        Create a new character in the database.
        """
        db: Session = next(self.get_db())
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
            return jsonify(schemas.Character.model_validate(
                            db_character).model_dump()), 201
        except ValidationError as e:
            # Handle Pydantic validation errors
            errors = [{"field": error['loc'][0],
                       "message": error['msg']} for error in e.errors()]
            return jsonify({"errors": errors}), 400
        finally:
            db.close()

    @swag_from(path_swagger['delete'])
    def delete_character(self, character_id: int):
        """
        Delete a character from the database based on the given character ID.
        """
        db: Session = next(self.get_db())
        character = db.query(models.Character).filter(
            models.Character.id == character_id).first()
        if character is None:
            return jsonify({"error": "Character not found"}), 400
        db.delete(character)
        db.commit()
        return jsonify(
            {"info": f"Character with id '{character_id}' was deleted"}), 200

    # Dependencia para obtener la sesion de la base de datos
    def get_db(self):
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


app = Flask(__name__)
character_api = CharacterAPI(app)

if __name__ == '__main__':
    app.run(debug=True)
