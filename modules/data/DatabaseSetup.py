# modules/data/DatabaseSetup.py
from pymongo import MongoClient
from modules.logger import db_logger

class DatabaseSetup:
    def __init__(self):
        self.client = MongoClient(
            'mongodb://localhost:27017/'
        )
        self.db = self.client['home_assistant']

    def create_collections(self):
        user_schema = {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["name", "role"],
                    "properties": {
                        "name": {"bsonType": "string"},
                        "role": {"bsonType": "string"},
                        "age": {"bsonType": "int"},
                        "health_status": {"bsonType": "string"},
                        "health_records": {"bsonType": "array"}
                    }
                }
            }
        }

        inventory_schema = {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "properties": {
                        "categories": {"bsonType": "array"},
                        "items": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "required": ["name", "category"],
                                "properties": {
                                    "name": {"bsonType": "string"},
                                    "category": {"bsonType": "string"},
                                    # quantity için spesifik tip belirtmeyelim
                                    "info": {"bsonType": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }
        shopping_list_schema = {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "properties": {
                        "items": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"bsonType": "string"},
                                    "status": {"bsonType": "string"},
                                    "info": {"bsonType": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }

        tasks_schema = {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "properties": {
                        "tasks": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"bsonType": "string"},
                                    "assigned_to": {"bsonType": "string"},
                                    "due_date": {"bsonType": "date"},
                                    "info": {"bsonType": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }

        daily_log_schema = {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "properties": {
                        "logs": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "required": ["title", "date"],
                                "properties": {
                                    "title": {"bsonType": "string"},
                                    "date": {"bsonType": "date"},
                                    "details": {"bsonType": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }

        collections = {
            'users': user_schema,
            'inventory': inventory_schema,
            'tasks': tasks_schema,
            'daily_log': daily_log_schema,
            'shopping_list': shopping_list_schema 
        }

        for name, schema in collections.items():
            if name not in self.db.list_collection_names():
                try:
                    self.db.create_collection(name, **schema)
                except Exception as e:
                    print(f"Error creating collection {name}: {e}")
                    db_logger.error(f"Error creating collection {name}: {e}")
                print(f"Created collection: {name}")

    def create_indexes(self):
        # Users
        self.db.users.create_index("name")
        self.db.users.create_index("role")
        self.db.users.create_index("health_status")

        # Inventory
        self.db.inventory.create_index("items.name")
        self.db.inventory.create_index("items.category")
        self.db.inventory.create_index("categories")

        # Shopping List
        self.db.shopping_list.create_index("items.name")
        self.db.shopping_list.create_index("items.status")

        # Tasks
        self.db.tasks.create_index("tasks.name")
        self.db.tasks.create_index("tasks.assigned_to")
        self.db.tasks.create_index("tasks.due_date")

        # Daily Log
        self.db.daily_log.create_index("logs.title")
        self.db.daily_log.create_index("logs.date")
    


    def insert_initial_categories(self):
        initial_categories = [
            "food",
            "cleaning",
            "personal_care",
            "electronics",
            "tools",
            "medicine",
            "clothing",
            "other"
        ]

        self.db.inventory.update_one(
            {"categories": {"$exists": True}},
            {"$setOnInsert": {"categories": initial_categories, "items": []}},
            upsert=True
        )

    def setup(self):
        try:
            print("Starting database setup...")
            
            self.create_collections()
            print("Collections created with schemas")
            
            self.create_indexes()
            print("Indexes created")
            
            self.insert_initial_categories()
            print("Initial categories inserted")
            
            print("Database setup completed successfully")
            
        except Exception as e:
            print(f"Error during database setup: {e}")
            raise
        finally:
            self.client.close()

if __name__ == "__main__":
    setup = DatabaseSetup()
    setup.setup()