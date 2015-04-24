# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
A breakdown app which shows what in the scene is out of date.
"""

from tank.platform import Application

import sys
import os

class MultiBreakdown(Application):

    def init_app(self):
        """
        Called as the application is being initialized
        """
        tk_multi_breakdown = self.import_module("tk_multi_breakdown")
        cb = lambda : tk_multi_breakdown.show_dialog(self)
        self.engine.register_command("Scene Breakdown...", cb, { "short_name": "breakdown" })


    def show_breakdown_dialog(self):
        """
        Show the breakdown UI as a dialog.
        
        This is a helper method to make it easy to programatically access the breakdown UI.
        External code could then do something like:
        
        >>> import sgtk
        >>> e = sgtk.platform.current_engine()
        >>> e.apps["tk-multi-breakdown"].show_breakdown_dialog()
        """        
        tk_multi_breakdown = self.import_module("tk_multi_breakdown")
        fn = lambda : tk_multi_breakdown.show_dialog(self)
        self.engine.execute_in_main_thread(fn)
        
        
    def analyze_scene(self):
        """
        Runs the scene analysis and returns a list of scene items.
        
        Each item is represented by a dictionary with a number of keys to 
        describe the item. This method uses the same logic that the main UI
        uses to determine the list of files.
        
        Only files whose path corresponds to a template in the toolkit templates
        file will be detected. Files do not need to exist as publishes in Shotgun
        however if they do, this method will return basic Shotgun publish metadata
        for them.
        
        The two keys node_name and node_type are used to return a DCC-centric 
        "address" or representation which makes it possible to identify the path
        within the DCC. In for example Maya and Nuke, this will return the 
        node name and type. The logic for this is implemented in the hooks and 
        will vary between DCCs.
        
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
                     'id': 1424,
                     'name': 'test',
                     'published_file_type': {'id': 3,
                                             'name': 'Rendered Image',
                                             'type': 'PublishedFileType'},
                     'task': {'id': 4714, 'name': 'Comp', 'type': 'Task'},
                     'type': 'PublishedFile',
                     'project': {'id': 234, 'name': 'Climp', 'type': 'Project'},
                     'version_number': 1},
         'template': <Sgtk TemplatePath nuke_shot_render_pub_mono_dpx>}
        
        This method will attempt to connect to shotgun, but the number of calls made are
        constant and independent of the scene complexity.
        
        You typically use it like this:
        
        >>> import sgtk
        >>> e = sgtk.platform.current_engine()
        >>> items = e.apps["tk-multi-breakdown"].analyze_scene()
        
        :returns: List of dictionaries, see above for example.
        """
        tk_multi_breakdown = self.import_module("tk_multi_breakdown")
        
        # first, scan the scene and get a list of items
        items = tk_multi_breakdown.get_breakdown_items()
        
        # if shotgun data is returned for an item, trim this down
        # to return a more basic listing than the one returned
        # from get_breakdown_items:
        for i in items:
            if i["sg_data"]:
                new_sg_data = {}
                new_sg_data["id"] = i["sg_data"]["id"]
                new_sg_data["type"] = i["sg_data"]["type"]
                new_sg_data["code"] = i["sg_data"]["code"]
                new_sg_data["entity"] = i["sg_data"]["entity"]
                new_sg_data["task"] = i["sg_data"]["task"]
                new_sg_data["published_file_type"] = i["sg_data"]["published_file_type"]
                new_sg_data["name"] = i["sg_data"]["name"]
                new_sg_data["project"] = i["sg_data"]["project"]
                new_sg_data["version_number"] = i["sg_data"]["version_number"]
                i["sg_data"] = new_sg_data
                
        return items

    def calculate_latest_version(self, template, fields):
        """
        Given a template and some fields, return the highest version number found on disk.
        The template key containing the version number is assumed to be named {version}.
        
        This will perform a scan on disk to determine the highest version.
        
        You typically use this in conjunction with the analyze_scene() method. 
        For example:
        
        import sgtk
        e = sgtk.platform.current_engine()
        breakdown_app = e.apps["tk-multi-breakdown"]
        
        # get list of breakdown items
        items = breakdown_app.analyze_scene()
        
        # now loop over all items
        for i in items:
        
            # get the latest version on disk
            latest_version = breakdown_app.calculate_latest_version(i["template"], i["fields"])
            
            # if our current version is out of date, update it!
            current_version = i["version"]
            if latest_version > current_version:
                
                # make a fields dictionary representing the latest version
                latest_fields = copy.copy(i["fields"])
                latest_fields["version"] = latest_version
                
                # request that the breakdown updates to the latest version
                breakdown_app.update_item(i["node_type"], i["node_name"], i["template"], latest_fields)
         
        :param template: Template object to calculate for
        :param curr_fields: A complete set of fields for the template
        :returns: The highest version number found
        """
        return tk_multi_breakdown.calculate_latest_version(template, fields)
        
    def update_item(self, node_type, node_name, template, fields):
        """
        Request that the breakdown updates an given node with a new version.
        This is similar to running the update in the breakdown UI. The actual 
        update call will be dispatched to a hook which handles the DCC specific logic.
        
        You typically use this in conjunction with the analyze_scene() method. 
        For example:
        
        import sgtk
        e = sgtk.platform.current_engine()
        breakdown_app = e.apps["tk-multi-breakdown"]
        
        # get list of breakdown items
        items = breakdown_app.analyze_scene()
        
        # now loop over all items
        for i in items:
        
            # get the latest version on disk
            latest_version = breakdown_app.calculate_latest_version(i["template"], i["fields"])
            
            # if our current version is out of date, update it!
            current_version = i["version"]
            if latest_version > current_version:
                
                # make a fields dictionary representing the latest version
                latest_fields = copy.copy(i["fields"])
                latest_fields["version"] = latest_version
                
                # request that the breakdown updates to the latest version
                breakdown_app.update_item(i["node_type"], i["node_name"], i["template"], latest_fields)
        
        :param node_type: Note type of the item to update, as returned by analyze_scene()
        :param node_name: Note name of the item to update, as returned by analyze_scene()
        :param template: Template object representing the path pattern to update
        :param fields: Fields dictionary representing the values to apply to the template in order
                       to render an valid and existing path on disk that the system can update to.
        """
        d = {}
        d["node"] = node_name
        d["type"] = node_type
        d["path"] = template.apply_fields(fields)
        
        # call out to hook
        return self._app.execute_hook_method("hook_scene_operations", "update", items=[d])



