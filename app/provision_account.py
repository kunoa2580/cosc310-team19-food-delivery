"""Trusted local provisioning: python -m app.provision_account."""
import argparse
from getpass import getpass
from app.schemas.account import Registration
from app.services.account_service import create_account
from app.repositories.restaurant_repository import RestaurantRepository


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a trusted restaurant/admin account")
    parser.add_argument("--role", choices=["restaurant", "admin"], required=True)
    parser.add_argument("--user-id", "--email", required=True, help="Account sign-in identifier")
    parser.add_argument("--name", required=True)
    parser.add_argument("--restaurant-id", type=int, action="append", default=[])
    args = parser.parse_args()
    for restaurant_id in args.restaurant_id:
        if RestaurantRepository().restaurant_repo_get_by_id(restaurant_id) is None:
            parser.error(f"Restaurant {restaurant_id} does not exist")
    password = getpass("Password (8-128 characters): ")
    if password != getpass("Confirm password: "):
        parser.error("Passwords do not match")
    account = create_account(Registration(name=args.name, email=args.user_id, password=password),
                             role=args.role, restaurant_ids=args.restaurant_id)
    print(f"Created {account.role} account {account.id}")


if __name__ == "__main__":
    main()
