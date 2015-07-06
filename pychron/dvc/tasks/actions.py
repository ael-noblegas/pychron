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
# ============= standard library imports ========================
# ============= local library imports  ==========================
from pyface.tasks.action.task_action import TaskAction

from pychron.envisage.resources import icon


class LocalRepositoryAction(TaskAction):
    enabled_name = 'selected_local_repository_name'


class RemoteRepositoryAction(TaskAction):
    enabled_name = 'selected_repository_name'


class CloneAction(RemoteRepositoryAction):
    method = 'clone'
    name = 'Clone'


class AddBranchAction(LocalRepositoryAction):
    name = 'Add Branch'
    method = 'add_branch'
    image = icon('add')


class CheckoutBranchAction(LocalRepositoryAction):
    name = 'Checkout Branch'
    method = 'checkout_branch'
    image = icon('checkout')


class PushAction(LocalRepositoryAction):
    name = 'Push'
    method = 'push'
    image = icon('arrow_up')
# ============= EOF =============================================
