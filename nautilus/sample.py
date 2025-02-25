import os
from nvflare.fuel.flare_api.flare_api import new_secure_session
from nvflare.fuel.flare_api.flare_api import Session
import json

username = "admin@nvidia.com"
admin_user_dir = os.path.join("/workspace/NVFlare/examples/advanced/docker/workspace/example_docker_project/prod_00", username)
sess = new_secure_session(
    username=username,
    startup_kit_location=admin_user_dir
)
print(sess.get_system_info())

path_to_example_job = "/workspace/NVFlare/examples/advanced/job_api/pt/jobs/job_config/cifar10_fedavg"
job_id = sess.submit_job(path_to_example_job)
#print(job_id + " was submitted")
#job_id = '7f0753df-4bcc-4576-b3ab-2756819d88ca'
def sample_cb(
        session: Session, job_id: str, job_meta, *cb_args, **cb_kwargs
    ) -> bool:
    if job_meta["status"] == "RUNNING":
        if cb_kwargs["cb_run_counter"]["count"] < 3:
            print(job_meta)
            print(cb_kwargs["cb_run_counter"])
        else:
            print(".", end="")
    else:
        print("\n" + str(job_meta))

    cb_kwargs["cb_run_counter"]["count"] += 1
    return True

#sess.monitor_job(job_id, cb=sample_cb, cb_run_counter={"count":0})

def format_json( data: dict):
    print(json.dumps(data, sort_keys=True, indent=4,separators=(',', ': ')))

list_jobs_output = sess.list_jobs()
print(format_json(list_jobs_output))

#sess.abort_job(job_id)
#sess.delete_job(job_id)
