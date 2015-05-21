# ===============================================================================
# Copyright 2015 Jake Ross
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
from traits.api import Float, Str, List
from traitsui.api import Item, EnumEditor
# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.core.confirmation import remember_confirmation_dialog
from pychron.experiment.utilities.identifier import SPECIAL_MAPPING
from pychron.pipeline.graphical_filter import GraphicalFilterModel, GraphicalFilterView
from pychron.pipeline.nodes.base import BaseNode


class FindReferencesNode(BaseNode):
    user_choice = False
    threshold = Float

    analysis_type = Str
    analysis_types = List
    # analysis_type_name = None
    name = 'Find References'

    def reset(self):
        self.user_choice = None

    def load(self, nodedict):
        self.threshold = nodedict['threshold']
        self.analysis_type = nodedict['analysis_type']

    # def dump(self, obj):
    #     obj['threshold'] = self.threshold

    def _analysis_type_changed(self, new):
        self.name = 'Find {}s'.format(new)

    def run(self, state):
        if not state.unknowns:
            return

        times = sorted((ai.rundate for ai in state.unknowns))

        atype = self.analysis_type.lower().replace('_', ' ')
        refs = self.dvc.find_references(times, atype)
        if refs:
            review = self.user_choice
            if self.user_choice is None:
                # ask if use whats to review
                review, remember = remember_confirmation_dialog('What you like to review this Node? '
                                                                '{}'.format(self.name))
                if remember:
                    self.user_choice = review

            if review:
                ans = state.unknowns[:]
                ans.extend(refs)
                # refs.extend(state.unknowns)
                model = GraphicalFilterModel(analyses=ans)
                model.setup()
                model.analysis_types = [self.analysis_type]

                obj = GraphicalFilterView(model=model)
                info = obj.edit_traits(kind='livemodal')
                if info.result:
                    refs = model.get_filtered_selection()
                    if obj.is_append:
                        refs = state.references.extend(refs)

                        # refs = ans
            state.references = refs
            state.has_references = True

    def traits_view(self):
        v = self._view_factory(Item('threshold',
                                    tooltip='Maximum difference between blank and unknowns in hours',
                                    label='Threshold (Hrs)'),
                               Item('analysis_type',
                                    editor=EnumEditor(name='analysis_types')))

        return v

    def _analysis_types_default(self):
        return [' '.join(map(str.capitalize, k.split('_'))) for k in SPECIAL_MAPPING.keys()]

#
# class FindAirsNode(FindNode):
#     name = 'Find Airs'
#     analysis_type = 'blank_unknown'
#     analysis_type_name = 'Air'
#
#
# class FindBlanksNode(FindNode):
#     name = 'Find Blanks'
#     analysis_type = 'blank_unknown'
#     analysis_type_name = 'Blank Unknown'


# ============= EOF =============================================



