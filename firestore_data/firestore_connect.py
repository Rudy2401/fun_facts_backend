import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
from google.cloud.firestore_v1 import _helpers
import json

cred = credentials.Certificate("funfacts-5b1a9-firebase-adminsdk-zcx1s-f0c4a47e26.json")
firebase_admin.initialize_app(cred)

db = firestore.Client()


def get_document(collection_name, document_id):
    # Reference to the collection
    collection_ref = db.collection(collection_name)

    # Reference to the document
    document_ref = collection_ref.document(document_id)

    # Get the document
    document = document_ref.get()

    # Check if the document exists
    if document.exists:
        print(f"Document data: {document.to_dict()}")
    else:
        print("No such document!")


def get_all_documents(collection_name):

    # Reference to the collection
    collection_ref = db.collection(collection_name)

    # Get all documents in the collection
    documents = collection_ref.stream()

    # Iterate over all documents, serialize GeoPoint  and convert to JSON
    dicts = []
    for doc in documents:
        doc_dict = doc.to_dict()
        for key, value in doc_dict.items():
            if isinstance(value, firestore.GeoPoint):
                doc_dict[key] = {"latitude": value.latitude, "longitude": value.longitude}
            elif isinstance(value, _helpers.DatetimeWithNanoseconds):
                doc_dict[key] = value.isoformat()
        dicts.append(doc_dict)
    json.dump(dicts, open(f"{collection_name}.json", "w"), indent=4)


if __name__ == '__main__':
    collection = "users"

    # Fetch a document
    get_all_documents(collection)