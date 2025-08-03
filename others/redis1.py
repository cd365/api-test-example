import redis

"""
pip install redis
"""

if __name__ == "__main__":
    client = redis.Redis(
        host="127.0.0.1", port=6379, db=8, password="", decode_responses=True
    )
    key = "my_test_key"
    value = client.get(key)
    if value is not None:
        print(value)
    else:
        print(f"the value `{key}` is not found")
    client.setex(key, 5, "123123")
    value = client.get(key)
    print(value)
