import weaviate
from weaviate.classes.init import Auth
import os

client = weaviate.connect_to_custom(
    http_host="weaviate.nguyenh.work",
    http_port=443,
    http_secure=True,
    grpc_host="grpc.weaviate.nguyenh.work",
    grpc_port=443,
    grpc_secure=True,
    auth_credentials=Auth.api_key("189143d91a5b25e2"),
    headers={"X-Cohere-Api-Key": "189143d91a5b25e2"},
    skip_init_checks=True  # Skip gRPC health checks
)

