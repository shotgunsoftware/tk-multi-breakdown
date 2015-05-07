# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

import sys
import os
import shutil
import tempfile

from tank_test.tank_test_base import *
import tank
from tank.errors import TankError
from tank.platform import application
from tank.platform import constants
from tank.template import Template
from tank.deploy import descriptor


class TestApplication(TankTestBase):
    
    def setUp(self):
        super(TestApplication, self).setUp()
        self.setup_fixtures()
        
        # set up a sequence/shot/step
        # and run folder creation
        self.seq = {"type": "Sequence",
                    "id": 2,
                    "code": "seq_code",
                    "project": self.project}
        self.shot = {"type": "Shot",
                     "id": 1,
                     "code": "shot_code",
                     "sg_sequence": self.seq,
                     "project": self.project}
        self.step = {"type": "Step",
                     "id": 3,
                     "code": "step_code",
                     "entity_type": "Shot",
                     "short_name": "step_short_name"}
        self.task = {"type": "Task",
                     "id": 23,
                     "entity": self.shot,
                     "step": self.step,
                     "project": self.project}

        entities = [self.shot, self.seq, self.step, self.project, self.task]

        # set up a path to this app 
        os.environ["APP_PATH"] = os.path.abspath(os.path.join( os.path.dirname(__file__), ".."))

        # Add these to mocked shotgun
        self.add_to_sg_mock_db(entities)

        # run folder creation
        self.tk.create_filesystem_structure(self.shot["type"], self.shot["id"])
        
        # now make a context
        context = self.tk.context_from_entity(self.shot["type"], self.shot["id"])
        
        # and start the engine
        self.engine = tank.platform.start_engine("test_engine", self.tk, context)

        
    def tearDown(self):
                
        # engine is held as global, so must be destroyed.
        cur_engine = tank.platform.current_engine()
        if cur_engine:
            cur_engine.destroy()
        
        # important to call base class so it can clean up memory
        super(TestApplication, self).tearDown()

    
    
class TestApi(TestApplication):

    def setUp(self):
        super(TestApi, self).setUp()
        self.app = self.engine.apps["tk-multi-breakdown"]
        
    def test_get_setting(self):
        # Test that app is able to locate a template based on the template name
        tmpl = self.app.get_template("test_template")
        self.assertEqual("maya_publish_name", tmpl.name)
        self.assertIsInstance(tmpl, Template)
        
        # test resource
    
