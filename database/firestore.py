from google.cloud import firestore
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
CRED_PATH = os.getenv("CRED_PATH")

class FirestoreDB:
    def __init__(self,cred_path=CRED_PATH):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
        self.db = firestore.Client()
        self.user_collection = self.db.collection("users")
    
    def create_user(self, chat_id: int, information: dict):
        """ Register information about a new user
        
        Parameters
        ----------
        chat_id: int
            Id from telegram chat
        information: dict
            Dictionary containing information about user
        
        Returns
        -------
        bool
            If it does not exists, returns False. Otherwise, True.
        """
        doc_ref = self.user_collection.document(str(chat_id))

        try:
            doc_ref.set({
                "chat_id": str(chat_id),
                "name": information["name"],
                "monthly_income": information["monthly_income"],
                "savings_target": information["savings_target"],
                "created_at": firestore.SERVER_TIMESTAMP
            })
            print(f"User {information["name"]} created successfully!")
            return True
        except Exception as exc:
            print(exc)
            return False

    def check_user(self, chat_id: int) -> bool:
        """ Checks if a user is already registered or not.
        
        Parameters
        ----------
        chat_id: int
            Id from telegram chat
        
        Returns
        -------
        bool
            If it does not exists, returns False. Otherwise, True.
        """
        doc_ref = self.user_collection.document(str(chat_id))
        return doc_ref.get().exists
    