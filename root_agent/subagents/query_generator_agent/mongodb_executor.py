from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId
from dateutil.parser import isoparse
import traceback
from typing import Dict, Any

#these 3 lines for geting from .env file url which is kept there
from dotenv import load_dotenv
import os
# 🔑 Use Standard Connection String (mongodb:// instead of mongodb+srv://)
load_dotenv() 
MONGO_URI =os.getenv("Mongo_DB_URL")

DB_NAME = "sales_database"


def convert_object_ids(document):
    """Recursively convert ObjectId to str for JSON compatibility."""
    if isinstance(document, list):
        return [convert_object_ids(d) for d in document]
    elif isinstance(document, dict):
        return {k: str(v) if isinstance(v, ObjectId) else convert_object_ids(v) for k, v in document.items()}
    return document


def convert_iso_dates_in_query(query):
    """Convert ISO date strings inside query to datetime objects."""
    if isinstance(query, dict):
        for key, value in query.items():
            if isinstance(value, dict):
                convert_iso_dates_in_query(value)
            elif isinstance(value, str):
                try:
                    query[key] = isoparse(value)
                except ValueError:
                    pass
    return query


def convert_iso_dates_in_pipeline(pipeline):
    """Convert ISO date strings inside aggregation pipeline."""
    for stage in pipeline:
        if "$match" in stage:
            convert_iso_dates_in_query(stage["$match"])
    return pipeline


def mongodb_execution_tool(query_obj: Dict[str, Any]) -> Dict[str, Any]:
    client = None
    try:
        client_params = {
            "serverSelectionTimeoutMS": 20000,  # increase timeout
            "socketTimeoutMS": 30000,
            "connectTimeoutMS": 20000,
            "retryWrites": True,
            "appname": "query_generator",
            "tlsAllowInvalidCertificates": True,
        }

        client = MongoClient(MONGO_URI, **client_params)
        db = client[DB_NAME]
        coll = db[query_obj["collection"]]
        op = query_obj["operation"]

        # FIND
        if op == "find":
            q = query_obj.get("query", {})
            convert_iso_dates_in_query(q)
            cursor = coll.find(q, query_obj.get("projection"))

            if query_obj.get("explain"):
                return {"success": True, "explain": cursor.explain()}

            if sort := query_obj.get("sort"):
                cursor = cursor.sort(sort)
            if skip := query_obj.get("skip"):
                cursor = cursor.skip(skip)
            if limit := query_obj.get("limit"):
                cursor = cursor.limit(limit)

            return {"success": True, "data": convert_object_ids(list(cursor))}

        # AGGREGATE
        elif op == "aggregate":
            pipeline = query_obj.get("query", [])
            if not isinstance(pipeline, list):
                return {"success": False, "error": "Aggregation pipeline must be a list."}

            convert_iso_dates_in_pipeline(pipeline)

            if query_obj.get("explain"):
                explain_output = coll.aggregate(pipeline, allowDiskUse=True).explain()
                return {"success": True, "explain": convert_object_ids(explain_output)}

            result = list(coll.aggregate(pipeline, allowDiskUse=True))
            return {"success": True, "data": convert_object_ids(result)}

        # COUNT
        elif op == "count":
            q = query_obj.get("query", {})
            convert_iso_dates_in_query(q)

            if query_obj.get("explain"):
                explain_output = coll.find(q).explain()
                return {"success": True, "explain": convert_object_ids(explain_output)}

            count = coll.count_documents(q)
            return {"success": True, "count": count}

        # INSERT ONE
        elif op == "insert_one":
            result = coll.insert_one(query_obj["document"])
            return {"success": True, "inserted_id": str(result.inserted_id)}

        # INSERT MANY
        elif op == "insert_many":
            result = coll.insert_many(query_obj["document"])
            return {"success": True, "inserted_ids": [str(_id) for _id in result.inserted_ids]}

        # UPDATE ONE
        elif op == "update_one":
            result = coll.update_one(query_obj["query"], query_obj["update"])
            return {"success": True, "matched_count": result.matched_count, "modified_count": result.modified_count}

        # UPDATE MANY
        elif op == "update_many":
            result = coll.update_many(query_obj["query"], query_obj["update"])
            return {"success": True, "matched_count": result.matched_count, "modified_count": result.modified_count}

        # DELETE ONE
        elif op == "delete_one":
            result = coll.delete_one(query_obj["query"])
            return {"success": True, "deleted_count": result.deleted_count}

        # DELETE MANY
        elif op == "delete_many":
            result = coll.delete_many(query_obj["query"])
            return {"success": True, "deleted_count": result.deleted_count}

        else:
            return {"success": False, "error": f"Unsupported operation '{op}'"}

    except PyMongoError as e:
        return {"success": False, "error": "MongoDB Error", "details": str(e), "stack_trace": traceback.format_exc()}
    except Exception as e:
        return {"success": False, "error": "Unexpected Error", "details": str(e), "stack_trace": traceback.format_exc()}
    finally:
        if client:
            client.close()
