# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.forms.widgets import Select
from django.forms.widgets import Textarea
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.html import escape


# Originaly comes from https://djangosnippets.org/snippets/2453/
class SelectWithDisabled(Select):
    """ Subclass of Django's select widget that allows disabling options.

    To disable an option, pass a dict instead of a string for its label, of the form:

        {'label': 'option label', 'disabled': True}

    """
    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_text(option_value)
        if (option_value in selected_choices):
            selected_html = ' selected="selected"'
        else:
            selected_html = ''
        disabled_html = ''
        if isinstance(option_label, dict):
            if dict.get(option_label, 'disabled'):
                disabled_html = ' disabled="disabled"'
            option_label = option_label['label']
        return '<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, disabled_html,
            conditional_escape(force_text(option_label)))


class MarkdownTextareaWidget(Textarea):
    """ A simple Textarea widget using the simplemde JS library to provide Markdown editor. """
    class Media:
        css = {
            'all': ('machina/build/css/vendor/simplemde.min.css', ),
        }
        js = (
            'machina/build/js/vendor/simplemde.min.js',
            'machina/build/js/machina.editor.min.js',
        )

    def render(self, name, value, attrs=None):
        attrs = {} if attrs is None else attrs
        classes = attrs.get('classes', '')
        attrs['class'] = classes + ' machina-mde-markdown'
        return super(MarkdownTextareaWidget, self).render(name, value, attrs)
