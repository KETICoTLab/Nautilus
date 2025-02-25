import os
from nvflare.fuel.flare_api import new_secure_session
from nvflare.fuel.flare_api import Session
import json

def display_help():
    """
    세션 관련 함수 도움말 표출 -> 한국어 지원을 안하는 경우를 대비해서 영어로 작성
    """
    help_text = """
    ### Help Guide for Session and Job Management ###

    1. **create_session(admin, admin_dir)**:
       - Creates a new secure session for the admin user.
       - Parameters:
         - admin (str): Username for the session.
         - admin_dir (str): Path to the directory where admin data is stored.
       - Returns:
         - sess (Session): A secure session object.

       Example:
       >>> session = create_session("admin", "/path/to/admin_dir")

    2. **sess_system_info(sess)**:
       - Retrieves system information for the given session.
       - Parameters:
         - sess (Session): The session object.
       - Returns:
         - System information (dict or string).

       Example:
       >>> info = sess_system_info(session)
       >>> print(info)

    3. **submit_job(sess, job_path)**:
       - Submits a job using the given session.
       - Parameters:
         - sess (Session): The session object.
         - job_path (str): Path to the job file.
       - Returns:
         - job_id (str): ID of the submitted job.

       Example:
       >>> job_id = submit_job(session, "/path/to/job")

    4. **job_cb(session, job_id, job_meta, *cb_args, **cb_kwargs)**:
       - Callback function for job monitoring. Prints job status and metadata.
       - Parameters:
         - session (Session): The session object.
         - job_id (str): ID of the job.
         - job_meta (dict): Metadata of the job.
         - cb_args, cb_kwargs: Additional arguments for callbacks.
       - Returns:
         - (bool): Always True.

    5. **job_monitor(sess, job_id)**:
       - Monitors the status of a job using the provided session.
       - Parameters:
         - sess (Session): The session object.
         - job_id (str): ID of the job.

       Example:
       >>> job_monitor(session, job_id)

    6. **print_job_info(sess)**:
       - Prints a formatted JSON output of all jobs in the session.
       - Parameters:
         - sess (Session): The session object.

       Example:
       >>> print_job_info(session)

    7. **job_abort(sess, job_id)**:
       - Aborts a running job.
       - Parameters:
         - sess (Session): The session object.
         - job_id (str): ID of the job.

       Example:
       >>> job_abort(session, job_id)

    8. **job_delete(sess, job_id)**:
       - Deletes a job from the session.
       - Parameters:
         - sess (Session): The session object.
         - job_id (str): ID of the job.

       Example:
       >>> job_delete(session, job_id)

    9. **job_download(sess, job_id)**:
       - Downloads the result of a job.
       - Parameters:
         - sess (Session): The session object.
         - job_id (str): ID of the job.

       Example:
       >>> job_download(session, job_id)

    10. **job_clone(sess, job_id)**:
        - Clones an existing job.
        - Parameters:
          - sess (Session): The session object.
          - job_id (str): ID of the job.

        Example:
        >>> job_clone(session, job_id)
    """
    print(help_text)



#새로운 세션 생성
def create_session(admin, admin_dir):
    username = admin
    admin_user_dir = os.path.join(admin_dir, username)
    sess = new_secure_session(
        username=username,
        startup_kit_location = admin_user_dir
    )
    return sess

#세션 정보 출력
def sess_system_info(sess):
    return sess.get_system_info()

#job_id = '7f0753df-4bcc-4576-b3ab-2756819d88ca'
def submit_job(sess, job_path):
    path_to_example_job = job_path
    job_id = sess.submit_job()
    print(job_id + " was submitted")
    return job_id
#sess = create_session()
#submit_job(sess, "/tmp/nvflare/jobs/job_config/cifar10_fedavg")

def job_cb(
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

def job_monitor(sess, job_id):
    sess.monitor_job(job_id, cb=job_cb, cb_run_counter={"count":0})


def print_job_info(sess):
    def format_json( data: dict):
        print(json.dumps(data, sort_keys=True, indent=4,separators=(',', ': ')))
    
    list_jobs_output = sess.list_jobs()
    format_json(list_jobs_output)

def job_abort(sess, job_id):
    sess.abort_job(job_id)

def job_delete(sess, job_id):
    sess.delete_job(job_id)

def job_download(sess, job_id):
    sess.download_job_result(job_id)

def job_clone(sess, job_id):
    sess.clone_job(job_id)

