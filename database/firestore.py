from google.cloud import firestore
from datetime import datetime
from dotenv import load_dotenv
import pendulum
import os

load_dotenv()
CRED_PATH = os.getenv("CRED_PATH")

class FirestoreDB:
    def __init__(self,cred_path=CRED_PATH):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
        self.db = firestore.Client()
        self.user_collection = self.db.collection("users")
        self.monthly_expenses = self.db.collection("monthly_expenses")
    
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
    
# def insert_expense(self, chat_id: int, information: dict):
#     """ Register a new expense
    
#     Parameters
#     ----------
#     chat_id: int
#         Id from telegram chat
#     information: dict
#         Dictionary containing information about expense
    
#     Returns
#     -------
#     bool
#         If it all goes right, returns True. Returns False in case of error.
#     """
#     dt = pendulum.from_format(information["date"], "DD/MM/YYYY")
#     str_dt = dt.format('MM_YYYY')
#     doc_ref = self.monthly_expenses.document(str_dt)
#     print("Month document seen: ",str_dt)

#     try:
#         doc_ref.set({
#             "chat_id": information["chat_id"],
#             "value": information["value"],
#             "description": information["description"],
#             "category": information["category"],
#             "date": information["date"],
#             "created_at": firestore.SERVER_TIMESTAMP
#         })
#         print(f"Expense registered successfully!")
#         return True
#     except Exception as exc:
#         print(exc)
#         return False
    
    def insert_expense(self, chat_id: int, information: dict) -> bool:
        """
        Register a new expense inside user's subcollection 'expenses'.
        
        Expected information keys: value, description, category, date (DD/MM/YYYY)
    
        Parameters
        ----------
        chat_id: int
            Id from telegram chat
        information: dict
            Dictionary containing information about expense

        Returns
        -------
        bool
            If it all goes right, returns True. Returns False in case of error.
        """
        try:
            dt = pendulum.from_format(information["date"], "DD/MM/YYYY")
            formatted_date = dt.format("YYYY-MM-DD")

            # Path: users/{chat_id}/expenses/{auto_id}
            expenses_ref = self.user_collection.document(str(chat_id)).collection("expenses")
            
            expense_data = {
                "value": information.get("value"),
                "description": information.get("description", ""),
                "category": information.get("category", ""),
                "date": formatted_date,
                "month_year": dt.format("MM-YYYY"),  # useful for queries
                "created_at": firestore.SERVER_TIMESTAMP
            }

            expenses_ref.add(expense_data)  # Firestore auto-generates an ID
            print(f"Expense added for user {chat_id}: {expense_data}")
            return True

        except Exception as exc:
            print(f"Error inserting expense: {exc}")
            return False