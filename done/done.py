""" Show a toggle which lets students mark things as done."""

import uuid

import pkg_resources
from django import utils
from xblock.core import XBlock
from xblock.fields import Boolean, DateTime, Float, Scope, String
from xblock.fragment import Fragment
from xblockutils.resources import ResourceLoader
from xblockutils.settings import ThemableXBlockMixin, XBlockWithSettingsMixin

from .utils import DummyTranslationService, _


def resource_string(path):
    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")


@XBlock.wants('settings')
@XBlock.needs('i18n')
class DoneXBlock(XBlock, XBlockWithSettingsMixin, ThemableXBlockMixin):
    """
    Show a toggle which lets students mark things as done.
    """

    done = Boolean(
        scope=Scope.user_state,
        help=_("Is the student done?"),
        default=False
    )

    align = String(
        scope=Scope.settings,
        help=_("Align left/right/center"),
        default=_("left")
    )

    has_score = True

    loader = ResourceLoader(__name__)

    block_settings_key = 'done'
    default_theme_config = {
        'package': 'done',
        'locations': ["static/css/done.css"]
    }

    @staticmethod
    def resource_string(path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    @property
    def i18n_service(self):
        """ Obtains translation service """
        return self.runtime.service(self, "i18n") or DummyTranslationService()

    def get_switch_style(self):
        try:
            return resource_string('static/css/translations/{lang}/switch_style.css'.format(
                lang=utils.translation.get_language(),
            ))
        except IOError:
            return resource_string('static/css/translations/en/switch_style.css')

    # pylint: disable=unused-argument
    @XBlock.json_handler
    def toggle_button(self, data, suffix=''):
        """
        Ajax call when the button is clicked. Input is a JSON dictionary
        with one boolean field: `done`. This will save this in the
        XBlock field, and then issue an appropriate grade.
        """
        if 'done' in data:
            self.done = data['done']
            if data['done']:
                grade = 1
            else:
                grade = 0
            grade_event = {'value': grade, 'max_value': 1}
            self.runtime.publish(self, 'grade', grade_event)
            # This should move to self.runtime.publish, once that pipeline
            # is finished for XBlocks.
            self.runtime.publish(self, "edx.done.toggled", {'done': self.done})

        return {'state': self.done}

    def student_view(self, context=None):  # pylint: disable=unused-argument
        """
        The primary view of the DoneXBlock, shown to students
        when viewing courses.
        """
        
        (unchecked_png, checked_png) = (
            self.runtime.local_resource_url(self, x) for x in
            ('public/check-empty.png', 'public/check-full.png')
        )
        if not context:
            context = {}

        context.update({
            'id': uuid.uuid1(0),
            'done': self.done
        })

        frag = Fragment()
        frag.add_content(self.loader.render_django_template(
            "static/html/done.html",
            context=context,
            i18n_service=self.i18n_service,
        ))
        frag.add_css(self.get_switch_style())
        frag.add_css(resource_string("static/css/done.css"))
        frag.add_javascript(resource_string("static/js/src/done.js"))
        frag.initialize_js("DoneXBlock", {'state': self.done,
                                          'unchecked': unchecked_png,
                                          'checked': checked_png,
                                          'align': self.align.lower()})
        return frag

    def studio_view(self, context=None):  # pylint: disable=unused-argument
        '''
        Minimal view with no configuration options giving some help text.
        '''
        frag = Fragment()
        frag.add_content(self.loader.render_django_template(
            "static/html/studioview.html",
            context=context,
            i18n_service=self.i18n_service,
        ))
        frag.add_css(self.get_switch_style())
        return frag

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("DoneXBlock",
             """<vertical_demo>
                  <done align="left"> </done>
                  <done align="right"> </done>
                  <done align="center"> </done>
                </vertical_demo>
             """),
        ]

    # Everything below is stolen from
    # https://github.com/edx/edx-ora2/blob/master/apps/openassessment/
    #        xblock/lms_mixin.py
    # It's needed to keep the LMS+Studio happy.
    # It should be included as a mixin.

    display_name = String(
        default=_("Completion"), scope=Scope.settings,
        help="Display name"
    )

    start = DateTime(
        default=None, scope=Scope.settings,
        help=_(
            "ISO-8601 formatted string representing the start date "
            "of this assignment. We ignore this."
        )
    )

    due = DateTime(
        default=None, scope=Scope.settings,
        help=_(
            "ISO-8601 formatted string representing the due date "
             "of this assignment. We ignore this."
        )
    )

    weight = Float(
        display_name=_("Problem Weight"),
        help=_(
            "Defines the number of points each problem is worth. "
            "If the value is not set, the problem is worth the sum of the "
            "option point values."
        ),
        values={"min": 0, "step": .1},
        scope=Scope.settings
    )

    def has_dynamic_children(self):
        """Do we dynamically determine our children? No, we don't have any.
        """
        return False

    def max_score(self):
        """The maximum raw score of our problem.
        """
        return 1
