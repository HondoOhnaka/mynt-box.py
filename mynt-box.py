import os, shutil, datetime, time, sys
from datetime import datetime
from oauth import oauth
from dropbox import client, rest, session
import oauth.oauth as oauth
from datetime import datetime, timedelta

import subprocess

debug = False

APP_KEY = '<YOUR DROPBOX KEY>'
APP_SECRET = '<YOUR DROPBOX SECRET KEY>'

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'

# time in minutes that we should compare against last modified of file
# convenience to not redownload unmodified file
# if you are running via cron, this should probably be set to the time interval 
# between runs
TIME_INTERVAL = 5 # minutes

# seems to be some weirdness with local and server timezones
# not sure how else to do these at the moment
# need to handle local within the script.
# not sure how to deal with server time zone other than setting
# a hardcoded value, which seems lame - todo fix
TZ_OFFSET = 6 
SERVER_TZ_OFFSET = 0

sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
dir_sep = "/"

if os.path.exists("access_token.txt"):
    s = file("access_token.txt").read()
    t = oauth.OAuthToken.from_string(s)
    sess.set_token(t.key, t.secret)
else:
    request_token = sess.obtain_request_token()
    url = sess.build_authorize_url(request_token)
    print "AUTH URL:", url 
    print "GO THERE AND HIT ENTER AFTER APPROVING..."
    raw_input()
    access_token = sess.obtain_access_token(request_token)
    file("access_token.txt", "w").write(str(access_token))
    
db_client = client.DropboxClient(sess)

def changed_since_last(file=None, minutes_since_updated=TIME_INTERVAL):
    """
    check the last modified time of a dropbox file object 
    and compare it to the current time. If it is has changed in the last
    minutes_since_updated range, return True
    else return False
    """
    if not file:
        print "Oops, you need to pass a file to me"
        return False
        
    if debug:
        print file['path'][ file["path"].rindex('/')+1 : ]

    file_time = datetime.strptime(file['modified'], "%a, %d %b %Y %H:%M:%S +0000")
    curr_time = datetime.now() + timedelta(hours=SERVER_TZ_OFFSET)
    
    if debug:
        print file['modified']
        print "file last modified at: ", file_time - timedelta(hours=6)
        print "                  now: ", curr_time
    
    return (file_time - timedelta(hours=TZ_OFFSET)) > (curr_time - timedelta(minutes=TIME_INTERVAL))
    

def get_files(remote_dir, local_dir, full_overwrite=False):
    """
    Worker to get remote file and copy it to local. 
    
    Will copy files that meet the following criteria:
        must be in the folder at `remote_dir`
        must have been modified in TIME_INTERVAL minutes since the last check

    Will return False if the remote_dir is a file, needs to be a directory
    or if there was an error opening a connection    
    
    filename is not prepended with '_', which indicates a draft file to ignore.
    (mynt)

    Returns the number of files transferred
    """
    
    num_files_copied = 0
    
    try:
        resp = db_client.metadata(remote_dir, list=True)
    except rest.ErrorResponse, e:
        print "There was an error: %s" % e
        return False

    if not resp['is_dir']:
        if debug:
            print "Remote path must be a directory, %s is a file" % (remote_dir,)
        return False
    else:
        for f in resp['contents']:
            file_name = f['path'][ f["path"].rindex(dir_sep)+1 : ]
            # local path should be the _posts path on the 
            # server where you will run mynt
            local_file = local_dir + dir_sep + file_name
            
            if f['is_dir']:
                continue # skip it, only get the top level files
            elif not changed_since_last(f) and os.path.exists(local_file):
                if debug:
                    print "file hasn't changed, skipping"
                    print ""
                continue
            else:
                ## ignore file prepended with _ as they will 
                # be by mynt, saves a little time/bandwidth
                if file_name[0] == '_':
                    continue
                
                if debug:
                    print "Copying file to: ", local_file
                    print ""
                
                contents = db_client.get_file(f['path']).read()
                file(local_file, "w").write(contents)
                
                num_files_copied += 1 # track for return value

    return num_files_copied

if len(sys.argv) != 3:
    print "Usage: python mynt-box.py <dropbox path> <local path>"
else:
    remote_dir, local_dir = sys.argv[1], sys.argv[2]
    files_transferred = get_files(remote_dir, local_dir)
    
    if files_transferred:
        if debug:
            print 'happy happy %d files trasnferred' % (files_transferred,)
            
        # generate the static files into your html public directory
        subprocess.call(['mynt', 'gen', '-f', '/path/to/your/blog/directory', '/path/to/public/html/directory/'])
