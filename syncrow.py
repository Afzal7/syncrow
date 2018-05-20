import sublime
import sublime_plugin
from urllib import request, parse
import json
import os.path
import yaml
import re

def plugin_loaded():
	window = sublime.active_window()
	window.run_command("syncrow", {"sync": 1})
	# pan = window.create_output_panel('my_panel')
	# pan.run_command("append", {"characters": "Hello World"})
	# window.run_command('show_panel', {'panel':'output.my_panel'})
	# window.run_command("show_panel", {"panel": "console", "toggle": True})
	# 	print(window)

class SyncrowCommand(sublime_plugin.TextCommand):

	def run(self, edit, **args):
		self.baseUrl = 'http://www.syncrow.in/'
		# self.baseUrl = 'http://localhost:3000'
		self.syncrow_key = self.view.settings().get("syncrow_key")
		self.window = sublime.active_window()

		# self.view.insert(edit, 0, "Hello, World!")
		# allcontent = sublime.Region(self.view.sel())
		# sublime.Region(0, self.view.size())
		# self.view.replace(edit, allcontent, 'Hello, World!')
		# print(urllib.request.urlopen(self.baseUrl+"/posts").read())
		# window.show_quick_panel('self.view.substr(sel)', None, sublime.MONOSPACE_FONT)

		if not os.path.isdir(os.path.join(sublime.packages_path(),'Syncrow Snippets')):
			os.mkdir(os.path.join(sublime.packages_path(),'Syncrow Snippets'))

		if 'sync' in args and args['sync']:
			self.sync()
			return

		sel = self.view.sel()[0]
		self.selected_text = self.view.substr(sel)

		if not self.selected_text:
			self.window.status_message('Syncrow - Select something first!')
			return

		print(self.selected_text)
		self.window.show_input_panel('Enter Snippet Name', '', self.on_done, '', '')

	def on_done(self, file_name):
		self.window.status_message('Syncrow - Waiting for the magic to happen...')
		snippet = {'name': file_name, 'content': self.sanitize_text(self.selected_text)}
		self.create_snippet(snippet, True)

	def sync(self):
		if not self.syncrow_key:
			return

		snippet_list = self.read_yaml()
		snippets_to_upload = [self.get_snippet_from_file(snippet['name']) for snippet in snippet_list if snippet['id'] == None]

		for snippet in snippets_to_upload:
			self.upload_snippet(snippet)

		snippet_list = self.read_yaml() #Reloading snippet list
		snippet_list_ids = [snippet['id'] for snippet in snippet_list if snippet['id'] != None]
		# snippet_list_ids = ','.join(str(x) for x in snippet_list_ids)

		self.window.status_message('Syncrow - Syncing...')

		data = parse.urlencode({'access_key': self.syncrow_key, 'snippets_already_present': snippet_list_ids}).encode()

		req =	request.Request(self.baseUrl+'/api/v1/users/sync_snippets', data=data)
		response_encoded = request.urlopen(req)
		response_decoded = response_encoded.read().decode(encoding='utf-8',errors='ignore')
		snippets = json.loads(response_decoded)


		# response = request.urlopen(self.baseUrl+"/api/v1/users/snippets?access_key="+self.syncrow_key+"&snippets_already_present="+snippet_list_ids)
		# response_text = response.read().decode(encoding='utf-8',errors='ignore')
		# snippets = json.loads(response_text)

		if snippets['success'] == True:
			for snippet in snippets['data']:
				self.create_snippet(snippet, False)

			self.window.status_message('Syncrow - Yay! Syncing completed.')
		else:
			self.window.status_message('Syncrow - Cant sync! Invalid syncrow secret key.')

	def create_snippet(self, snippet, upload):
		if upload:
			while os.path.isfile(os.path.join(sublime.packages_path(),'Syncrow Snippets',snippet['name']+".sublime-snippet")):
				self.window.status_message('Syncrow - Name Already Exists, Try Again :(')
				return

		fo = open(os.path.join(sublime.packages_path(),'Syncrow Snippets',snippet['name']+".sublime-snippet"), "w")
		
		snippet_file_content = "<snippet><content><![CDATA[%s]]></content><tabTrigger>%s</tabTrigger><description>Syncrow</description></snippet>" % (snippet['content'], snippet['name'])
		
		fo.write(snippet_file_content)
		fo.close()

		self.window.status_message('Syncrow - Done! Life is a bit easy now.')

		self.update_snippet_list(snippet)

		if upload:
			self.upload_snippet(snippet)

	def upload_snippet(self, snippet):
		if not self.syncrow_key:
			return
		print('2'*10)
		data = parse.urlencode({'access_key': self.syncrow_key, 'name': snippet['name'], 'content': snippet['content']}).encode()
		print(data)
		req =	request.Request(self.baseUrl+'/api/v1/users/add_snippet', data=data)
		response_encoded = request.urlopen(req)
		response_decoded = response_encoded.read().decode(encoding='utf-8',errors='ignore')
		response = json.loads(response_decoded)
		print('=================')
		print(response)
		print('=================')
		if response['success'] == True:
			self.window.status_message('Syncrow - Syncing completed!')
			self.update_snippet_id(response['data'])
		else:
			self.window.status_message('Syncrow - Snippet created but not synced! Check your syncrow secret key.')

	def sanitize_text(self, text):
		# return text.replace('$','\$')
		return re.sub(r'\$[^\$\{]', '\$', text)

	def get_snippet_list(self):
		snippet_list = []
		for file in os.listdir(sublime.packages_path()):
			if file.endswith(".sublime-snippet"):
				snippet_list.append(file)
				# print(os.path.join("/mydir", file))

		return snippet_list

	def get_snippet_from_file(self, snippet_name):
		for file in os.listdir(os.path.join(sublime.packages_path(),'Syncrow Snippets')):
			print(file)
			if file == snippet_name+".sublime-snippet":
				return {'name': snippet_name, 'content': open(os.path.join(sublime.packages_path(),'Syncrow Snippets',file), 'r').read()}

	def update_snippet_list(self, snippet):
		snippet_list = self.read_yaml() or []
		
		new_snippet = {'id': snippet.get('id'), 'name': snippet['name']}
		snippet_list.append(new_snippet)
		
		self.write_yaml(snippet_list)

	def update_snippet_id(self, snippet):
		snippet_list = self.read_yaml() or []
		
		# new_snippet = {'id': snippet.get('id'), 'name': snippet['name']}
		# snippet_list.append(new_snippet)

		for item in snippet_list:
			if item['name'] == snippet['name']:
				item['id'] = snippet['id']
		
		self.write_yaml(snippet_list)

	def read_yaml(self):
		if os.path.exists(os.path.join(sublime.packages_path(),'Syncrow Snippets',"index.yaml")):
			file = open(os.path.join(sublime.packages_path(),'Syncrow Snippets',"index.yaml"), "r")
		else:
			file = open(os.path.join(sublime.packages_path(),'Syncrow Snippets',"index.yaml"), "w+")
		
		snippet_list = yaml.load(file)
		file.close()
		
		return snippet_list or []

	def write_yaml(self, data):
		file = open(os.path.join(sublime.packages_path(),'Syncrow Snippets',"index.yaml"), "w")
		yaml.dump(data, file, default_flow_style=False)
		file.close()