"""
Sublime Text package to format Python code using `black`
https://github.com/ambv/black formatter.
"""
import os
import sublime
import sublime_plugin

#: name of the plugin
PLUGIN_NAME = os.path.splitext(os.path.basename(__file__))[0]
#: settings filename
SETTINGS = "{}.sublime-settings".format(PLUGIN_NAME)


def load_user_settings():
	"""Method to procure user settings for black."""
	return sublime.load_settings(SETTINGS)


def execute(window, settings, diff_only=False):
	"""Command to execute in window."""

	# TODO(vishwas): Once Sublime text starts supporting Python3.6+ extend
	# the same to format view strings in addition to the files. This is
	# currently not possible as any python module imported within plugin
	# would run in Python3.3 which doesn't support `black`.
	file_name = window.active_view().file_name()
	if not file_name:
		sublime.message_dialog("Black formatter can currently be run only on saved files.")
		return

	command = "black {} -l {} {}".format(
		"--diff" if diff_only else " ",
		settings.get("line_length", 88),
		" -S" if settings.get("skip_string_normalization", False) else "",
	)

	cmd = []
	# To ensure we don't have any issues with respect to click's
	# http://click.pocoo.org/5/python3/#python-3-surrogate-handling
	encoding = settings.get("encoding", None)
	if encoding is not None:
		cmd.append(encoding)

	cmd.append(command)
	cmd.append('"{}"'.format(file_name))
	window.run_command("exec", {"shell_cmd": " ".join(cmd)})


class black_format(sublime_plugin.WindowCommand):
	"""Command to format files in place using `black`."""

	def run(self):
		"""Run command"""
		if "Python" in self.window.active_view().settings().get("syntax"):
			execute(self.window, load_user_settings())


class black_diff(sublime_plugin.WindowCommand):
	"""Command to show what would be different if formatted using `black`."""

	def run(self):
		"""Run command"""
		if "Python" in self.window.active_view().settings().get("syntax"):
			execute(self.window, load_user_settings(), True)


class AutoRunBlack(sublime_plugin.EventListener):
	""" Listen for events triggered by ST. """

	def on_post_save_async(self, view):
		"""Run black on save"""
		settings = load_user_settings()
		if settings.get("run_on_save", False):
			if "Python" in view.settings().get("syntax"):
				execute(view.window(), settings)
