
import os
import shutil
import traceback
from typing import List

from .constants import ProvisionMode, WorkDir
from .ctx import ProvisionContext
from .entity import Project
from .spec import Builder


class Provisioner:
    def __init__(self, root_dir: str, builders: List[Builder]):
        self.root_dir = root_dir
        self.builders = builders
        self.template = {}

    def add_template(self, template: dict):
        if not isinstance(template, dict):
            raise ValueError(f"template must be a dict but got {type(template)}")
        self.template.update(template)

    def provision(self, project: Project, mode=None):
        server = project.get_server()
        if not server:
            raise RuntimeError("missing server from the project")

        workspace_root_dir = os.path.join(self.root_dir, project.name)
        ctx = ProvisionContext(workspace_root_dir, project)
        if self.template:
            ctx.set_template(self.template)

        if not mode:
            mode = ProvisionMode.NORMAL
        ctx.set_provision_mode(mode)

        try:
            for b in self.builders:
                b.initialize(project, ctx)

            # call builders!
            for b in self.builders:
                b.build(project, ctx)

            for b in self.builders[::-1]:
                b.finalize(project, ctx)

        except Exception:
            prod_dir = ctx.get(WorkDir.CURRENT_PROD_DIR)
            if prod_dir:
                shutil.rmtree(prod_dir)
            print("Exception raised during provision.  Incomplete prod_n folder removed.")
            traceback.print_exc()
        finally:
            wip_dir = ctx.get(WorkDir.WIP)
            if wip_dir:
                shutil.rmtree(wip_dir)
        return ctx
