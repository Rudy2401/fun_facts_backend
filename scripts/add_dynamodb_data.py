import json
import datetime
import boto3


def clean_landmarks_data():
    # Load the data from the JSON file
    with open("../firestore_data/landmarks.json") as f:
        data = json.load(f)

    # Clean the data
    for landmark in data:
        del landmark["l"]
        del landmark["g"]
        del landmark["dislikes"]
        landmark["createdAt"] = datetime.datetime.now().isoformat()
        landmark["updatedAt"] = datetime.datetime.now().isoformat()
        landmark["likes"] = 0

        # Convert the coordinates to decimal
        landmark["coordinates"]["latitude"] = str(landmark["coordinates"]["latitude"])
        landmark["coordinates"]["longitude"] = str(landmark["coordinates"]["longitude"])

    # Write the cleaned data back to the JSON file
    return data


def clean_fun_facts_data():
    # Load the data from the JSON file
    with open("../firestore_data/funFacts.json") as f:
        data = json.load(f)

    # Clean the data
    for fun_fact in data:
        del fun_fact["dislikes"]
        fun_fact["createdAt"] = datetime.datetime.now().isoformat()
        fun_fact["updatedAt"] = datetime.datetime.now().isoformat()
        fun_fact["likes"] = 0
        fun_fact["funFactId"] = fun_fact["id"]
        del fun_fact["id"]
        del fun_fact["verificationFlag"]
        del fun_fact["disputeFlag"]
        del fun_fact["dateSubmitted"]
        fun_fact["funFactStatus"] = "APPROVED"

        if "rejectionUsers" in fun_fact:
            del fun_fact["rejectionUsers"]

        if "approvalUsers" in fun_fact:
            del fun_fact["approvalUsers"]

        if "rejectionReason" in fun_fact:
            del fun_fact["rejectionReason"]

    # Write the cleaned data back to the JSON file
    return data


def get_distinct_categories(data):
    categories = set()
    for landmark in data:
        categories.add(landmark["type"])
    return categories


def add_data(data, table_name):
    # Connect to DynamoDB
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    # Add the list of dict to the table
    with table.batch_writer() as batch:
        for item in data:
            batch.put_item(Item=item)


if __name__ == "__main__":
    # Clean the data
    landmarks_data = clean_landmarks_data()
    # fun_facts_data = clean_fun_facts_data()
    print(get_distinct_categories(landmarks_data))

    # Add the data to the Landmarks table
    # add_data(fun_facts_data, "FunFact")