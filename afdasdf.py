python manage.py shell -c "from policies.services import vector_db; c=vector_db.get_or_create_collection(vector_db.COLLECTION_NAME); print(c.count())"
