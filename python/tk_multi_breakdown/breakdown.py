# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import urlparse
import os
import urllib
import shutil
import sys
import tank

from tank import TankError

# cache the publish data we pull down from shotgun for performance
g_cached_sg_publish_data = {}

# the template key we use to find the version number
VERSION_KEY = "version"

def get_breakdown_items():
    """
    Analyzes the scene (by running a hook) and returns a list of items 
    in the scene which are applicable for the breakdown. These items all
    match some template inside toolkit and have a concept of a version field.
    
    The file paths detected are also checked against shotgun, and in the case
    a match is found in shotgun (in the form of a publish record), metadata for
    this shotgun object is downloaded and returned. This method will send a single 
    query to shotgun to retrieve this. 
    
    A list of dictionaries are returned. Each dictionary will have the following keys: 
    
    {'fields':       # resolved template fields
     'node_name':    # the name of the object detected (returned by the hook)
     'node_type':    # the type of the object detected (returned by the hook)
     'path':         # pull path to the items
     'sg_data':      # shotgun publish data if applicable (None otherwise)
     'template':     # template object representing the path
     }
 
    The node type and node name are generated by the hook and are specific to the DCC. These are passed
    back to the update hook when an update is due so that the update hook can identify which item to update. 
 
    Here is an example of what the return data typically looks like:
 
    {'fields': {'Sequence': 'aaa',
                'Shot': 'aaa_00010',
                'Step': 'Comp',
                'eye': '%V',
                'height': 1556,
                'name': 'test',
                'output': 'output',
                'version': 1,
                'width': 2048},
     'node_name': 'Read2',
     'node_type': 'Read',
     'path': u'/mnt/projects/climp/sequences/aaa/aaa_00010/Comp/publish/elements/test/v001/2048x1556/aaa_00010_test_output_v001.%04d.dpx',
     'sg_data': {'code': 'aaa_00010_test_output_v001.%04d.dpx',
                 'entity': {'id': 1660, 'name': 'aaa_00010', 'type': 'Shot'},
                 'entity.Asset.sg_asset_type': None,
                 'id': 1424,
                 'image': 'https://....',
                 'name': 'test',
                 'published_file_type': {'id': 3,
                                         'name': 'Rendered Image',
                                         'type': 'PublishedFileType'},
                 'task': {'id': 4714, 'name': 'Comp', 'type': 'Task'},
                 'type': 'PublishedFile',
                 'project': {'id': 234, 'name': 'Climp', 'type': 'Project'},
                 'version_number': 1},
     'template': <Sgtk TemplatePath nuke_shot_render_pub_mono_dpx>}
     
    :returns: See details above.
    """
    global g_cached_sg_publish_data
    items = []

    # perform the scene scanning in the main UI thread - a lot of apps are sensitive to these
    # types of operations happening in other threads.
    app = tank.platform.current_bundle()
    scene_objects = app.engine.execute_in_main_thread(app.execute_hook_method, "hook_scene_operations", "scan_scene")
    # returns a list of dictionaries, each dict being like this:
    # {"node": node_name, "type": "reference", "path": maya_path}


    for scene_object in scene_objects:

        node_name = scene_object.get("node")
        node_type = scene_object.get("type")
        file_name = scene_object.get("path").replace("/", os.path.sep)

        # see if this read node matches any path in the templates setup
        matching_template = app.tank.template_from_path(file_name)

        if matching_template:

            # see if we have a version number
            fields = matching_template.get_fields(file_name)
            if VERSION_KEY in fields:

                # now the fields are the raw breakdown of the path in the read node.
                # could be bla.left.0002.exr, bla.%V.####.exr etc
                
                # remove all abstract fields from keys so that the default value will get used
                # when building a path from the template.  This is consistent with the utility
                # method 'register_publish'
                for key_name, key in matching_template.keys.iteritems():
                    if key_name in fields and key.is_abstract:
                        del(fields[key_name])

                # we also want to normalize the eye field (this should probably be an abstract field!)
                # note: we need to do this explicitly because the eye isn't abstract in the default 
                # configs yet (which is incorrect!).
                fields["eye"] = "%V"
                
                # now build the normalized path that we can use to find corresponding Shotgun published files
                normalized_path = matching_template.apply_fields(fields)
                
                item = {}
                item["path"] = normalized_path
                item["node_name"] = node_name
                item["node_type"] = node_type
                item["template"] = matching_template
                item["fields"] = fields
                item["sg_data"] = None


                # store the normalized fields in dict
                items.append(item)

    # now now do a second pass on all the files that are valid to see if they are published
    # note that we store (by convention) all things on a normalized sequence form in SG, e.g
    # all four-padded sequences are stored as '%04d' regardless if they have been published from
    # houdini, maya, nuke etc.
    valid_paths = [ x.get("path") for x in items ]

    # check if we have the path in the cache
    paths_to_fetch = []
    for p in valid_paths:
        if p not in g_cached_sg_publish_data:
            paths_to_fetch.append(p)
        else:
            # use cache data!
            for item in items:
                if item.get("path") == p:
                    item["sg_data"] = g_cached_sg_publish_data[p]


    fields = ["entity",
              "entity.Asset.sg_asset_type", # grab asset type if it is an asset
              "code",
              "image",
              "name",
              "task",
              "version_number",
              "project"
              ]

    if tank.util.get_published_file_entity_type(app.tank) == "PublishedFile":
        fields.append("published_file_type")
    else:# == "TankPublishedFile"
        fields.append("tank_type")

    sg_data = tank.util.find_publish(app.tank, paths_to_fetch, fields=fields)

    # process and cache shotgun items
    for (path, sg_chunk) in sg_data.items():
        # cache item
        g_cached_sg_publish_data[path] = sg_chunk

        # change type from valid -> publish
        for item in items:
            if item.get("path") == path:
                item["sg_data"] = sg_chunk

    return items


def calculate_latest_version(template, curr_fields):
    """
    Given a template and some fields, return the highest version number found on disk.
    The template key containing the version number is assumed to be named {version}.
    
    This will perform a scan on disk to determine the highest version.
    
    :param template: Template object to calculate for
    :param curr_fields: A complete set of fields for the template
    :returns: The highest version number found
    """
    # set up the payload
    output = {}

    # calculate visibility
    # check if this is the latest item

    # note - have to do some tricks here to get sequences and stereo working
    # need to fix this in Tank platform

    # get all eyes, all frames and all versions
    # potentially a HUGE glob, so may be really SUPER SLOW...
    # todo: better support for sequence iterations
    
    # first, find all abstract (Sequence) keys from the template:
    abstract_keys = set()
    for key_name, key in template.keys.iteritems():
        if key.is_abstract:
            abstract_keys.add(key_name)

    # skip keys are all abstract keys + 'version' & 'eye'
    skip_keys = [k for k in abstract_keys] + [VERSION_KEY, "eye"]

    # then find all files, skipping these keys
    app = tank.platform.current_bundle()
    all_versions = app.tank.paths_from_template(template, curr_fields, skip_keys=skip_keys)

    # if we didn't find anything then something has gone wrong with our 
    # logic as we should have at least one file so error out:
    # TODO - this should be handled more cleanly!
    if not all_versions:
        raise TankError("Failed to find any files!")        
    
    # now look for the highest version number...
    highest_version = 0
    for ver in all_versions:
        curr_fields = template.get_fields(ver)
        if curr_fields[VERSION_KEY] > highest_version:
            highest_version = curr_fields[VERSION_KEY]

    return highest_version
    
