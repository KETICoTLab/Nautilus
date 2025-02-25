import os
from nvflare.fuel.flare_api.flare_api import new_secure_session
from nvflare.fuel.flare_api.flare_api import Session
import json
from nvflare.fuel.flare_api.flare_api import Session, basic_cb_with_print



username = "admin@nvidia.com"
admin_user_dir = os.path.join("/workspace/NVFlare/examples/advanced/docker/workspace/example_docker_project/prod_00", username)
sess = new_secure_session(
    username=username,
    startup_kit_location=admin_user_dir
)
print(sess.get_system_info())

path_to_example_job = "/workspace/NVFlare/examples/hello-world/hello-numpy-sag/jobs/hello-numpy-sag"
job_id = sess.submit_job(path_to_example_job)
print(job_id + " was submitted")

sess.monitor_job(job_id, cb=basic_cb_with_print, cb_run_counter={"count":0})

print(sess.api.do_command("shutdown client"))
print(sess.api.do_command("shutdown server"))

sess.close()

