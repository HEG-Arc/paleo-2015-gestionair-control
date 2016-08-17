import subprocess
from pycall import CallFile, Call, Context
from pycall import ValidationError

from messaging import send_amqp_message

def call_phone_number(phone_number, wait, extension, context_name):
    #TODO maybe use ARI instead?
    call = Call('SIP/%s' % phone_number, wait_time=wait, retry_time=1, max_retries=1)
    context = Context(context_name, str(extension), '1')
    try:
        cf = CallFile(call, context)
        cf.spool()
    except ValidationError:
        print "asterisk CallFile error"

    send_amqp_message({'type': 'PHONE_RINGING', 'number': int(phone_number)}, "simulation")
    subprocess.Popen('/usr/bin/sudo chmod 660 /var/spool/asterisk/outgoing/*.call && /usr/bin/sudo chown asterisk:asterisk /var/spool/asterisk/outgoing/*.call', shell=True)
