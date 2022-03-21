from SpiffWorkflow.specs import *
from SpiffWorkflow import Workflow


spec = WorkflowSpec()

wf = Workflow(spec)
wf.complete_task_from_id(...)

