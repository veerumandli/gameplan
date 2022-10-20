# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from redis.commands.search.field import TextField, NumericField
from redis.commands.search.indexDefinition import IndexDefinition
from frappe.utils import update_progress_bar
from frappe.utils.redis_wrapper import RedisWrapper
from redis.exceptions import ResponseError


class SearchIndex:
    index_name = None
    prefix = None
    TextField = TextField
    NumericField = NumericField

    def get_records_to_index(self):
        raise NotImplementedError

    def get_schema(self):
        raise NotImplementedError

    def get_key(self, record):
        raise NotImplementedError

    def search(self, query):
        r = frappe.cache()
        try:
            result = r.ft(self.index_name).search(query)
        except ResponseError:
            result = frappe._dict({
                "total": 0,
                "docs": [],
                "duration": 0
            })
        return result

    def exists(self):
        try:
            frappe.cache().ft(self.index_name).info()
            return True
        except ResponseError:
            return False

    def rebuild_index(self):
        r = frappe.cache()
        self.drop_index()
        # Options for index creation
        index_def = IndexDefinition(
            prefix = [f"{r.make_key(self.prefix).decode()}:"],
            score = 0.5,
            score_field = "doc_score"
        )
        schema = self.get_schema()
        # Create an index and pass in the schema
        r.ft(self.index_name).create_index(schema, definition=index_def)

        records_to_index = self.get_records_to_index()
        self.create_index_for_records(records_to_index)

    def create_index_for_records(self, records):
        r = frappe.cache()
        for i, d in enumerate(records):
            if not hasattr(frappe.local, 'request'):
                update_progress_bar('Indexing records', i, len(records), absolute=True)

            key = r.make_key(f"{self.prefix}:{self.get_key(d)}").decode()
            mapping = {
                field.name: d.get(field.name)
                for field in self.get_schema()
            }

            super(RedisWrapper, r).hset(key, mapping=mapping)

        if not hasattr(frappe.local, 'request'):
            print()

    def remove_index_for_records(self, records):
        r = frappe.cache()
        for d in records:
            key = r.make_key(f"{self.prefix}:{self.get_key(d)}").decode()
            r.ft(self.index_name).delete_document(key)

    def drop_index(self):
        try:
            r = frappe.cache()
            r.ft(self.index_name).dropindex(delete_documents=True)
        except ResponseError:
            pass
