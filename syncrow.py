import sublime
import sublime_plugin
from urllib import request, parse
import json
import os.path

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
		self.syncrow_key = self.view.settings().get("syncrow_key")
		self.window = sublime.active_window()

		# self.view.insert(edit, 0, "Hello, World!")
		# allcontent = sublime.Region(self.view.sel())
		# sublime.Region(0, self.view.size())
		# self.view.replace(edit, allcontent, 'Hello, World!')
		# print(urllib.request.urlopen(self.baseUrl+"/posts").read())
		# window.show_quick_panel('self.view.substr(sel)', None, sublime.MONOSPACE_FONT)

		print('-----------------')
		print(self.get_snippet_list())
		print('-----------------')

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
		self.create_snippet(self.selected_text, file_name, True)

	def sample_snippet_list(self):
		return [
			{
				"id": 1, "name": "basic-css", "content": "body" 
			}
		]

	def sync(self):
		if not self.syncrow_key:
			return

		self.window.status_message('Syncrow - Syncing...')
		response = request.urlopen(self.baseUrl+"/api/v1/users/snippets?access_key="+self.syncrow_key)
		response_text = response.read().decode(encoding='utf-8',errors='ignore')
		snippets = json.loads(response_text)

		print(snippets)
		if snippets['success'] == True:
			for snippet in snippets['data']:
				self.create_snippet(snippet['content'], snippet['name'], False)

			self.window.status_message('Syncrow - Yay! Syncing completed.')
		else:
			self.window.status_message('Syncrow - Cant sync! Invalid syncrow secret key.')

		# for i in list(range(3)):
		# 	print(snippets[i])

		# snippet_list = self.get_snippet_list()

	def create_snippet(self, snippet_content, file_name, upload):
		if not os.path.isdir(os.path.join(sublime.packages_path(),'Syncrow Snippets')):
			os.mkdir(os.path.join(sublime.packages_path(),'Syncrow Snippets'))
		if upload:
			while os.path.isfile(os.path.join(sublime.packages_path(),'Syncrow Snippets',file_name+".sublime-snippet")):
				self.window.status_message('Syncrow - Name Already Exists, Try Again :(')
				return

		fo = open(os.path.join(sublime.packages_path(),'Syncrow Snippets',file_name+".sublime-snippet"), "w")
		
		snippet = "<snippet><content><![CDATA[%s]]></content><tabTrigger>%s</tabTrigger><description>Syncrow</description></snippet>" % (snippet_content, file_name)
		
		fo.write(snippet)
		fo.close()

		self.window.status_message('Syncrow - Done! Life is a bit easy now.')

		if upload:
			self.upload_snippet(file_name, snippet_content)

	def upload_snippet(self, name, content):
		if not self.syncrow_key:
			return

		data = parse.urlencode({'access_key': self.syncrow_key, 'name': name, 'content': content}).encode()
		print(data)
		req =	request.Request(self.baseUrl+'/api/v1/users/add_snippet', data=data)
		response_encoded = request.urlopen(req)
		response_decoded = response_encoded.read().decode(encoding='utf-8',errors='ignore')
		response = json.loads(response_decoded)
		print('-----------------')
		print(response)
		print('-----------------')
		if response['success'] == True:
			self.window.status_message('Syncrow - Snippet syncing completed!')
		else:
			self.window.status_message('Syncrow - Snippet created but not synced! Check your syncrow secret key.')

	def get_snippet_list(self):
		snippet_list = []
		for file in os.listdir(sublime.packages_path()):
			if file.endswith(".sublime-snippet"):
				snippet_list.append(file)
				# print(os.path.join("/mydir", file))

		return snippet_list
