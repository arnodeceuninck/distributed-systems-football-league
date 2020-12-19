

containers = {"matches": "http://127.0.0.1:5002", "clubs": "http://127.0.0.1:5003"}
# containers = {"matches": "http://127.0.0.1/:5002"}

def get_container(name):
    return containers[name]