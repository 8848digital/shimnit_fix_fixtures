import json
import os
import frappe
from frappe.core.doctype.data_import.data_import import export_json, import_doc


def before_migrate():
	export_fixtures()

def after_migrate():
	frappe.enqueue(import_fixtures, job_id='Upload Permissions')
	# import_fixtures()


def import_fixtures(app='fix_fixtures'):

	fixtures_path = frappe.get_app_path(app, "fixtures")
	if not os.path.exists(fixtures_path):
		return

	fixture_files = os.listdir(fixtures_path)

	for fname in fixture_files:
		print(fname)
		if not fname.endswith(".json"):
			continue

		file_path = frappe.get_app_path(app, "fixtures", fname)
		try:
			import_doc(file_path)
		except (ImportError, frappe.DoesNotExistError) as e:
			# fixture syncing for missing doctypes
			print(f"Skipping fixture syncing from the file {fname}. Reason: {e}")

def export_fixtures(app=None):
	"""Export fixtures as JSON to `[app]/fixtures`"""

	print(frappe.get_app_path('fix_fixtures', "fixtures"))
	if app:
		apps = [app]
	else:
		apps = frappe.get_installed_apps()
	i = 0
	for app in apps:
		for fixture in frappe.get_hooks("fixtures", app_name=app):
			filters = None
			or_filters = None
			if isinstance(fixture, dict):
				filters = fixture.get("filters")
				or_filters = fixture.get("or_filters")
				fixture = fixture.get("doctype") or fixture.get("dt")
			print(f"Exporting {fixture} app {app} filters {(filters if filters else or_filters)}")
			if not os.path.exists(frappe.get_app_path('fix_fixtures', "fixtures")):
				os.mkdir(frappe.get_app_path('fix_fixtures', "fixtures"))

			export_json(
				fixture,
				frappe.get_app_path('fix_fixtures', "fixtures", str(i) + frappe.scrub(fixture) + ".json"),
				filters=filters,
				or_filters=or_filters,
				order_by="idx asc, creation asc",
			)
			i=i+1