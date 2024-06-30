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
    """
    Load the paths of YAML files for Swagger documentation.

    Parameters:
    None

    Returns:
    dict: A dictionary containing the paths of YAML files for each API
    endpoint.

    The paths are constructed using the current working directory
    and the 'swagger' folder. The dictionary keys represent the API
    endpoints (e.g., 'get_all', 'get', 'create', 'delete')
    and the values are the corresponding paths to the YAML files.
    """
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
        """
        Initialize the CharacterAPI class with the provided Flask app instance.

        Parameters:
        app (Flask): The Flask app instance to which the API routes
        will be added.

        Returns:
        None
        """
        self.app = app
        self.setup_routes()
        self.setup_swagger()

    def setup_routes(self):
        """
        Set up the routes for the character API.

        This method adds four URL rules to the Flask app instance.
        Each rule corresponds
        to a specific API endpoint for managing characters.
        The view functions associated
        with these endpoints are defined in the CharacterAPI class.

        Parameters:
        None

        Returns:
        None
        """
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
        """
        Set up Swagger documentation for the character API.

        This method configures the Flask app to use Swagger
        for API documentation.
        It sets the specifications route, enables Swagger UI,
        and provides basic information about the API.

        Parameters:
        None

        Returns:
        None

        Raises:
        None
        """
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

        Parameters:
        None

        Returns:
        JSON: A JSON response containing an array of character objects.
        Each character object has the following properties:
        id, name, height, mass, birth_year, and eye_color.

        Raises:
        None
        """
        db: Session = next(self.get_db())
        characters = db.query(
            models.Character.id,
            models.Character.name,
            models.Character.height,
            models.Character.mass,
            models.Character.birth_year,
            models.Character.eye_color).all()
        return jsonify([schemas.GetAll.model_validate(
                    character).model_dump() for character in characters])

    @swag_from(path_swagger['get'])
    def read_character(self, character_id: int):
        """
        Retrieve a character from the database based on the given character ID.

        Parameters:
        character_id (int): The unique identifier of the character to retrieve.

        Returns:
        JSON: A JSON response containing the details of the character if found.
        If the character is not found, a JSON response with an error message
        is returned.

        Raises:
        None
        """
        db: Session = next(self.get_db())
        character = db.query(models.Character).filter(
            models.Character.id == character_id).first()
        if character is None:
            return jsonify({"error": "Character not found"}), 400
        return jsonify(schemas.Character.model_validate(
                        character).model_dump())

    @swag_from(path_swagger['create'])
    def create_character(self):
        """
        Create a new character in the database.

        Parameters:
        None

        Returns:
        JSON: A JSON response containing the created character's details
        if successful.
        If the character already exists, returns a JSON response
        with an error message.
        If there are validation errors, returns a JSON response
        with the errors.

        Raises:
        None
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

        Parameters:
        character_id (int): The unique identifier of the character to delete.

        Returns:
        JSON: A JSON response indicating the success of the operation.
        If the character is not found, returns a JSON response
        with an error message.

        Raises:
        None
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
        """
        Context manager for handling database sessions.

        This function uses Python's context management protocol
        (the 'with' statement)
        to ensure that the database session is properly closed
        after it is no longer needed.
        This is important to prevent database connection leaks
        and to maintain good database performance.

        Parameters:
        None

        Returns:
        Session: A database session object that can be used
        to interact with the database.

        Raises:
        None
        """
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


app = Flask(__name__)
character_api = CharacterAPI(app)

if __name__ == '__main__':
    app.run(debug=True)
