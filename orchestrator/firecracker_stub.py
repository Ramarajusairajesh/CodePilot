import logging

def launch_vm(image, job_id, task):
    logging.info(f"Launching Firecracker VM: image={image}, job_id={job_id}, task={task}")
    # TODO: Integrate with Firecracker CLI
    return f"vm-{job_id}"

def terminate_vm(vm_id):
    logging.info(f"Terminating Firecracker VM: {vm_id}")
    # TODO: Integrate with Firecracker CLI
    return True 