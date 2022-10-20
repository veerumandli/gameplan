# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals
import frappe
from gameplan.search_index import SearchIndex
from redis.commands.search.query import Query
from frappe.utils import strip_html_tags


class DiscussionsSearchIndex(SearchIndex):
	index_name = "discussions_index"
	prefix = "discussions_search_doc"

	def get_schema(self):
		return (
			self.TextField("title", weight=3.0),
			self.TextField("content"),
			self.TextField("modified"),
			self.TextField("comment")
		)

	def get_key(self, record):
		return f'{record.name}:{record.comment}'

	def get_records_to_index(self):
		records = []
		result = frappe.db.get_all('Team Discussion', fields=['name', 'title', 'content', 'modified'])
		for d in result:
			d.comment = ''
			d.content = strip_html_tags(d.content)
			d.modified = frappe.utils.cstr(d.modified)
			records.append(d)

		result = frappe.db.get_all('Team Comment',
			fields=['name', 'content', 'reference_name', 'modified'],
			filters={'reference_doctype': 'Team Discussion', 'deleted_at': ('is', 'not set')}
		)
		for d in result:
			d.title = ''
			d.comment = d.name
			d.name = d.reference_name
			d.content = strip_html_tags(d.content)
			d.modified = frappe.utils.cstr(d.modified)
			records.append(d)

		return records


@frappe.whitelist()
def search(query, start=0):
	index = DiscussionsSearchIndex()
	query = Query(query).paging(start, 30).highlight(tags=["<mark>", "</mark>"]).sort_by("modified", asc=False)
	result = index.search(query)
	if result.total == 0:
		return result

	names = []
	for d in result.docs:
		_, name, comment = d.id.split(':')
		names.append(frappe.utils.cint(name))
	names = list(set(names))

	data_by_name = {
		d.name: d
		for d in frappe.db.get_all('Team Discussion',
			fields=['name', 'title', 'team', 'project', 'owner', 'modified', 'creation', 'last_post_at', 'last_post_by', 'comments_count', 'closed_at', 'closed_by'],
			filters={'name': ['in', names]}
		)
	}

	docs = []
	seen = []
	for d in result.docs:
		_, name, comment = d.id.split(':')
		name = frappe.utils.cint(name)
		if name in seen:
			continue
		doc = data_by_name[name]
		if d.title:
			doc.title = d.title
		doc.comment = d.comment
		doc.content = d.content
		docs.append(doc)
		seen.append(name)

	return {
		"docs": docs,
		"total": result.total,
		"duration": result.duration
	}


def rebuild_index_in_background():
	frappe.enqueue(rebuild_index_if_not_exists, force=True, queue='long')


def rebuild_index_if_not_exists(force=False):
	index = DiscussionsSearchIndex()
	if not index.exists() or force:
		index.rebuild_index()
