# modules/data/DatabaseManager.py
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
from modules.logger import db_logger

class DatabaseManager:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['home_assistant']



    def _ensure_array_exists(self, collection, array_name):
        """Ensures array field exists in collection"""
        try:
            self.db[collection].update_one(
                {},
                {'$setOnInsert': {array_name: []}},
                upsert=True
            )
        except Exception as e:
            db_logger.error(f"Error ensuring array {array_name}: {e}")




    def _parse_date(self, date_str, default_delta=1):
        """Converts string to datetime with fallback"""
        try:
            if isinstance(date_str, str):
                return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            return date_str if date_str else datetime.now() + timedelta(days=default_delta)
        except:
            return datetime.now() + timedelta(days=default_delta)



    # User operations
    def add_user(self, name, role, age=None):
        """Add new user to system"""
        try:
            user = {
                'name': name,
                'role': role,
                'age': age,
                'health_status': 'healthy',
                'health_records': []
            }
            result = self.db.users.insert_one(user)
            db_logger.info(f"Added user: {name}")
            return str(result.inserted_id)
        except Exception as e:
            db_logger.error(f"Error adding user {name}: {e}")
            return None


    def get_user(self, name):
        """Get user by name"""
        try:
            result = self.db.users.find_one({"name": name})
            return self.serialize_mongo_doc(result) if result else None
        except Exception as e:
            db_logger.error(f"Error getting user {name}: {e}")
            return None
        

    def get_all_users(self):
        """Get all users"""
        try:
            result = list(self.db.users.find({}))
            return self.serialize_mongo_doc(result)
        except Exception as e:
            db_logger.error(f"Error getting all users: {e}")
            return []
        


    def update_user_health(self, name, status=None, medical_record=None):
        """Update user health status and/or add medical record"""
        try:
            if status:
                self.db.users.update_one(
                    {"name": name},
                    {"$set": {"health_status": status}}
                )

            if medical_record:
                medical_record['date'] = datetime.now()
                self.db.users.update_one(
                    {"name": name},
                    {"$push": {"health_records": medical_record}}
                )

            db_logger.info(f"Updated health status for user: {name}")
            return True
        except Exception as e:
            db_logger.error(f"Error updating health status for user {name}: {e}")
            return False


    def get_user_health(self, name):
        """Get user's health status and records"""
        try:
            user = self.get_user(name)
            if user:
                return {
                    'status': user.get('health_status'),
                    'records': user.get('health_records', [])
                }
            return None
        except Exception as e:
            db_logger.error(f"Error getting health status for user {name}: {e}")
            return None
        



    # Inventory operations
    def add_inventory_item(self, name, category, quantity, info=None):
        """Add new item to inventory"""
        try:
            self._ensure_array_exists('inventory', 'items')
            
            item = {
                'name': name,
                'category': category,
                'quantity': quantity,
                'info': info or {},
                'created_at': datetime.now()
            }
            
            result = self.db.inventory.update_one(
                {},
                {'$push': {'items': item}}
            )
            
            if result.modified_count > 0:
                db_logger.info(f"Added inventory item: {name}")
                return True
            return False
        except Exception as e:
            db_logger.error(f"Error adding inventory item {name}: {e}")
            return False

    def get_inventory_item(self, name):
        """Get item from inventory by name"""
        try:
            result = self.db.inventory.find_one(
                {"items.name": name},
                {"items.$": 1}
            )
            return self.serialize_mongo_doc(result['items'][0]) if result else None
        except Exception as e:
            db_logger.error(f"Error getting inventory item {name}: {e}")
            return None

    def update_inventory_quantity(self, name, new_quantity):
        """Update item quantity in inventory"""
        try:
            result = self.db.inventory.update_one(
                {"items.name": name},
                {"$set": {"items.$.quantity": new_quantity}}
            )
            if result.modified_count > 0:
                db_logger.info(f"Updated quantity for item: {name}")
                return True
            return False
        except Exception as e:
            db_logger.error(f"Error updating quantity for item {name}: {e}")
            return False

    def get_low_stock_items(self, threshold=5):
        """Get items with low quantity"""
        try:
            result = list(self.db.inventory.aggregate([
                {'$unwind': '$items'},
                {'$match': {'items.quantity': {'$lt': threshold}}}
            ]))
            return self.serialize_mongo_doc(result)
        except Exception as e:
            db_logger.error(f"Error getting low stock items: {e}")
            return []

    # Shopping List operations
    def add_to_shopping_list(self, item_data):
        """Add item to shopping list"""
        try:
            self._ensure_array_exists('shopping_list', 'items')
            
            item = {
                'name': item_data['name'],
                'status': item_data.get('status', 'pending'),
                'info': item_data.get('info', {}),
                'added_at': datetime.now()
            }
            
            result = self.db.shopping_list.update_one(
                {},
                {'$push': {'items': item}},
                upsert=True
            )
            
            if result.modified_count > 0:
                db_logger.info(f"Added item to shopping list: {item['name']}")
                return True
            return False
        except Exception as e:
            db_logger.error(f"Error adding item to shopping list: {e}")
            return False

    def get_shopping_list(self):
        """Get entire shopping list"""
        try:
            result = self.db.shopping_list.find_one({})
            return self.serialize_mongo_doc(result) if result else None
        except Exception as e:
            db_logger.error(f"Error getting shopping list: {e}")
            return None

    def update_shopping_item_status(self, name, new_status):
        """Update shopping item status"""
        try:
            result = self.db.shopping_list.update_one(
                {"items.name": name},
                {"$set": {"items.$.status": new_status}}
            )
            if result.modified_count > 0:
                db_logger.info(f"Updated status for shopping item: {name}")
                return True
            return False
        except Exception as e:
            db_logger.error(f"Error updating shopping item status: {e}")
            return False

    def get_pending_shopping_items(self):
        """Get pending items from shopping list"""
        try:
            result = self.db.shopping_list.find_one(
                {"items.status": "pending"},
                {"items": {"$elemMatch": {"status": "pending"}}}
            )
            return self.serialize_mongo_doc(result) if result else None
        except Exception as e:
            db_logger.error(f"Error getting pending shopping items: {e}")
            return None
        



    # Task operations
    def add_task(self, name, assigned_to=None, due_date=None, info=None):
        """Add new task"""
        try:
            self._ensure_array_exists('tasks', 'tasks')
            
            due_date = self._parse_date(due_date)
            
            task = {
                'name': name,
                'assigned_to': assigned_to,
                'due_date': due_date,
                'status': 'pending',
                'info': info or {},
                'created_at': datetime.now()
            }

            result = self.db.tasks.update_one(
                {},
                {'$push': {'tasks': task}}
            )

            if result.modified_count > 0:
                db_logger.info(f"Added new task: {name}")
                return True
            return False
        except Exception as e:
            db_logger.error(f"Error adding task {name}: {e}")
            return False

    def complete_task(self, name):
        """Mark task as completed"""
        try:
            result = self.db.tasks.update_one(
                {"tasks.name": name},
                {
                    "$set": {
                        "tasks.$.status": "completed",
                        "tasks.$.completed_at": datetime.now()
                    }
                }
            )
            if result.modified_count > 0:
                db_logger.info(f"Completed task: {name}")
                return True
            return False
        except Exception as e:
            db_logger.error(f"Error completing task {name}: {e}")
            return False

    def get_pending_tasks(self):
        """Get all pending tasks"""
        try:
            result = list(self.db.tasks.aggregate([
                {'$unwind': '$tasks'},
                {'$match': {'tasks.status': 'pending'}},
                {'$sort': {'tasks.due_date': 1}}
            ]))
            return self.serialize_mongo_doc(result)
        except Exception as e:
            db_logger.error(f"Error getting pending tasks: {e}")
            return []

    def get_overdue_tasks(self):
        """Get overdue pending tasks"""
        try:
            result = list(self.db.tasks.aggregate([
                {'$unwind': '$tasks'},
                {'$match': {
                    'tasks.status': 'pending',
                    'tasks.due_date': {'$lt': datetime.now()}
                }}
            ]))
            return self.serialize_mongo_doc(result)
        except Exception as e:
            db_logger.error(f"Error getting overdue tasks: {e}")
            return []

    # Daily Log operations
    def add_daily_log(self, title, details=None):
        """Add new daily log entry"""
        try:
            self._ensure_array_exists('daily_log', 'logs')

            log = {
                'title': title,
                'date': datetime.now(),
                'details': {'text': details} if details else {},
                'created_at': datetime.now()
            }

            result = self.db.daily_log.update_one(
                {},
                {'$push': {'logs': log}}
            )

            if result.modified_count > 0:
                db_logger.info(f"Added daily log: {title}")
                return True
            return False
        except Exception as e:
            db_logger.error(f"Error adding daily log {title}: {e}")
            return False

    def get_today_logs(self):
        """Get all logs from today"""
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            result = list(self.db.daily_log.aggregate([
                {'$unwind': '$logs'},
                {'$match': {
                    'logs.date': {
                        '$gte': today,
                        '$lt': tomorrow
                    }
                }}
            ]))
            return self.serialize_mongo_doc(result)
        except Exception as e:
            db_logger.error(f"Error getting today's logs: {e}")
            return []

    def delete_daily_log(self, title):
        """Delete daily log entry by title"""
        try:
            result = self.db.daily_log.update_one(
                {},
                {'$pull': {'logs': {'title': title}}}
            )
            if result.modified_count > 0:
                db_logger.info(f"Deleted daily log: {title}")
                return True
            return False
        except Exception as e:
            db_logger.error(f"Error deleting daily log {title}: {e}")
            return False
            

    def get_date_logs(self, date):
        """Get logs from specific date"""
        try:
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d')
            next_date = date + timedelta(days=1)
            
            result = list(self.db.daily_log.aggregate([
                {'$unwind': '$logs'},
                {'$match': {
                    'logs.date': {
                        '$gte': date,
                        '$lt': next_date
                    }
                }}
            ]))
            return self.serialize_mongo_doc(result)
        except Exception as e:
            db_logger.error(f"Error getting logs for date {date}: {e}")
            return []
        


    # Utility functions
    def _convert_units(self, value, from_unit, to_unit):
        """
        Convert between units
        Supported conversions: kg<->g<->mg, l<->ml
        """
        try:
            conversions = {
                'kg': {'g': 1000, 'mg': 1000000},
                'l': {'ml': 1000}
            }
            
            if from_unit in conversions and to_unit in conversions[from_unit]:
                return value * conversions[from_unit][to_unit]
            elif to_unit in conversions and from_unit in conversions[to_unit]:
                return value / conversions[to_unit][from_unit]
            return None
        except Exception as e:
            db_logger.error(f"Error converting units: {e}")
            return None

    def serialize_mongo_doc(self, doc):
        """Convert MongoDB document to JSON-serializable format"""
        try:
            if isinstance(doc, dict):
                return {
                    k: str(v) if isinstance(v, (ObjectId, datetime)) else
                    self.serialize_mongo_doc(v) if isinstance(v, (dict, list)) else v
                    for k, v in doc.items()
                }
            elif isinstance(doc, list):
                return [self.serialize_mongo_doc(item) for item in doc]
            return doc
        except Exception as e:
            db_logger.error(f"Error serializing document: {e}")
            return None

    def close(self):
        """Close MongoDB connection"""
        try:
            self.client.close()
            db_logger.info("Closed database connection")
        except Exception as e:
            db_logger.error(f"Error closing database connection: {e}")