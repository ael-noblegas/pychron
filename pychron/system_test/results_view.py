# ===============================================================================
# Copyright 2014 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# ============= enthought library imports =======================
from traits.api import Instance, Int, Property, Any, Str
from traitsui.api import View, Controller, UItem, TabularEditor, VGroup, UReadonly
from pyface.timer.do_later import do_after
# ============= standard library imports ========================
# ============= local library imports  ==========================
from traitsui.tabular_adapter import TabularAdapter
from pychron.core.helpers.formatting import floatfmt
from pychron.pychron_constants import LIGHT_GREEN, LIGHT_RED, LIGHT_YELLOW


COLOR_MAP = {'Passed': LIGHT_GREEN,
             'Skipped': 'lightblue',
             'Failed': LIGHT_RED,
             'Invalid': LIGHT_YELLOW}


class ResultsAdapter(TabularAdapter):
    columns = [('Plugin', 'plugin'),
               ('Name', 'name'),
               ('Duration (s)', 'duration'),
               ('Result', 'result')]
    plugin_width = Int(200)
    name_width = Int(200)
    duration_text = Property

    def get_bg_color(self, obj, trait, row, column=0):
        return COLOR_MAP[self.item.result]

    def _get_duration_text(self):
        return floatfmt(self.item.duration)  # '{:0.5f}'.format(self.item.duration)


class ResultsView(Controller):
    model = Instance('pychron.system_test.tester.SystemTester')
    auto_close = 5
    selected = Any

    # def close( self, info, is_ok ):
    # print info, is_ok
    help_str = Str('Select any row to cancel auto close')

    def _selected_changed(self, new):
        self._cancel_auto_close = bool(new)

    def init(self, info):
        if self.auto_close:
            do_after(self.auto_close * 1000, self._do_auto_close)

    def _do_auto_close(self):
        if self.should_close:
            self.info.ui.dispose()

    @property
    def should_close(self):
        a = self._cancel_auto_close
        b = self.model.all_passed

        return not a and b

    def traits_view(self):
        v = View(VGroup(UItem('results', editor=TabularEditor(adapter=ResultsAdapter(),
                                                              editable=False,
                                                              selected='controller.selected')),
                        VGroup(UReadonly('controller.help_str'), show_border=True)),
                 title='Test Results',
                 buttons=['OK'],
                 width=600,
                 resizable=True)
        return v

# ============= EOF =============================================



