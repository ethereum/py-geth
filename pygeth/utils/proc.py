import time
import signal

import gevent


def wait_for_popen(proc, max_wait=5):
    wait_till = time.time() + 5
    while proc.poll() is None and time.time() < wait_till:
        gevent.sleep(0.1)


def kill_proc(proc):
    try:
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            wait_for_popen(proc, 5)
        if proc.poll() is None:
            proc.terminate()
            wait_for_popen(proc, 2)
        if proc.poll() is None:
            proc.kill()
            wait_for_popen(proc, 1)
    except KeyboardInterrupt:
        proc.kill()


def format_error_message(prefix, command, return_code, stdoutdata, stderrdata):
    lines = [prefix]

    lines.append("Command    : {0}".format(' '.join(command)))
    lines.append("Return Code: {0}".format(return_code))

    if stdoutdata:
        lines.append("stdout:\n`{0}`".format(stdoutdata))
    else:
        lines.append("stdout: N/A")

    if stderrdata:
        lines.append("stderr:\n`{0}`".format(stderrdata))
    else:
        lines.append("stderr: N/A")

    return "\n".join(lines)
