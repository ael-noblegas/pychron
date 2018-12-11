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
from pyface.confirmation_dialog import confirm
from pyface.constant import YES
from traits.api import Float, Str, List, Property, cached_property, Button, Bool
from traitsui.api import Item, EnumEditor, UItem, VGroup

from pychron.core.helpers.iterfuncs import partition, groupby_group_id
from pychron.core.pychron_traits import BorderHGroup, BorderVGroup
from pychron.core.ui.check_list_editor import CheckListEditor
from pychron.pipeline.editors.flux_results_editor import FluxPosition
from pychron.pipeline.graphical_filter import GraphicalFilterModel, GraphicalFilterView
from pychron.pipeline.nodes.data import DVCNode
from pychron.pychron_constants import DEFAULT_MONITOR_NAME, NULL_STR, REFERENCE_ANALYSIS_TYPES, BLANKS


def compress_groups(ans):
    if ans:
        for i, (gid, analyses) in enumerate(groupby_group_id(ans)):
            for ai in analyses:
                ai.group_id = i


class FindNode(DVCNode):
    pass


class BaseFindFluxNode(FindNode):
    irradiation = Str
    irradiations = Property
    samples = Property(depends_on='irradiation, level')
    levels = Property(depends_on='irradiation')
    level = Str
    monitor_sample_name = Str(DEFAULT_MONITOR_NAME)

    def load(self, nodedict):
        self.irradiation = nodedict.get('irradiation', '')
        self._load_hook(nodedict)

    def _load_hook(self, nodedict):
        pass

    def _to_template(self, d):
        d['irradiation'] = self.irradiation

    def _irradiation_changed(self):
        try:
            self.level = self.levels[0]
        except IndexError:
            pass

    @cached_property
    def _get_samples(self):
        if self.irradiation and self.level:
            return self.dvc.distinct_sample_names(self.irradiation, self.level)
        else:
            return []

    @cached_property
    def _get_levels(self):
        if self.irradiation and self.dvc:
            irrad = self.dvc.get_irradiation(self.irradiation)
            return sorted([l.name for l in irrad.levels])
        else:
            return []

    @cached_property
    def _get_irradiations(self):
        if self.dvc:
            irrads = self.dvc.get_irradiations()
            return [i.name for i in irrads]
        else:
            return []

    def _fp_factory(self, geom, irradiation, level, identifier, sample, hole_id, fluxes):

        pp = next((p for p in fluxes if p['identifier'] == identifier))

        j, j_err, mean_j, mean_j_err, model_kind = 0, 0, 0, 0, ''
        if pp:
            j = pp.get('j', 0)
            j_err = pp.get('j_err', 0)
            mean_j = pp.get('mean_j', 0)
            mean_j_err = pp.get('mean_j_err', 0)

            options = pp.get('options')
            if options:
                model_kind = pp.get('model_kind', '')

        x, y, r, idx = geom[hole_id - 1]
        fp = FluxPosition(identifier=identifier,
                          irradiation=irradiation,
                          level=level,
                          sample=sample, hole_id=hole_id,
                          saved_j=j or 0,
                          saved_jerr=j_err or 0,
                          mean_j=mean_j or 0,
                          mean_jerr=mean_j_err or 0,
                          model_kind=model_kind,
                          x=x, y=y)
        return fp


class FindVerticalFluxNode(BaseFindFluxNode):
    select_all_button = Button('Select All')
    selected_levels = List

    def run(self, state):
        state.levels = self.selected_levels
        state.irradiation = self.irradiation

    def _select_all_button_fired(self):
        self.selected_levels = self.levels

    def traits_view(self):
        v = self._view_factory(Item('irradiation', editor=EnumEditor(name='irradiations')),
                               UItem('select_all_button'),
                               UItem('selected_levels',
                                     style='custom',
                                     editor=CheckListEditor(name='levels')),
                               width=300,
                               title='Select Irradiation and Level',
                               resizable=True)
        return v


class FindRepositoryAnalysesNode(FindNode):
    repositories = List

    def run(self, state):
        dvc = self.dvc
        rs = []
        for ri in self.repositories:
            ans = dvc.get_repoository_analyses(ri)
            rs.extend(ans)

        unks, refs = partition(rs, predicate=lambda x: x.analysis_type == 'unknown')
        state.unknowns = unks
        state.references = refs
        self.unknowns = unks
        self.references = refs


class FindFluxMonitorMeansNode(BaseFindFluxNode):
    name = 'Find Flux Monitors'

    def _load_hook(self, nodedict):
        self.level = nodedict.get('level', '')
        self.irradiation = nodedict.get('irradiation', '')

    def run(self, state):
        if not self.irradiation or not self.level:
            self.configure()

        if not self.irradiation or not self.level:
            state.veto = self
        else:
            dvc = self.dvc
            args = dvc.get_irradiation_geometry(self.irradiation, self.level)
            if args:
                geom, holder = args
                state.geometry = geom
                state.holder = holder

            ips = dvc.get_flux_monitors(self.irradiation, self.level, self.monitor_sample_name)

            fluxes = dvc.get_flux_positions(self.irradiation, self.level)
            state.monitor_positions = [self._fp_factory(state.geometry, self.irradiation, self.level,
                                                        ip.identifier, ip.sample.name, ip.position, fluxes)
                                       for ip in ips if ip.identifier]

    def traits_view(self):
        v = self._view_factory(Item('irradiation', editor=EnumEditor(name='irradiations')),
                               Item('level', editor=EnumEditor(name='levels')),
                               Item('monitor_sample_name', editor=EnumEditor(name='samples')),
                               width=300,
                               title='Select Irradiation and Level')
        return v


class FindFluxMonitorsNode(BaseFindFluxNode):
    name = 'Find Flux Monitors'

    use_browser = Bool(False)

    def run(self, state):
        if not self.irradiation or not self.level:
            self.configure()

        if not self.irradiation or not self.level:
            state.veto = self
        else:
            dvc = self.dvc
            args = dvc.get_irradiation_geometry(self.irradiation, self.level)
            if args:
                geom, holder = args
                state.geometry = geom
                state.holder = holder

            ips = dvc.get_unknown_positions(self.irradiation, self.level, self.monitor_sample_name)

            fluxes = dvc.get_flux_positions(self.irradiation, self.level)
            state.unknown_positions = [self._fp_factory(state.geometry, self.irradiation, self.level,
                                                        ip.identifier, ip.sample.name, ip.position, fluxes)
                                       for ip in ips if ip.identifier]

            if self.use_browser:
                is_append, monitors = self.get_browser_analyses(irradiation=self.irradiation,
                                                                level=self.level)
            else:
                monitors = self.dvc.find_flux_monitors(self.irradiation, self.level, self.monitor_sample_name)

            state.unknowns = monitors

            state.irradiation = self.irradiation
            state.level = self.level

    def _load_hook(self, nodedict):
        self.level = nodedict.get('level', '')

    def _to_template(self, d):
        super(FindFluxMonitorsNode, self)._to_template(d)
        d['level'] = self.level

    def traits_view(self):
        v = self._view_factory(Item('irradiation', editor=EnumEditor(name='irradiations')),
                               Item('level', editor=EnumEditor(name='levels')),
                               Item('monitor_sample_name', editor=EnumEditor(name='samples')),
                               Item('use_browser'),
                               width=300,
                               title='Select Irradiation and Level')
        return v


class FindReferencesNode(FindNode):
    user_choice = False
    threshold = Float

    load_name = Str

    display_loads = Property(depends_on='limit_to_analysis_loads')
    loads = List
    analysis_loads = List
    limit_to_analysis_loads = Bool(True)

    threshold_enabled = Property

    analysis_types = List
    available_analysis_types = List

    extract_device = Str
    enable_extract_device = Bool
    extract_devices = List

    mass_spectrometer = Str
    enable_mass_spectrometer = Bool
    mass_spectrometers = List
    use_graphical_filter = Bool

    def reset(self):
        self.user_choice = None
        super(FindReferencesNode, self).reset()

    def load(self, nodedict):
        self.threshold = nodedict.get('threshold', 10)
        self.analysis_types = nodedict.get('analysis_types', [])
        self.name = nodedict.get('name', 'Find References')
        self.limit_to_analysis_loads = nodedict.get('limit_to_analysis_loads', True)
        self.use_graphical_filter = nodedict.get('use_graphical_filter', True)

    def finish_load(self):
        self.extract_devices = self.dvc.get_extraction_device_names()
        self.mass_spectrometers = self.dvc.get_mass_spectrometer_names()
        names = [NULL_STR]
        dbnames = self.dvc.get_load_names()
        if dbnames:
            names += dbnames

        self.loads = names

    def _to_template(self, d):
        d = dict()
        for key in ('threshold', 'analysis_types', 'limit_to_analysis_loads', 'use_graphical_filter'):
            d[key] = getattr(self, key)

    def pre_run(self, state, configure=True):
        if not state.unknowns:
            return

        eds = {ai.extract_device for ai in state.unknowns}
        self.enable_extract_device = len(eds) > 1
        self.extract_device = list(eds)[0]

        ms = {ai.mass_spectrometer for ai in state.unknowns}
        self.enable_mass_spectrometer = len(ms) > 1
        self.mass_spectrometer = list(ms)[0]

        ls = {ai.load_name for ai in state.unknowns}
        self.analysis_loads = [NULL_STR] + list(ls)

        return super(FindReferencesNode, self).pre_run(state, configure=configure)

    def run(self, state):
        for gid, ans in groupby_group_id(state.unknowns):
            if self._run_group(state, gid, list(ans)):
                return

        compress_groups(state.unknowns)
        compress_groups(state.references)

    def _run_group(self, state, gid, unknowns):
        atypes = [ai.lower().replace(' ', '_') for ai in self.analysis_types]
        kw = dict(extract_devices=self.extract_device,
                  mass_spectrometers=self.mass_spectrometer,
                  make_records=False)

        while 1:
            if self.load_name and self.load_name != NULL_STR:
                refs = self.dvc.find_references_by_load(self.load_name, atypes, **kw)
                if refs:
                    times = sorted([ai.rundate for ai in refs])
            else:
                times = sorted([ai.rundate for ai in unknowns])
                refs = self.dvc.find_references(times, atypes, hours=self.threshold, **kw)

            if not refs:
                if confirm(None, 'No References Found. Would you like to try different search criteria?') == YES:
                    if self.configure():
                        continue
                    else:
                        state.canceled = True
                        return True
                else:
                    if not confirm(None, 'Would you like to search manually?') == YES:
                        state.canceled = True
                    return True
            else:
                break

        if refs:
            if self.use_graphical_filter:
                unknowns.extend(refs)
                model = GraphicalFilterModel(analyses=unknowns,
                                             dvc=self.dvc,
                                             extract_device=self.extract_device,
                                             mass_spectrometer=self.mass_spectrometer,
                                             low_post=times[0],
                                             high_post=times[-1],
                                             threshold=self.threshold,
                                             gid=gid)

                model.setup()
                model.analysis_types = self.analysis_types

                obj = GraphicalFilterView(model=model)
                info = obj.edit_traits(kind='livemodal')
                if info.result:
                    refs = model.get_filtered_selection()
                else:
                    refs = None
                    state.veto = self

            if refs:
                refs = self.dvc.make_analyses(refs)
                state.references = list(refs)
                return True

    def traits_view(self):

        load_grp = BorderHGroup(UItem('load_name', editor=EnumEditor(name='display_loads')),
                                Item('limit_to_analysis_loads',
                                     tooltip='Limit Loads based on the selected analyses',
                                     label='Limit Loads by Analyses'),
                                label='Load')
        inst_grp = BorderVGroup(Item('extract_device',
                                     enabled_when='enable_extract_device',
                                     editor=EnumEditor(name='extract_devices'),
                                     label='Extract Device'),
                                Item('mass_spectrometer',
                                     label='Mass Spectrometer',
                                     enabled_when='enable_mass_spectrometer',
                                     editor=EnumEditor(name='mass_spectrometers')),
                                label='Instruments')

        filter_grp = BorderVGroup(Item('threshold',
                                       tooltip='Maximum difference between references and unknowns in hours',
                                       enabled_when='threshold_enabled',
                                       label='Threshold (Hrs)'),
                                  Item('use_graphical_filter', label='Graphical Selection'),
                                  VGroup(UItem('analysis_types',
                                               style='custom',
                                               editor=CheckListEditor(name='available_analysis_types', cols=2)),
                                         show_border=True, label='Analysis Types'),
                                  label='Filtering')

        v = self._view_factory(VGroup(load_grp,
                                      filter_grp,
                                      inst_grp))

        return v

    def _available_analysis_types_default(self):
        return [(b, b) for b in REFERENCE_ANALYSIS_TYPES]

    def _get_display_loads(self):
        if self.limit_to_analysis_loads:
            return self.analysis_loads
        else:
            return self.loads

    def _get_threshold_enabled(self):
        return not self.load_name or self.load_name == NULL_STR


class FindBlanksNode(FindReferencesNode):
    def _available_analysis_types_default(self):
        return [(b, b) for b in BLANKS]

# ============= EOF =============================================
