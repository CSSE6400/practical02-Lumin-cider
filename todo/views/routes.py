from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta

 
api = Blueprint('api', __name__, url_prefix='/api/v1') 

TEST_ITEM = {
    "id": 1,
    "title": "Watch CSSE6400 Lecture",
    "description": "Watch the CSSE6400 lecture on ECHO360 for week 1",
    "completed": True,
    "deadline_at": "2023-02-27T00:00:00",
    "created_at": "2023-02-20T00:00:00",
    "updated_at": "2023-02-20T00:00:00"
}
 
@api.route('/health') 
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET']) 
def get_todos(): 
   todos = Todo.query.all() 
   result = []
   completed = None
   
   if request.args.get('completed') != None:
      completed = True if request.args.get('completed') == 'true' else False

   window = request.args.get('window', type=int)
   
   for todo in todos:
      if not request.args:
         result.append(todo.to_dict()) 
      else:
         if completed is not None:
            if todo.completed == completed:
               result.append(todo.to_dict())
         
         if window is not None:
            if todo.deadline_at < (datetime.now() + timedelta(days=window)):
               result.append(todo.to_dict())
   return jsonify(result)

@api.route('/todos/<int:todo_id>', methods=['GET']) 
def get_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({'error': 'Todo not found'}), 404 
   return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['PUT']) 
def update_todo(todo_id):
   for key in request.json.keys():
      if key not in ["title", "id", "description", "completed", "deadline_at"]:
         return jsonify({'error':'unnecessary extra fields found'}), 400
      elif key == 'id':
         return jsonify({'error':'cannot change todo id'}),400

   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({'error': 'Todo not found'}), 404 
 
   todo.title = request.json.get('title', todo.title) 
   todo.description = request.json.get('description', todo.description) 
   todo.completed = request.json.get('completed', todo.completed) 
   todo.deadline_at = request.json.get('deadline_at', todo.deadline_at) 
   db.session.commit() 
 
   return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE']) 
def delete_todo(todo_id): 
   todo = Todo.query.get(todo_id) 
   if todo is None: 
      return jsonify({}), 200 
 
   db.session.delete(todo) 
   db.session.commit() 
   return jsonify(todo.to_dict()), 200

@api.route('/todos', methods=['POST']) 
def create_todo(): 
   if request.json.get('title') is None:
      return jsonify({'error': 'required title not found'}), 400
   
   for key in request.json.keys():
      if key not in ["title", "id", "description", "completed", "deadline_at"]:
         return jsonify({'error':'unnecessary extra fields found'}), 400

   todo = Todo(   
      title=request.json.get('title'), 
      description=request.json.get('description'), 
      completed=request.json.get('completed', False), 
   ) 
   if 'deadline_at' in request.json: 
      todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at')) 
 
   # Adds a new record to the database or will update an existing record 
   db.session.add(todo) 
   # Commits the changes to the database, this must be called for the changes to be saved 
   db.session.commit() 
   return jsonify(todo.to_dict()), 201


 
