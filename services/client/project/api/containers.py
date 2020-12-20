

# containers = {"matches": "http://127.0.0.1:5002", "clubs": "http://127.0.0.1:5003", "users": "http://127.0.0.1:5001"}
containers = {"matches": "http://matches:5000/", "clubs": "http://clubs:5000/", "users": "http://users:5000/"}

def get_container(name):
    return containers[name]