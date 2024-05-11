import os
from database import create_connection, get_sqlalchemy_uri, OUTPUT_PATH, mongo_database
from create_erd import create_erd
from sql_to_json import sql_to_json
from one_to_one import one_to_one
from many_to_many import many_to_many


def main():
    # connect to postgre
    conn = create_connection()

    # save to json
    sql_to_json(conn)

    # ask user if they want to view the ERD diagram
    view_erd = input("Do you want to view the JSON file? (y/n): ").lower()
    if view_erd == "y":
        os.startfile("schema_details.json")

    # ask user if they want to view the ERD diagram
    view_erd = input("Do you want to view the ERD diagram? (y/n): ").lower()
    if view_erd == "y":
        # create erd diagram
        uri = get_sqlalchemy_uri()
        create_erd(uri, OUTPUT_PATH)
        os.startfile(OUTPUT_PATH)

    # mongo database
    db = mongo_database()

    print("Choose the relationship handling method:")
    print("1: One-to-One")
    print("2: Delete junction tables")
    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        # one to one
        one_to_one(conn, db)
    elif choice == "2":
        # delete junction tables
        many_to_many(conn, db)
    else:
        print("Invalid choice. Exiting...")

    if conn is not None:
        conn.close()


if __name__ == "__main__":
    main()
