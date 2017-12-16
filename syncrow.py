import sublime
import sublime_plugin
from urllib import request, parse
import json
import os.path

def plugin_loaded():
	print(sublime.platform())
	window = sublime.active_window()
	# pan = window.create_output_panel('my_panel')
	# pan.run_command("append", {"characters": "Hello World"})
	# window.run_command('show_panel', {'panel':'output.my_panel'})
	# window.run_command("show_panel", {"panel": "console", "toggle": True})
	window.run_command("syncrow", {"sync": 1})
	# 	print(window)

class SyncrowCommand(sublime_plugin.TextCommand):

	def run(self, edit, **args):
		self.baseUrl = 'http://192.168.0.114:3000/'
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
		print(self.selected_text)
		self.window.show_input_panel('Enter Snippet Name', '', self.on_done, '', '')

	def on_done(self, file_name):
		sublime.status_message('Waiting for the magic to happen...')
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

		sublime.status_message('Syncing...')
		response = request.urlopen(self.baseUrl+"/api/v1/snippet?access_token="+self.syncrow_key)
		response_text = response.read().decode(encoding='utf-8',errors='ignore')
		snippets = json.loads(response_text)
		print(snippets)
		sublime.status_message('Yay! Syncing completed.')

		# for i in list(range(3)):
		# 	print(snippets[i])

		snippet_list = self.get_snippet_list()

		for snippet in snippets:
			self.create_snippet(snippet['content'], snippet['name'], False)

		# snippet_file = open(sublime.packages_path()+'/syncrow_snippet_list.json', "w+")
		# print(123123123)
		# print(self.sample_snippet_list())
		# print(123123123)
		# snippet_file.write(self.sample_snippet_list())
		# print(snippet_file.read())
		# snippet_list = json.load(snippet_file)
		# for snippet in snippet_list.values():
		# 		print(snippet['id'], snippet['name'], snippet['content'])
		# snippet_file.close()

		# with open(sublime.packages_path()+'/syncrow_snippet_list.json', 'w+') as snippet_file:
		# 	# print(json.dumps(self.sample_snippet_list()))
		# 	snippet_file.write(json.dumps(self.sample_snippet_list()))
		# with open(sublime.packages_path()+'/syncrow_snippet_list.json', 'r') as snippet_file:
		# 	# print(snippet_file)
		# 	snippet_list = json.loads(snippet_file.read())
		# 	print(snippet_list)
		# 	for snippet in snippet_list:
		# 			print(snippet['id'], snippet['name'], snippet['content'])
		# snippet_list = open(sublime.packages_path()+'/syncrow_snippet_list.json', "w")

	def create_snippet(self, snippet_content, file_name, upload):
		if upload:
			while os.path.isfile(sublime.packages_path()+'/'+file_name+".sublime-snippet"):
				sublime.status_message('Name Already Exists, Try Again :(')
				return

		fo = open(sublime.packages_path()+'/'+file_name+".sublime-snippet", "w")
		
		snippet = "<snippet><content><![CDATA[%s]]></content><tabTrigger>%s</tabTrigger><description>Syncrow</description></snippet>" % (snippet_content, file_name)
		
		fo.write(snippet)
		fo.close()

		sublime.status_message('Done! Life is a little bit easy now.')

		if upload:
			self.upload_snippet(file_name, snippet_content)

	def upload_snippet(self, name, content):
		if not self.syncrow_key:
			return

		data = parse.urlencode({'name': name, 'content': content}).encode()
		req =	request.Request(self.baseUrl+'/api/v1/snippet?access_token='+self.syncrow_key, data=data)
		response = request.urlopen(req)
		response_text = response.read().decode(encoding='utf-8',errors='ignore')
		snippet = json.loads(response_text)
		print('-----------------')
		print(snippet)
		print('-----------------')
		sublime.status_message('Snippet syncing completed!')
		syncrow_json.append(snippet)


	def get_snippet_list(self):
		snippet_list = []
		for file in os.listdir(sublime.packages_path()):
			if file.endswith(".sublime-snippet"):
				snippet_list.append(file)
				# print(os.path.join("/mydir", file))

		return snippet_list