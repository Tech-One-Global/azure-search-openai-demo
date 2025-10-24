import asyncio
import os
import sys

from azure.identity.aio import AzureDeveloperCliCredential
from msgraph import GraphServiceClient
from msgraph.generated.applications.item.add_password.add_password_post_request_body import (
    AddPasswordPostRequestBody,
)
from msgraph.generated.models.password_credential import PasswordCredential

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
from load_azd_env import load_azd_env


async def add_client_secret(graph_client: GraphServiceClient, app_id: str) -> str:
    request_password = AddPasswordPostRequestBody(
        password_credential=PasswordCredential(display_name="WebAppSecret"),
    )
    password_credential = await graph_client.applications.by_application_id(app_id).add_password.post(request_password)
    if password_credential is None:
        raise ValueError("Failed to create client secret")
    if password_credential.secret_text is None:
        raise ValueError("Created client secret has no secret text")
    return password_credential.secret_text


async def main():
    load_azd_env()
    
    auth_tenant = os.getenv("AZURE_AUTH_TENANT_ID", os.getenv("AZURE_TENANT_ID"))
    client_app_object_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not client_app_object_id:
        print("Usage: python fix_client_secret.py <client_app_object_id>")
        exit(1)
    
    credential = AzureDeveloperCliCredential(tenant_id=auth_tenant)
    scopes = ["https://graph.microsoft.com/.default"]
    graph_client = GraphServiceClient(credentials=credential, scopes=scopes)
    
    print(f"Adding client secret to {client_app_object_id}")
    client_secret = await add_client_secret(graph_client, client_app_object_id)
    print(f"\nClient secret created successfully!")
    print(f"Run this command to set it:")
    print(f"azd env set AZURE_CLIENT_APP_SECRET '{client_secret}'")


if __name__ == "__main__":
    asyncio.run(main())
