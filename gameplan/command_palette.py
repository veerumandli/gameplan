# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from gameplan.search_index import SearchIndex
from redis.commands.search.query import Query

class CommandPaletteSearchIndex(SearchIndex):
	index_name = 'command_palette_index'
	prefix = 'command_palette_search_doc'

	def get_schema(self):
		return (
            self.TextField("title", weight=3.0),
            self.TextField("modified"),
        )

	def get_key(self, record):
		return f'{record.doctype}:{record.name}'

	def get_records_to_index(self):
		out = []

		for doctype in ["Team", "Team Project", "Team Discussion", "Team Task"]:
			data = frappe.get_all(doctype, fields=["name", "title", "modified"])
			for d in data:
				d.doctype = doctype
				d.modified = frappe.utils.cstr(d.modified)
				out.append(d)

		return out

@frappe.whitelist()
def search(query, start=0):
	index = CommandPaletteSearchIndex()
	query = Query(query).paging(start, 5).sort_by("modified", asc=False)
	result = index.search(query)
	if result.total == 0:
		return []

	out = []
	for d in result.docs:
		_, doctype, name = d.id.split(':')
		record = frappe._dict(
			doctype=doctype,
			name=name,
			title=d.title,
			modified=d.modified,
		)
		out.append(record)

	return out



def rebuild_index_in_background():
	frappe.enqueue(rebuild_index_if_not_exists, force=True, queue='long')


def rebuild_index_if_not_exists(force=False):
	index = CommandPaletteSearchIndex()
	if not index.exists() or force:
		index.rebuild_index()
