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
from traits.api import HasTraits, List, Str, Float
from traitsui.api import View, UItem
from traitsui.editors import TableEditor
from traitsui.table_column import ObjectColumn

# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.core.helpers.formatting import floatfmt
from pychron.processing.analyses.view.magnitude_editor import MagnitudeColumn
from pychron.pychron_constants import INTERFERENCE_KEYS


class ErrorComponent(HasTraits):
    name = Str
    value = Float

    def get_percent_value(self):
        return self.value / 100


class ErrorComponentsView(HasTraits):
    name = 'Error Components'

    error_components = List

    def __init__(self, an, *args, **kw):
        super(ErrorComponentsView, self).__init__(*args, **kw)
        self._load(an)

    def _load(self, an):

        es = []
        keys = [k for k in an.arar_mapping.values() if k in an.isotopes]
        for k in keys:
            iso = an.isotopes[k]
            es.append(ErrorComponent(name=k,
                                     value=iso.age_error_component))
        for k in keys:
            d = '{} IC'.format(k)
            es.append(ErrorComponent(name=d,
                                     value=an.get_error_component(d)))
        for k in keys:
            d = '{} bk'.format(k)
            es.append(ErrorComponent(name=d,
                                     value=an.get_error_component(d)))

        for k in INTERFERENCE_KEYS + ('J',):
            v = an.get_error_component(k)
            es.append(ErrorComponent(name=k, value=v))

        self.error_components = es
        # self.pie_canvas.load_scene(es)

    def traits_view(self):
        cols = [ObjectColumn(name='name', label='Component'),
                MagnitudeColumn(name='value',
                                label='',
                                width=200),
                ObjectColumn(name='value', label='Value',
                             width=100,
                             format_func=lambda x: floatfmt(x, n=5))]
        editor = TableEditor(columns=cols,
                             sortable=False,
                             editable=False)

        # v = View(VGroup(
        #     # Item('pie_enabled', label='Show Pie Chart',
        #     #      visible_when='pie_enabled'),
        #     # HGroup(Item('pie_enabled', label='Show Pie Chart')),
        #     VGroup(
        #         UItem('error_components', editor=editor),
        #         defined_when='not pie_enabled'),
        #     VSplit(
        #         UItem('error_components', editor=editor),
        #         UItem('pie_canvas', editor=ComponentEditor()),
        #         defined_when='pie_enabled')))
        v = View(UItem('error_components', editor=editor))
        return v
        # def traits_view(self):
        #     v = View(UItem('error_components',
        #                    editor=TabularEditor(adapter=ErrorComponentAdapter(),
        #                                         editable=False)))
        #     return v

# ============= EOF =============================================
