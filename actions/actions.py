#!/usr/bin/env python3
#
# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import subprocess

sys.path.append('hooks/')

from charmhelpers.core.hookenv import (
    action_fail,
    action_get,
)
from cinder_utils import (
    pause_unit_helper,
    resume_unit_helper,
    register_configs,
)
# import cinder_manage


def pause(args):
    """Pause the Ceilometer services.
    @raises Exception should the service fail to stop.
    """
    pause_unit_helper(register_configs())


def resume(args):
    """Resume the Ceilometer services.
    @raises Exception should the service fail to start."""
    resume_unit_helper(register_configs())


def remove_services(args):
    """Remove unused services entities from the database after enabling HA
    with a stateless backend such as cinder-ceph
    Calls cinder_manage.py python2 script with that function name.
    The call is checked with subprocess.
    """
    host = "host={}".format(action_get(key="host"))
    script = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'cinder_manage.py'))
    cmd = [script, "remove_services", host]
    cmd.extend(args)
    subprocess.check_call(cmd)


def rename_volume_host(args):
    """Update the host attribute of volumes from currenthost to newhost
    Calls cinder_manage.py python2 script with that function name.
    The call is checked with subprocess.
    """
    script = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'cinder_manage.py'))
    cmd = [script, "rename_volume_host"]
    cmd.extend(args)
    subprocess.check_call(cmd)


def volume_host_add_driver(args):
    """Rename the volume hostUpdate the os-vol-host-attr:host volume attribute
    to include driver and volume name. Used for migrating volumes to
    multi-backend and Ocata+ configurtation.
    Calls cinder_manage.py python2 script with that function name.
    The call is checked with subprocess.
    """
    script = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'cinder_manage.py'))
    cmd = [script, "volume_host_add_driver"]
    cmd.extend(args)
    subprocess.check_call(cmd)


# A dictionary of all the defined actions to callables (which take
# parsed arguments).
ACTIONS = {
    "pause": pause,
    "resume": resume,
    "remove-services": remove_services,
    "rename-volume-host": rename_volume_host,
    "volume-host-add-driver": volume_host_add_driver,
}


def main(args):
    action_name = os.path.basename(args[0])
    try:
        action = ACTIONS[action_name]
    except KeyError:
        return "Action %s undefined" % action_name
    else:
        try:
            action(args)
        except Exception as e:
            action_fail(str(e))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
